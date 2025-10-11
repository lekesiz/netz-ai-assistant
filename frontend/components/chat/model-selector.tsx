'use client'

import { useState, useEffect } from 'react'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Zap, Brain, Code, Sparkles } from 'lucide-react'

interface Model {
  type: string
  name: string
  model_id: string
  size_gb: number
  turkish_support: string
  coding_ability: string
  speed: number
  use_cases: string[]
}

export function ModelSelector() {
  const [models, setModels] = useState<Model[]>([])
  const [selectedModel, setSelectedModel] = useState<string>('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchModels()
  }, [])

  const fetchModels = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/models/available')
      const data = await response.json()
      if (data.status === 'success') {
        setModels(data.models)
        setSelectedModel(data.current_model)
      }
    } catch (error) {
      console.error('Failed to fetch models:', error)
    } finally {
      setLoading(false)
    }
  }

  const getModelIcon = (type: string) => {
    switch (type) {
      case 'fast':
        return <Zap className="w-4 h-4" />
      case 'accurate':
        return <Brain className="w-4 h-4" />
      case 'coding':
        return <Code className="w-4 h-4" />
      default:
        return <Sparkles className="w-4 h-4" />
    }
  }

  const getModelBadge = (model: Model) => {
    if (model.speed > 150) {
      return <Badge variant="secondary" className="ml-2">Hızlı</Badge>
    }
    if (parseFloat(model.coding_ability) >= 90) {
      return <Badge variant="secondary" className="ml-2">Kod</Badge>
    }
    if (model.size_gb >= 32) {
      return <Badge variant="secondary" className="ml-2">Güçlü</Badge>
    }
    return null
  }

  if (loading) {
    return (
      <div className="w-[200px] h-10 bg-muted animate-pulse rounded" />
    )
  }

  return (
    <Select value={selectedModel} onValueChange={setSelectedModel}>
      <SelectTrigger className="w-[250px]">
        <SelectValue placeholder="Model seçin" />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectLabel>AI Modelleri</SelectLabel>
          {models.map((model) => (
            <SelectItem key={model.model_id} value={model.type}>
              <div className="flex items-center">
                {getModelIcon(model.type)}
                <span className="ml-2">{model.name}</span>
                {getModelBadge(model)}
              </div>
            </SelectItem>
          ))}
        </SelectGroup>
      </SelectContent>
    </Select>
  )
}