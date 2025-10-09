#!/bin/bash
#
# NETZ AI Backup Script
# Performs daily backups of all critical data
#

set -euo pipefail

# Load environment variables
if [ -f /etc/netz-ai/.env ]; then
    source /etc/netz-ai/.env
fi

# Configuration
BACKUP_DIR="/backup/netz-ai"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TODAY=$(date +%Y-%m-%d)
BACKUP_PREFIX="netz-backup-${TIMESTAMP}"
LOG_FILE="/var/log/netz-ai/backup.log"
RETENTION_DAYS=30

# Directories to backup
DATA_DIRS=(
    "/opt/netz-ai/models"
    "/var/lib/netz-ai/uploads"
    "/var/lib/netz-ai/processed"
    "/etc/netz-ai"
)

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handling
handle_error() {
    log "ERROR: Backup failed at line $1"
    send_notification "Backup Failed" "NETZ AI backup failed. Please check logs."
    exit 1
}

trap 'handle_error $LINENO' ERR

# Send email notification
send_notification() {
    local subject="$1"
    local body="$2"
    
    if command -v mail &> /dev/null && [ ! -z "$NOTIFICATION_EMAIL" ]; then
        echo "$body" | mail -s "[NETZ AI] $subject" "$NOTIFICATION_EMAIL"
    fi
}

# Create backup directory
create_backup_dir() {
    local backup_path="$BACKUP_DIR/daily/$TODAY"
    mkdir -p "$backup_path"
    echo "$backup_path"
}

# Backup PostgreSQL
backup_postgresql() {
    log "Starting PostgreSQL backup..."
    
    local backup_path="$1"
    local pg_backup_file="$backup_path/${BACKUP_PREFIX}-postgresql.sql.gz"
    
    PGPASSWORD="$POSTGRES_PASSWORD" pg_dumpall \
        -h "$POSTGRES_HOST" \
        -U "$POSTGRES_USER" \
        --clean \
        --verbose | gzip > "$pg_backup_file"
    
    log "PostgreSQL backup completed: $pg_backup_file"
}

# Backup Redis
backup_redis() {
    log "Starting Redis backup..."
    
    local backup_path="$1"
    local redis_backup_file="$backup_path/${BACKUP_PREFIX}-redis.rdb"
    
    # Trigger Redis save
    redis-cli -h "$REDIS_HOST" -a "$REDIS_PASSWORD" BGSAVE
    
    # Wait for save to complete
    while [ $(redis-cli -h "$REDIS_HOST" -a "$REDIS_PASSWORD" LASTSAVE) -eq $(redis-cli -h "$REDIS_HOST" -a "$REDIS_PASSWORD" LASTSAVE) ]; do
        sleep 1
    done
    
    # Copy the dump file
    cp /var/lib/redis/dump.rdb "$redis_backup_file"
    
    log "Redis backup completed: $redis_backup_file"
}

# Backup Qdrant
backup_qdrant() {
    log "Starting Qdrant backup..."
    
    local backup_path="$1"
    local qdrant_backup_dir="$backup_path/${BACKUP_PREFIX}-qdrant"
    
    # Create snapshot via API
    curl -X POST "http://localhost:6333/collections/netz_knowledge/snapshots" \
        -H "Content-Type: application/json" \
        -d '{"wait": true}'
    
    # Copy Qdrant data
    mkdir -p "$qdrant_backup_dir"
    cp -r /var/lib/docker/volumes/netz-ai_qdrant_data/_data/* "$qdrant_backup_dir/"
    
    log "Qdrant backup completed: $qdrant_backup_dir"
}

# Backup file system
backup_filesystem() {
    log "Starting filesystem backup..."
    
    local backup_path="$1"
    local fs_backup_file="$backup_path/${BACKUP_PREFIX}-filesystem.tar.gz"
    
    # Create tar archive with exclusions
    tar -czf "$fs_backup_file" \
        --exclude='*.log' \
        --exclude='*.pyc' \
        --exclude='__pycache__' \
        --exclude='.git' \
        "${DATA_DIRS[@]}"
    
    log "Filesystem backup completed: $fs_backup_file"
}

# Encrypt backup
encrypt_backup() {
    local file="$1"
    
    if [ ! -z "$BACKUP_ENCRYPTION_KEY" ]; then
        log "Encrypting backup: $file"
        openssl enc -aes-256-cbc \
            -salt \
            -in "$file" \
            -out "${file}.enc" \
            -pass pass:"$BACKUP_ENCRYPTION_KEY"
        
        # Remove unencrypted file
        rm -f "$file"
        
        log "Encryption completed: ${file}.enc"
    fi
}

# Upload to S3 (optional)
upload_to_s3() {
    local backup_path="$1"
    
    if [ ! -z "$S3_BACKUP_BUCKET" ] && command -v aws &> /dev/null; then
        log "Uploading backup to S3..."
        
        aws s3 sync "$backup_path" "s3://$S3_BACKUP_BUCKET/daily/$TODAY/" \
            --storage-class GLACIER_IR \
            --exclude "*.log"
        
        log "S3 upload completed"
    fi
}

# Clean old backups
cleanup_old_backups() {
    log "Cleaning up old backups..."
    
    # Local cleanup
    find "$BACKUP_DIR/daily" -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null || true
    
    # S3 cleanup (if configured)
    if [ ! -z "$S3_BACKUP_BUCKET" ] && command -v aws &> /dev/null; then
        aws s3 ls "s3://$S3_BACKUP_BUCKET/daily/" | \
            awk '{print $2}' | \
            while read -r prefix; do
                backup_date=$(echo "$prefix" | sed 's/\///')
                if [[ $(date -d "$backup_date" +%s 2>/dev/null || echo 0) -lt $(date -d "$RETENTION_DAYS days ago" +%s) ]]; then
                    aws s3 rm "s3://$S3_BACKUP_BUCKET/daily/$prefix" --recursive
                fi
            done
    fi
    
    log "Cleanup completed"
}

# Verify backup
verify_backup() {
    local backup_path="$1"
    
    log "Verifying backup..."
    
    # Check if backup files exist and have size > 0
    local errors=0
    
    for file in "$backup_path"/*; do
        if [ -f "$file" ]; then
            size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null)
            if [ "$size" -eq 0 ]; then
                log "ERROR: Backup file is empty: $file"
                ((errors++))
            fi
        fi
    done
    
    if [ $errors -gt 0 ]; then
        log "ERROR: Backup verification failed with $errors errors"
        return 1
    fi
    
    log "Backup verification passed"
    return 0
}

# Generate backup report
generate_report() {
    local backup_path="$1"
    local report_file="$backup_path/backup-report.txt"
    
    {
        echo "NETZ AI Backup Report"
        echo "===================="
        echo "Date: $(date)"
        echo "Backup ID: $BACKUP_PREFIX"
        echo ""
        echo "Files:"
        ls -lah "$backup_path"
        echo ""
        echo "Disk Usage:"
        du -sh "$backup_path"
        echo ""
        echo "System Status:"
        df -h | grep -E '^/dev/'
        echo ""
        echo "Service Status:"
        systemctl status netz-* --no-pager || true
    } > "$report_file"
    
    log "Backup report generated: $report_file"
}

# Main backup process
main() {
    log "=== Starting NETZ AI Backup ==="
    
    # Create backup directory
    BACKUP_PATH=$(create_backup_dir)
    log "Backup directory: $BACKUP_PATH"
    
    # Perform backups
    backup_postgresql "$BACKUP_PATH"
    backup_redis "$BACKUP_PATH"
    backup_qdrant "$BACKUP_PATH"
    backup_filesystem "$BACKUP_PATH"
    
    # Encrypt all backup files
    for file in "$BACKUP_PATH"/*; do
        if [[ -f "$file" && ! "$file" =~ \.enc$ ]]; then
            encrypt_backup "$file"
        fi
    done
    
    # Verify backup
    if verify_backup "$BACKUP_PATH"; then
        # Upload to S3 if configured
        upload_to_s3 "$BACKUP_PATH"
        
        # Generate report
        generate_report "$BACKUP_PATH"
        
        # Send success notification
        send_notification "Backup Successful" "NETZ AI backup completed successfully at $TIMESTAMP"
        
        # Cleanup old backups
        cleanup_old_backups
        
        log "=== Backup completed successfully ==="
    else
        handle_error "Backup verification"
    fi
    
    # Create weekly and monthly copies
    if [ "$(date +%u)" -eq 7 ]; then
        # Sunday - create weekly backup
        cp -r "$BACKUP_PATH" "$BACKUP_DIR/weekly/week-$(date +%U)"
        log "Weekly backup created"
    fi
    
    if [ "$(date +%d)" -eq 1 ]; then
        # First day of month - create monthly backup
        cp -r "$BACKUP_PATH" "$BACKUP_DIR/monthly/$(date +%Y-%m)"
        log "Monthly backup created"
    fi
}

# Run main function
main "$@"