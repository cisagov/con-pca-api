FROM python:3.8

# Nginx
RUN apt-get update
RUN apt-get install nginx -y
RUN apt-get install cron -y

# Generate certs
RUN mkdir /certs
RUN openssl req -x509 -nodes -days 365 -subj "/C=CA/ST=ID/O=INL/CN=localhost" -newkey rsa:2048 -keyout /certs/server.key -out /certs/server.crt

# Set work directory
RUN mkdir /app/
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN pip install --upgrade pip
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Copy project
ADD ./src /app

# Copy nginx conf
COPY etc/nginx.conf /etc/nginx/conf.d/
RUN rm -rf /etc/nginx/sites-enabled/

# Get combined ca bundle for rds/docdb
RUN  wget https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem

# Entrypoint
COPY ./etc/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod a+x /usr/local/bin/entrypoint.sh

EXPOSE 8000
EXPOSE 80
EXPOSE 443

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
