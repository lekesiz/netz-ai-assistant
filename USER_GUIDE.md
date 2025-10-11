# NETZ AI Assistant - User Guide 📚

## 🚀 Starting the Application

### One-Click Launch
```bash
cd /Users/mikail/Desktop/NETZ-AI-Project
./launch.sh
```

This will:
1. Start all required services (PostgreSQL, Redis, Qdrant, Ollama)
2. Launch the backend API
3. Start the frontend
4. Open your browser to http://localhost:3000

## 💬 Using the Chat Interface

### Main Features
- **French Language Optimized**: The AI speaks fluent French
- **Conversation History**: All chats are automatically saved
- **Dark/Light Mode**: Click the theme toggle in the top right
- **Multiple Conversations**: Create new chats or switch between existing ones

### How to Chat
1. Type your message in French or English
2. Press Enter or click Send
3. The AI will respond with context from your company data
4. Sources are shown when available

### Example Questions (in French)
- "Quels sont nos services informatiques?"
- "Comment configurer un poste de travail?"
- "Quelle est notre politique de sécurité?"
- "Montrez-moi les dernières factures"
- "Quel est le chiffre d'affaires du mois?"

## 📊 Data Sources

The AI has access to:
- **Google Drive Documents**: Company policies, procedures, technical docs
- **PennyLane Financial Data**: Invoices, customers, financial reports
- **Real-time Updates**: Data syncs automatically every night

## 🔧 Admin Functions

### Sync Data Manually

**Update Google Drive Documents:**
```bash
curl -X POST http://localhost:8000/api/data/update/google_drive
```

**Update PennyLane Data:**
```bash
curl -X POST http://localhost:8000/api/data/update/pennylane
```

**Check Sync Status:**
```bash
curl http://localhost:8000/api/data/status
```

### View API Documentation
Open http://localhost:8000/docs in your browser

## 🛠️ Troubleshooting

### Chat Not Responding?
1. Check if backend is running: `curl http://localhost:8000/health`
2. Restart services: `./launch.sh`

### Can't Access Frontend?
1. Check if port 3000 is free
2. Look at logs: `tail -f logs/frontend.log`

### Data Not Updating?
1. Check sync status
2. Manually trigger sync (see Admin Functions)
3. Check logs: `tail -f logs/backend.log`

## 🛑 Stopping the Application

```bash
./scripts/stop-all.sh
```

## 📱 Keyboard Shortcuts

- `Ctrl/Cmd + K`: New conversation
- `Ctrl/Cmd + /`: Focus chat input
- `Ctrl/Cmd + D`: Toggle dark mode

## 🔐 Security Notes

- All data stays on your local machine
- No external API calls except PennyLane
- Conversations are stored locally
- Regular backups recommended

## 📞 Support

For technical issues:
- Check logs in `/logs` directory
- Run diagnostics: `python test_system.py`
- Contact: mikail@netzinformatique.fr

---

**Enjoy your AI-powered assistant!** 🎉