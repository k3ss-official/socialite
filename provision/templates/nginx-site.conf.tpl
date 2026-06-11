# Rendered by deploy_site.sh — do not edit on the server; redeploy instead.
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN};

    root ${ROOT};
    index index.html;

    # static landing page: cache hard, compress, lock down
    gzip on;
    gzip_types text/css application/javascript image/svg+xml;

    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options SAMEORIGIN;
    add_header Referrer-Policy strict-origin-when-cross-origin;

    location ~* \.(css|js|webp|jpg|jpeg|png|svg|woff2?)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        try_files $uri $uri/ =404;
    }
}
