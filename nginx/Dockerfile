FROM nginx:latest

RUN mkdir -p /app/staticfiles

COPY nginx.conf /etc/nginx/nginx.conf

COPY html/ /usr/share/nginx/html/

EXPOSE 80