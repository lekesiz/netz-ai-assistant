#!/bin/sh

# Generate dhparam if it doesn't exist
if [ ! -f /etc/nginx/dhparam.pem ]; then
    echo "Generating DH parameters (this may take a while)..."
    openssl dhparam -out /etc/nginx/dhparam.pem 2048
fi

# Create cache directory
mkdir -p /var/cache/nginx
chown -R nginx:nginx /var/cache/nginx

# Test nginx configuration
nginx -t

# Start nginx in background
nginx -g "daemon off;" &

# Store nginx PID
NGINX_PID=$!

# Function to handle shutdown
shutdown() {
    echo "Shutting down nginx..."
    kill -QUIT $NGINX_PID
    wait $NGINX_PID
}

# Trap signals
trap shutdown TERM INT QUIT

# Wait for nginx
wait $NGINX_PID