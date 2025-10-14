FROM nginx:alpine

# Install certbot and required packages
RUN apk add --no-cache certbot python3 py3-pip openssl curl

# Install certbot nginx plugin
RUN pip3 install certbot-nginx

# Copy nginx configuration
COPY conf.d /etc/nginx/conf.d/
COPY snippets /etc/nginx/snippets/

# Copy custom nginx.conf if needed
COPY nginx.conf /etc/nginx/nginx.conf

# Create directories for certbot
RUN mkdir -p /var/www/certbot
RUN mkdir -p /var/log/nginx

# Make sure nginx user owns the directories
RUN chown -R nginx:nginx /var/www/certbot
RUN chown -R nginx:nginx /var/log/nginx

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80 443

ENTRYPOINT ["/entrypoint.sh"]