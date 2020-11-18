FROM python:3.9.0

# Nginx
RUN apt-get update
RUN apt-get install nginx -y

# Generate certs
RUN mkdir /certs
RUN openssl req -x509 -nodes -days 365 -subj "/C=CA/ST=ID/O=INL/CN=localhost" -newkey rsa:2048 -keyout /certs/server.key -out /certs/server.crt

# Set work directory
RUN mkdir /app/
WORKDIR /app

# Set environment variables
ENV DJANGO_SETTINGS_MODULE "config.settings"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Install dependencies
RUN pip install --upgrade pip
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt --use-feature=2020-resolver --no-deps

# Copy project
ADD ./src /app

# Copy nginx conf
COPY etc/nginx.conf /etc/nginx/conf.d/
RUN rm -rf /etc/nginx/sites-enabled/

# Entrypoint
COPY ./etc/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod a+x /usr/local/bin/entrypoint.sh

EXPOSE 8000
EXPOSE 80
EXPOSE 443

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
