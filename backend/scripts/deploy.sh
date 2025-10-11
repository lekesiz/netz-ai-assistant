#!/bin/bash
# NETZ AI Production Deployment Script

set -e  # Exit on error

# Configuration
DEPLOY_ENV=${1:-production}
BACKUP_BEFORE_DEPLOY=${BACKUP_BEFORE_DEPLOY:-true}
HEALTH_CHECK_TIMEOUT=60
ROLLBACK_ON_FAILURE=${ROLLBACK_ON_FAILURE:-true}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check environment file
    if [ ! -f ".env" ]; then
        log_error ".env file not found"
        log_info "Creating from .env.example..."
        cp .env.example .env
        log_warning "Please update .env with production values"
        exit 1
    fi
    
    log_info "Prerequisites check passed"
}

backup_current_deployment() {
    if [ "$BACKUP_BEFORE_DEPLOY" = "true" ]; then
        log_info "Creating backup..."
        
        BACKUP_DIR="backups/deploy_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        # Backup database
        if docker ps | grep -q netz-postgres; then
            docker exec netz-postgres pg_dump -U netzai netzai > "$BACKUP_DIR/database.sql"
            log_info "Database backed up"
        fi
        
        # Backup data directories
        for dir in data logs; do
            if [ -d "$dir" ]; then
                cp -r "$dir" "$BACKUP_DIR/"
                log_info "$dir directory backed up"
            fi
        done
        
        # Save current image tags
        docker ps --format "table {{.Names}}\t{{.Image}}" > "$BACKUP_DIR/running_containers.txt"
        
        log_info "Backup completed: $BACKUP_DIR"
    fi
}

pull_latest_images() {
    log_info "Pulling latest images..."
    docker-compose pull
}

run_pre_deployment_tests() {
    log_info "Running pre-deployment tests..."
    
    # Run unit tests
    docker run --rm \
        -v $(pwd):/app \
        -w /app \
        python:3.11-slim \
        bash -c "pip install -r requirements.txt && pytest tests/unit -v"
    
    if [ $? -ne 0 ]; then
        log_error "Unit tests failed"
        exit 1
    fi
    
    log_info "Pre-deployment tests passed"
}

deploy_services() {
    log_info "Deploying services..."
    
    # Build and start services
    docker-compose build --no-cache
    docker-compose up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 10
    
    # Check health status
    local attempts=0
    local max_attempts=$((HEALTH_CHECK_TIMEOUT / 5))
    
    while [ $attempts -lt $max_attempts ]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            log_info "Health check passed"
            return 0
        fi
        
        attempts=$((attempts + 1))
        log_warning "Health check attempt $attempts/$max_attempts failed, retrying..."
        sleep 5
    done
    
    log_error "Health check failed after $HEALTH_CHECK_TIMEOUT seconds"
    return 1
}

run_post_deployment_tests() {
    log_info "Running post-deployment tests..."
    
    # Test API endpoints
    endpoints=(
        "http://localhost:8000/health"
        "http://localhost:8000/ready"
        "http://localhost:8000/api/chat"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if ! curl -f "$endpoint" > /dev/null 2>&1; then
            log_error "Endpoint test failed: $endpoint"
            return 1
        fi
    done
    
    log_info "Post-deployment tests passed"
}

setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Ensure Prometheus can scrape metrics
    if docker ps | grep -q netz-prometheus; then
        docker exec netz-prometheus wget -O- http://netz-api:9090/metrics > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            log_info "Prometheus metrics endpoint verified"
        else
            log_warning "Prometheus metrics endpoint not accessible"
        fi
    fi
}

rollback_deployment() {
    log_error "Deployment failed, rolling back..."
    
    # Stop current containers
    docker-compose down
    
    # Restore from backup if available
    if [ -d "$BACKUP_DIR" ]; then
        if [ -f "$BACKUP_DIR/database.sql" ]; then
            # Start only database
            docker-compose up -d postgres
            sleep 10
            docker exec -i netz-postgres psql -U netzai netzai < "$BACKUP_DIR/database.sql"
        fi
        
        # Restore data directories
        for dir in data logs; do
            if [ -d "$BACKUP_DIR/$dir" ]; then
                rm -rf "$dir"
                cp -r "$BACKUP_DIR/$dir" .
            fi
        done
    fi
    
    log_error "Rollback completed. Previous deployment restored."
    exit 1
}

cleanup_old_images() {
    log_info "Cleaning up old images..."
    docker image prune -f
}

generate_deployment_report() {
    log_info "Generating deployment report..."
    
    REPORT_FILE="deployment_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "NETZ AI Deployment Report"
        echo "========================="
        echo "Date: $(date)"
        echo "Environment: $DEPLOY_ENV"
        echo ""
        echo "Running Containers:"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo ""
        echo "Image Details:"
        docker images | grep netz
        echo ""
        echo "System Resources:"
        docker stats --no-stream
        echo ""
        echo "Recent Logs:"
        docker-compose logs --tail=20
    } > "$REPORT_FILE"
    
    log_info "Deployment report saved: $REPORT_FILE"
}

# Main deployment process
main() {
    log_info "Starting NETZ AI deployment to $DEPLOY_ENV..."
    
    # Pre-deployment
    check_prerequisites
    backup_current_deployment
    pull_latest_images
    run_pre_deployment_tests
    
    # Deployment
    if deploy_services; then
        # Post-deployment
        if run_post_deployment_tests; then
            setup_monitoring
            cleanup_old_images
            generate_deployment_report
            log_info "Deployment completed successfully!"
        else
            if [ "$ROLLBACK_ON_FAILURE" = "true" ]; then
                rollback_deployment
            else
                log_error "Post-deployment tests failed"
                exit 1
            fi
        fi
    else
        if [ "$ROLLBACK_ON_FAILURE" = "true" ]; then
            rollback_deployment
        else
            log_error "Deployment failed"
            exit 1
        fi
    fi
}

# Run main function
main "$@"