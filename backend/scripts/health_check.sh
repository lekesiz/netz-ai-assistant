#!/bin/bash
# NETZ AI Health Check Script

# Configuration
API_URL=${API_URL:-http://localhost:8000}
SLACK_WEBHOOK=${SLACK_WEBHOOK:-""}
EMAIL_ALERTS=${EMAIL_ALERTS:-""}
CHECK_INTERVAL=${CHECK_INTERVAL:-60}
ALERT_THRESHOLD=${ALERT_THRESHOLD:-3}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# State tracking
FAILURE_COUNT=0
LAST_ALERT_TIME=0

# Functions
log_status() {
    local status=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $status in
        "OK")
            echo -e "${GREEN}[$timestamp] OK:${NC} $message"
            ;;
        "WARN")
            echo -e "${YELLOW}[$timestamp] WARN:${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}[$timestamp] ERROR:${NC} $message"
            ;;
    esac
}

send_alert() {
    local severity=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Log to file
    echo "[$timestamp] $severity: $message" >> /var/log/netz_ai_health.log
    
    # Send Slack notification
    if [ ! -z "$SLACK_WEBHOOK" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚨 NETZ AI Alert [$severity]: $message\"}" \
            "$SLACK_WEBHOOK" 2>/dev/null
    fi
    
    # Send email alert
    if [ ! -z "$EMAIL_ALERTS" ]; then
        echo "$message" | mail -s "NETZ AI Alert [$severity]" "$EMAIL_ALERTS" 2>/dev/null
    fi
}

check_api_health() {
    local response=$(curl -s -w "\n%{http_code}" "$API_URL/health" 2>/dev/null)
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        local status=$(echo "$body" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        if [ "$status" = "healthy" ]; then
            return 0
        else
            return 1
        fi
    else
        return 2
    fi
}

check_service_health() {
    local service=$1
    local port=$2
    
    if nc -z localhost "$port" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

check_disk_space() {
    local threshold=90
    local usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$usage" -gt "$threshold" ]; then
        return 1
    else
        return 0
    fi
}

check_memory_usage() {
    local threshold=90
    local usage=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
    
    if [ "$usage" -gt "$threshold" ]; then
        return 1
    else
        return 0
    fi
}

check_container_health() {
    local unhealthy_containers=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep -i unhealthy | wc -l)
    
    if [ "$unhealthy_containers" -gt 0 ]; then
        return 1
    else
        return 0
    fi
}

perform_health_checks() {
    local all_healthy=true
    local issues=()
    
    # Check API health
    if check_api_health; then
        log_status "OK" "API is healthy"
    else
        all_healthy=false
        issues+=("API health check failed")
        log_status "ERROR" "API health check failed"
    fi
    
    # Check required services
    services=(
        "PostgreSQL:5432"
        "Redis:6379"
        "Ollama:11434"
    )
    
    for service_info in "${services[@]}"; do
        IFS=':' read -r service port <<< "$service_info"
        if check_service_health "$service" "$port"; then
            log_status "OK" "$service is running on port $port"
        else
            all_healthy=false
            issues+=("$service is not accessible on port $port")
            log_status "ERROR" "$service is not accessible on port $port"
        fi
    done
    
    # Check system resources
    if check_disk_space; then
        log_status "OK" "Disk space is sufficient"
    else
        all_healthy=false
        issues+=("Disk space is running low")
        log_status "WARN" "Disk space is running low"
    fi
    
    if check_memory_usage; then
        log_status "OK" "Memory usage is normal"
    else
        all_healthy=false
        issues+=("Memory usage is high")
        log_status "WARN" "Memory usage is high"
    fi
    
    # Check Docker containers
    if check_container_health; then
        log_status "OK" "All containers are healthy"
    else
        all_healthy=false
        issues+=("Some containers are unhealthy")
        log_status "ERROR" "Some containers are unhealthy"
    fi
    
    # Handle failures
    if [ "$all_healthy" = false ]; then
        FAILURE_COUNT=$((FAILURE_COUNT + 1))
        
        if [ $FAILURE_COUNT -ge $ALERT_THRESHOLD ]; then
            local current_time=$(date +%s)
            local time_since_alert=$((current_time - LAST_ALERT_TIME))
            
            # Send alert only if 5 minutes have passed since last alert
            if [ $time_since_alert -gt 300 ]; then
                local issue_list=$(printf '%s\n' "${issues[@]}")
                send_alert "CRITICAL" "Multiple health check failures:\n$issue_list"
                LAST_ALERT_TIME=$current_time
            fi
        fi
    else
        # Reset failure count on success
        if [ $FAILURE_COUNT -gt 0 ]; then
            log_status "OK" "System recovered after $FAILURE_COUNT failures"
            send_alert "INFO" "System recovered and is now healthy"
        fi
        FAILURE_COUNT=0
    fi
}

generate_health_report() {
    local report_file="/var/log/netz_ai_health_report_$(date +%Y%m%d).txt"
    
    {
        echo "NETZ AI Daily Health Report - $(date)"
        echo "====================================="
        echo ""
        echo "Service Status:"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo ""
        echo "Resource Usage:"
        docker stats --no-stream
        echo ""
        echo "Disk Usage:"
        df -h
        echo ""
        echo "Memory Usage:"
        free -h
        echo ""
        echo "Recent Errors:"
        grep ERROR /var/log/netz_ai_health.log | tail -20
    } > "$report_file"
    
    # Send daily report if email is configured
    if [ ! -z "$EMAIL_ALERTS" ]; then
        cat "$report_file" | mail -s "NETZ AI Daily Health Report" "$EMAIL_ALERTS"
    fi
}

# Main monitoring loop
main() {
    log_status "OK" "Starting NETZ AI health monitoring..."
    
    # Create log directory if it doesn't exist
    mkdir -p /var/log
    
    # Run continuous monitoring
    while true; do
        perform_health_checks
        
        # Generate daily report at midnight
        if [ $(date +%H:%M) = "00:00" ]; then
            generate_health_report
        fi
        
        sleep $CHECK_INTERVAL
    done
}

# Handle script termination
trap 'log_status "OK" "Health monitoring stopped"; exit 0' INT TERM

# Check if running as one-time check or continuous monitoring
if [ "$1" = "once" ]; then
    perform_health_checks
else
    main
fi