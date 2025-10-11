'use client'

import { useState, useCallback } from 'react'
import { Upload, X, FileText, CheckCircle, AlertCircle, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'

const UPLOAD_API_URL = process.env.NEXT_PUBLIC_UPLOAD_API_URL || 'http://localhost:8002'

interface UploadedFile {
  filename: string
  upload_time: string
  file_type: string
  size: number
  hash: string
}

interface UploadResult {
  status: string
  message?: string
  metadata?: any
  content_preview?: string
  error?: string
  filename?: string
}

export function DocumentUpload() {
  const [isDragging, setIsDragging] = useState(false)
  const [uploadingFiles, setUploadingFiles] = useState<File[]>([])
  const [uploadResults, setUploadResults] = useState<UploadResult[]>([])
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [existingFiles, setExistingFiles] = useState<UploadedFile[]>([])
  const [showExisting, setShowExisting] = useState(false)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const files = Array.from(e.dataTransfer.files)
    handleFiles(files)
  }, [])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files)
      handleFiles(files)
    }
  }

  const handleFiles = (files: File[]) => {
    const validTypes = ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.txt', '.csv']
    const validFiles = files.filter(file => {
      const ext = '.' + file.name.split('.').pop()?.toLowerCase()
      return validTypes.includes(ext)
    })

    if (validFiles.length !== files.length) {
      alert('Sadece PDF, Word, Excel, TXT ve CSV dosyaları yüklenebilir.')
    }

    setUploadingFiles(validFiles)
  }

  const uploadFiles = async () => {
    if (uploadingFiles.length === 0) return

    setIsUploading(true)
    setUploadProgress(0)
    setUploadResults([])

    const results: UploadResult[] = []
    
    for (let i = 0; i < uploadingFiles.length; i++) {
      const file = uploadingFiles[i]
      const formData = new FormData()
      formData.append('file', file)

      try {
        const response = await fetch(`${UPLOAD_API_URL}/api/upload/document`, {
          method: 'POST',
          body: formData
        })

        const result = await response.json()
        results.push(result)
      } catch (error) {
        results.push({
          status: 'error',
          filename: file.name,
          error: error instanceof Error ? error.message : 'Upload failed'
        })
      }

      setUploadProgress(((i + 1) / uploadingFiles.length) * 100)
    }

    setUploadResults(results)
    setIsUploading(false)
    setUploadingFiles([])
    
    // Refresh existing files list
    fetchExistingFiles()
  }

  const fetchExistingFiles = async () => {
    try {
      const response = await fetch(`${UPLOAD_API_URL}/api/documents/list`)
      const data = await response.json()
      setExistingFiles(data.documents || [])
    } catch (error) {
      console.error('Failed to fetch existing files:', error)
    }
  }

  const deleteFile = async (hash: string) => {
    if (!confirm('Bu belgeyi AI hafızasından silmek istediğinize emin misiniz?')) return

    try {
      const response = await fetch(`${UPLOAD_API_URL}/api/documents/${hash}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        fetchExistingFiles()
        alert('Belge başarıyla silindi.')
      }
    } catch (error) {
      alert('Belge silinirken hata oluştu.')
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  return (
    <Card className="max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>AI Hafızasına Belge Yükle</CardTitle>
        <CardDescription>
          PDF, Word, Excel, TXT veya CSV dosyalarını yükleyerek AI'nın bilgi bankasını güncelleyin
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            isDragging ? 'border-primary bg-primary/10' : 'border-gray-300'
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <p className="text-lg mb-2">
            Dosyaları buraya sürükleyin veya{' '}
            <label htmlFor="file-upload" className="text-primary cursor-pointer hover:underline">
              dosya seçin
            </label>
          </p>
          <input
            id="file-upload"
            type="file"
            multiple
            accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,.csv"
            className="hidden"
            onChange={handleFileSelect}
          />
          <p className="text-sm text-gray-500">
            PDF, DOCX, XLSX, TXT, CSV (Max 10MB)
          </p>
        </div>

        {uploadingFiles.length > 0 && (
          <div className="mt-6 space-y-2">
            <h3 className="font-medium mb-2">Yüklenecek Dosyalar:</h3>
            {uploadingFiles.map((file, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <div className="flex items-center">
                  <FileText className="h-5 w-5 mr-2 text-gray-500" />
                  <span className="text-sm">{file.name}</span>
                  <span className="text-sm text-gray-500 ml-2">
                    ({formatFileSize(file.size)})
                  </span>
                </div>
                <button
                  onClick={() => {
                    setUploadingFiles(files => files.filter((_, i) => i !== index))
                  }}
                  className="text-red-500 hover:text-red-700"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            ))}
            
            <Button
              onClick={uploadFiles}
              disabled={isUploading}
              className="w-full mt-4"
            >
              {isUploading ? 'Yükleniyor...' : 'Dosyaları Yükle'}
            </Button>
          </div>
        )}

        {isUploading && (
          <div className="mt-6">
            <Progress value={uploadProgress} className="w-full" />
            <p className="text-sm text-gray-500 mt-2 text-center">
              {Math.round(uploadProgress)}% tamamlandı
            </p>
          </div>
        )}

        {uploadResults.length > 0 && (
          <div className="mt-6 space-y-2">
            <h3 className="font-medium mb-2">Yükleme Sonuçları:</h3>
            {uploadResults.map((result, index) => (
              <Alert key={index} variant={result.status === 'success' ? 'default' : 'destructive'}>
                {result.status === 'success' ? (
                  <CheckCircle className="h-4 w-4" />
                ) : (
                  <AlertCircle className="h-4 w-4" />
                )}
                <AlertDescription>
                  <strong>{result.filename || result.metadata?.filename}:</strong>{' '}
                  {result.message || result.error}
                  {result.content_preview && (
                    <details className="mt-2">
                      <summary className="cursor-pointer text-sm text-primary">
                        İçerik önizlemesi
                      </summary>
                      <pre className="mt-2 p-2 bg-gray-50 rounded text-xs overflow-x-auto">
                        {result.content_preview}
                      </pre>
                    </details>
                  )}
                </AlertDescription>
              </Alert>
            ))}
          </div>
        )}

        <div className="mt-8 border-t pt-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-medium">AI Hafızasındaki Belgeler</h3>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setShowExisting(!showExisting)
                if (!showExisting && existingFiles.length === 0) {
                  fetchExistingFiles()
                }
              }}
            >
              {showExisting ? 'Gizle' : 'Göster'}
            </Button>
          </div>

          {showExisting && (
            <div className="space-y-2">
              {existingFiles.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-4">
                  Henüz yüklenmiş belge yok
                </p>
              ) : (
                existingFiles.map((file) => (
                  <div
                    key={file.hash}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center flex-1">
                      <FileText className="h-5 w-5 mr-3 text-gray-500" />
                      <div className="flex-1">
                        <p className="font-medium text-sm">{file.filename}</p>
                        <p className="text-xs text-gray-500">
                          {new Date(file.upload_time).toLocaleDateString('tr-TR')} •{' '}
                          {formatFileSize(file.size)}
                        </p>
                      </div>
                      <Badge variant="outline" className="ml-2">
                        {file.file_type}
                      </Badge>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteFile(file.hash)}
                      className="ml-2 text-red-500 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        <Alert className="mt-6">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <strong>Not:</strong> Yüklediğiniz belgeler AI tarafından analiz edilir ve bilgi bankasına eklenir. 
            Hassas bilgiler içeren belgeleri yüklemeden önce gözden geçirin.
          </AlertDescription>
        </Alert>
      </CardContent>
    </Card>
  )
}