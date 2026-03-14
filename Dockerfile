FROM nginx:alpine

# Copy dashboard files
COPY index.html /usr/share/nginx/html/index.html
COPY dashboard.html /usr/share/nginx/html/dashboard.html

# Serve on port 8555
RUN sed -i 's/listen\s*80;/listen 8555;/' /etc/nginx/conf.d/default.conf

EXPOSE 8555

CMD ["nginx", "-g", "daemon off;"]
