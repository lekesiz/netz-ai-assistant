# NETZ AI Assistant - Enterprise Offline AI System

## 🚀 Overview
An intelligent offline AI assistant for NETZ Informatique, providing real-time business insights, financial data analysis, and document management capabilities with multilingual support (French, Turkish, English).

## 📋 Key Features
- ✅ **Multilingual Chat Interface** (French, Turkish, English)
- ✅ **Real-time Financial Data** from PennyLane integration
- ✅ **Document Upload & Processing** (PDF, Word, Excel, TXT, CSV)
- ✅ **Vector Search** with Qdrant database
- ✅ **RAG (Retrieval Augmented Generation)** for accurate responses
- ✅ **Offline-first Architecture** for data security
- ✅ **Web-based Interface** with modern UI

## 🏗️ Current Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  Next.js 14     │────▶│  Simple API     │────▶│    Ollama        │
│  Frontend       │     │  (Port 8001)   │     │    (Mistral)     │
└─────────────────┘     └─────────────────┘     └──────────────────┘
                              │
┌─────────────────┐           │                  ┌──────────────────┐
│  Document       │────▶│  Upload API     │────▶│  Knowledge Base  │
│  Management     │     │  (Port 8002)   │     │  (JSON Storage)  │
└─────────────────┘     └─────────────────┘     └──────────────────┘

Additional Services:
├── Qdrant Vector DB (Port 6333)
├── PostgreSQL Database (Port 5432)
└── Redis Cache (Port 6379)
```

## 📦 Project Structure

```
NETZ-AI-Project/
├── backend/
│   ├── simple_api.py          # Main chat API (Port 8001)
│   ├── document_upload_api.py # Document upload service (Port 8002)
│   ├── main.py               # Full RAG implementation
│   ├── rag_service.py        # RAG service
│   ├── load_complete_data.py # Data loading script
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── app/
│   │   ├── page.tsx          # Home page
│   │   ├── chat/page.tsx     # Chat interface
│   │   └── documents/page.tsx # Document upload
│   ├── components/
│   │   ├── DocumentUpload.tsx # Upload component
│   │   └── chat/             # Chat components
│   └── package.json          # Node dependencies
├── docker-compose.yml        # Docker services
├── .env.example             # Environment template
└── README.md                # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- 8GB+ RAM (16GB recommended)
- macOS/Linux/Windows with WSL2

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/lekesiz/netz-ai-assistant.git
cd netz-ai-assistant
```

2. **Install backend dependencies**
```bash
cd backend
pip install -r requirements.txt
```

3. **Install frontend dependencies**
```bash
cd ../frontend
npm install
```

4. **Start Docker services**
```bash
cd ..
docker-compose up -d
```

5. **Install Ollama and Mistral model**
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Mistral model
ollama pull mistral
```

### Running the Application

1. **Start backend services**
```bash
cd backend
# Main chat API
python simple_api.py &

# Document upload API  
python document_upload_api.py &
```

2. **Start frontend**
```bash
cd ../frontend
npm run dev
```

3. **Access the application**
- Main Interface: http://localhost:3000 (or 3001)
- Chat: http://localhost:3000/chat
- Document Upload: http://localhost:3000/documents

## 📋 Usage Guide

### Chat Interface
- Ask questions in French, Turkish, or English
- Get real-time business insights
- Financial data queries
- Training program information

### Document Upload
1. Navigate to Documents page
2. Drag & drop or select files
3. Supported formats: PDF, Word, Excel, TXT, CSV
4. Documents are automatically processed and added to AI knowledge base

### Example Queries
- "Quel est le chiffre d'affaires d'octobre 2025?"
- "Quelle formation rapporte le plus?"
- "Ekim ayı ciromuz nedir?"
- "How many active clients do we have?"

## 📊 Current Company Data (2025)

### Financial Overview
- **January-October Revenue**: €119,386.85
- **October Revenue**: €41,558.85 (highest month)
- **Annual Projection**: €143,264.22
- **Active Clients**: 2,734

### Top Training Programs by Revenue
1. **Excel**: €35,815.85 (30%)
2. **Skills Assessment**: €28,500 (23.9%)
3. **Python**: €19,000 (15.9%)
4. **AutoCAD**: €13,058.85 (10.9%)
5. **WordPress**: €11,264 (9.4%)

## 🔧 Configuration

### Environment Variables

**backend/.env**
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/netz_ai
REDIS_URL=redis://localhost:6379
QDRANT_URL=http://localhost:6333
PENNYLANE_API_KEY=your_pennylane_key
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
```

**frontend/.env.local**
```env
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_UPLOAD_API_URL=http://localhost:8002
```

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**
   - Frontend may use port 3001 if 3000 is busy
   - Update `.env.local` accordingly

2. **AI responds in wrong language**
   - Specify language in query: "Réponds en turc: ..."
   - Model defaults to French

3. **Document upload fails**
   - Check file size (<10MB)
   - Ensure upload API is running on port 8002

4. **Slow responses**
   - Check if Ollama is running: `ollama list`
   - Ensure adequate RAM available

## 🚀 Upcoming Features

- [ ] Google Drive automatic sync
- [ ] Gmail integration
- [ ] Real-time PennyLane webhooks
- [ ] Voice chat interface
- [ ] Mobile app
- [ ] Advanced analytics dashboard

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is proprietary software for NETZ Informatique.

## 📞 Support

- **Email**: mikail@netzinformatique.fr
- **Company**: NETZ INFORMATIQUE
- **SIRET**: 818 347 346 00020
- **Address**: 1A Route de Schweighouse, 67500 HAGUENAU, France
- **Phone**: +33 3 67 31 02 01
- **Website**: [netzinformatique.fr](https://netzinformatique.fr)

---

**NETZ INFORMATIQUE** - Excellence in IT Training & Consulting Since 2015

*Last updated: January 9, 2025*