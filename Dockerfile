FROM python:3.9.1

# Nginx
RUN apt-get update
RUN apt-get install nginx -y

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
RUN pip install -r requirements.txt --no-deps

# Copy project
ADD ./src /app

# Copy nginx conf
COPY etc/nginx.conf /etc/nginx/conf.d/
RUN rm -rf /etc/nginx/sites-enabled/

# Install GeoIPUpdate
WORKDIR /tmp
RUN wget https://github.com/maxmind/geoipupdate/releases/download/v4.6.0/geoipupdate_4.6.0_linux_amd64.tar.gz
RUN tar -xzf geoipupdate_4.6.0_linux_amd64.tar.gz
RUN cp geoipupdate_4.6.0_linux_amd64/geoipupdate /usr/local/bin
COPY etc/GeoIP.conf /usr/local/etc/GeoIP.conf

# Entrypoint
COPY ./etc/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod a+x /usr/local/bin/entrypoint.sh

EXPOSE 8000
EXPOSE 80
EXPOSE 443

WORKDIR /app

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
