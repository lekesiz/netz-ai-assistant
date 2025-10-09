# NETZ AI Assistant - Enterprise Offline AI System

## 🚀 Overview
A fully offline, enterprise-grade AI assistant designed for NETZ Informatique, featuring company-specific knowledge and secure multi-user access.

## 📋 Key Features
- ✅ Completely offline operation (air-gapped deployment)
- ✅ French-optimized AI models
- ✅ Google Workspace integration (Drive, Gmail, Calendar)
- ✅ Secure multi-user access control
- ✅ Automatic data updates and model training
- ✅ Enterprise-grade security and monitoring

## 🏗️ System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Client    │────▶│  Kong Gateway   │────▶│   FastAPI       │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                          │
                        ┌─────────────────────────────────┴────────┐
                        │                                          │
                  ┌─────┴─────┐  ┌──────────────┐  ┌─────────────┴───┐
                  │   vLLM    │  │    Qdrant    │  │   PostgreSQL    │
                  │  Server   │  │  Vector DB   │  │    Database     │
                  └───────────┘  └──────────────┘  └─────────────────┘
```

## 📦 Project Structure

```
NETZ-AI-Project/
├── documents/          # Detailed documentation
│   ├── 01-Donanim-Gereksinimleri.md
│   ├── 02-Yazilim-Stack-Teknoloji-Secimi.md
│   ├── 03-LLM-Model-Secimi-Kurulum.md
│   ├── 04-Veri-Toplama-Egitim-Plani.md
│   └── 05-Guvenlik-Erisim-Kontrolu.md
├── scripts/           # Installation and management scripts
│   ├── install.sh     # Main installation script
│   └── backup.sh      # Backup automation
├── configs/           # Configuration files
│   ├── docker-compose.yml
│   └── .env.template
├── services/          # Systemd service files
│   ├── netz-llm.service
│   └── netz-api.service
├── data/             # Data directories (empty)
├── models/           # Model directories (empty)
└── training/         # Training scripts (coming soon)
```

## 🚀 Quick Start

### 1. System Requirements
- Ubuntu Server 22.04 LTS
- Minimum 64GB RAM
- NVIDIA GPU (RTX 4070 Ti or higher)
- 2TB+ storage space

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/lekesiz/netz-ai-assistant.git
cd netz-ai-assistant

# Run the installation script
sudo bash scripts/install.sh
```

### 3. Configuration

```bash
# Create environment file
cp configs/.env.template /etc/netz-ai/.env

# Edit configuration
sudo nano /etc/netz-ai/.env
```

### 4. Start Services

```bash
# Start all services
sudo systemctl start netz-llm
sudo systemctl start netz-api
sudo systemctl start netz-worker

# Check status
sudo systemctl status netz-*
```

## 🔐 Initial Access

1. Navigate to: `https://netz-ai.local`
2. Login with admin credentials
3. Change default passwords
4. Configure users and roles

## 📊 Monitoring

- Grafana: `http://localhost:3001` (admin/CHANGE_ME)
- Prometheus: `http://localhost:9090`
- Keycloak: `http://localhost:8080` (admin/CHANGE_ME)

## 🔧 Management Commands

```bash
# Create backup
sudo /opt/netz-ai/scripts/backup.sh

# View logs
sudo journalctl -u netz-api -f

# Update model
sudo -u netz-ai /opt/netz-ai/scripts/update-model.sh

# System health check
sudo /opt/netz-ai/scripts/health-check.sh
```

## 📚 Detailed Documentation

Comprehensive documentation for each topic is available in the `documents/` folder:

1. **Hardware Requirements**: Minimum, recommended, and enterprise configurations
2. **Software Stack**: Technologies and architecture details
3. **Model Selection**: LLM models and installation guide
4. **Data Collection**: Google Workspace integration and training process
5. **Security**: Access control, encryption, and security policies

## 🛡️ Security Notes

- Change all default passwords immediately
- Review and configure firewall rules
- Update SSL certificates for production
- Implement regular backup schedule
- Monitor audit logs continuously

## 🆘 Troubleshooting

### GPU Not Detected
```bash
nvidia-smi
# CUDA driver installation may be required
```

### Model Loading Error
```bash
# Check model files
ls -la /opt/netz-ai/models/
```

### API Connection Issues
```bash
# Check service status
sudo systemctl status netz-api
# Review logs
sudo journalctl -u netz-api -n 100
```

## 👤 Author

**Mikail Lekesiz**  
NETZ Informatique

## 📧 Contact

**NETZ Informatique**  
- Email: contact@netzinformatique.fr  
- Phone: +33 3 67 31 02 01  
- Website: [netzinformatique.fr](https://netzinformatique.fr)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔒 Confidentiality

This project contains proprietary information of NETZ Informatique. Please handle with appropriate confidentiality.

---
*Created by Mikail Lekesiz*  
*Last updated: 2025-01-09*