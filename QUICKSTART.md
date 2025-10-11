# NETZ AI Assistant - Quick Start Guide 🚀

## System is Running! ✅

Your NETZ AI Assistant is now fully operational. Here's how to access it:

### 🌐 Web Interface
Open your browser and go to: **http://localhost:3000**

### 💬 Start Chatting
1. The interface is optimized for French language
2. Ask questions about your company, IT support, or general queries
3. Conversations are automatically saved

### 🔧 Quick Commands

**Check System Status:**
```bash
cd /Users/mikail/Desktop/NETZ-AI-Project
source venv_mac/bin/activate
python test_system.py
```

**View Logs:**
```bash
# Backend logs
tail -f logs/backend.log

# Check all services
brew services list
docker ps
```

**Stop Everything:**
```bash
./scripts/stop-all.sh
```

**Restart Everything:**
```bash
./scripts/start-all.sh
```

### 📊 Current Configuration

- **Language**: French (Mistral model)
- **Frontend**: Next.js on port 3000
- **Backend**: FastAPI on port 8000
- **Vector DB**: Qdrant on port 6333
- **LLM**: Ollama with Mistral on port 11434

### 🔄 Next Steps

1. **Add Your Data**:
   ```bash
   # Sync Google Drive documents
   curl -X POST http://localhost:8000/api/data/update/google_drive
   
   # Import PennyLane data (add API key first)
   curl -X POST http://localhost:8000/api/data/update/pennylane
   ```

2. **Configure PennyLane**:
   - Edit `backend/.env`
   - Add: `PENNYLANE_API_KEY=your_key_here`

3. **Test the System**:
   - Chat in French about IT topics
   - Ask about NETZ Informatique services
   - Test conversation management

### 📱 Features Available Now

✅ French language chat interface
✅ Conversation history and management
✅ Dark/Light theme toggle
✅ Vector search capability
✅ Real-time streaming responses
✅ Source attribution for answers
✅ Auto-save conversations

### 🛠️ Troubleshooting

**Frontend not loading?**
```bash
cd frontend && npm run dev
```

**Backend errors?**
```bash
cd backend && python main.py
```

**Database issues?**
```bash
brew services restart postgresql@15
brew services restart redis
```

---

**Need Help?** 
- Check logs in `/logs` directory
- Run `python test_system.py` for diagnostics
- Review documentation in `/documents` folder

**System is ready for use!** 🎉