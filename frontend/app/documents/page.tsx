import { DocumentUpload } from '@/components/DocumentUpload'

export default function DocumentsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      <div className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold">NETZ AI Assistant - Gestion des Documents</h1>
        </div>
      </div>
      <main className="container mx-auto px-4 py-8">
        <DocumentUpload />
      </main>
    </div>
  )
}