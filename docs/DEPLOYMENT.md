# NETZ AI Production Deployment Guide

## Overview
This guide covers the complete deployment process for NETZ AI in a production environment.

## Prerequisites
- Docker and Docker Compose installed
- SSL certificates configured
- Domain name pointing to server
- Minimum 2GB RAM, 2 CPU cores
- At least 10GB free disk space

## Quick Start
```bash
# 1. Clone repository
git clone [repository-url]
cd NETZ-AI-Project

# 2. Configure environment
cp .env.production.example .env.production
# Edit .env.production with your settings

# 3. Deploy
chmod +x deploy.sh
./deploy.sh
```

## Configuration

### Environment Variables
Copy `.env.production.example` to `.env.production` and configure:

- `SECRET_KEY`: Strong secret key for application
- `JWT_SECRET`: JWT signing secret
- API keys for integrations (OpenAI, PennyLane, etc.)
- Database paths
- CORS origins

### SSL Configuration
Place your SSL certificates in `nginx/ssl/`:
- `cert.pem`: SSL certificate
- `key.pem`: Private key

### Domain Configuration
Update `nginx/nginx.conf` with your domain names.

## Deployment Process

### Standard Deployment
```bash
./deploy.sh
```

### Quick Deployment (Development)
```bash
./quick-deploy.sh
```

### Update Existing Deployment
```bash
./update.sh
```

### Rollback Deployment
```bash
./rollback.sh
```

## Monitoring

### Health Checks
- Application: `https://yourdomain.com/health`
- API Documentation: `https://yourdomain.com/docs`

### Logs
- Application logs: `/var/log/netz-ai/app.log`
- Nginx logs: Docker logs for nginx container
- Deployment logs: `/var/log/netz-ai-deploy.log`

### Metrics
Access admin dashboard for comprehensive metrics:
`https://yourdomain.com/admin/dashboard`

## Backup and Recovery

### Automatic Backups
- Backups created before each deployment
- Stored in `/opt/backups/netz-ai/`
- Automatic cleanup (keeps last 5 backups)

### Manual Backup
```bash
mkdir -p /opt/backups/netz-ai/manual/$(date +%Y%m%d_%H%M%S)
cp -r ./production_data /opt/backups/netz-ai/manual/$(date +%Y%m%d_%H%M%S)/
```

### Recovery
```bash
./rollback.sh  # Automated rollback to latest backup
```

## Troubleshooting

### Common Issues

1. **Health check fails**
   - Check container logs: `docker-compose logs netz-ai`
   - Verify environment variables
   - Check disk space and memory

2. **SSL certificate issues**
   - Verify certificate files in `nginx/ssl/`
   - Check certificate expiration
   - Validate certificate chain

3. **Database connection issues**
   - Check file permissions
   - Verify database paths exist
   - Check disk space

### Performance Optimization

1. **Scale workers**
   ```bash
   # In production_config.json
   "server": {
     "workers": 4  // Adjust based on CPU cores
   }
   ```

2. **Increase cache size**
   ```bash
   # In production_config.json
   "performance": {
     "cache_size": 2000  // Increase for more memory
   }
   ```

## Security

### Security Checklist
- [ ] SSL certificates installed and valid
- [ ] Strong secrets configured
- [ ] CORS origins properly set
- [ ] Rate limiting enabled
- [ ] Security headers configured
- [ ] Firewall rules in place

### Regular Maintenance
- Update SSL certificates before expiration
- Review and rotate API keys quarterly
- Monitor logs for security issues
- Apply security updates promptly

## Support
For technical support, contact: contact@netzinformatique.fr
