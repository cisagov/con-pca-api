FROM python:3.9.6

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && \
    apt-get install -y python3-pip python-dev

RUN apt-get install -y nodejs npm chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true

WORKDIR /var/www/

COPY ./new/package*.json ./
RUN npm install

ADD ./new/requirements.txt /var/www/requirements.txt
RUN pip install --upgrade pip \
    pip install -r requirements.txt

ADD ./new/ /var/www/

ENV PYTHONPATH "${PYTHONPATH}:/var/www"

# Install GeoIPUpdate
WORKDIR /tmp
RUN wget https://github.com/maxmind/geoipupdate/releases/download/v4.6.0/geoipupdate_4.6.0_linux_amd64.tar.gz
RUN tar -xzf geoipupdate_4.6.0_linux_amd64.tar.gz
RUN cp geoipupdate_4.6.0_linux_amd64/geoipupdate /usr/local/bin
COPY etc/new-GeoIP.conf /usr/local/etc/GeoIP.conf

# Entrypoint
COPY ./etc/new-entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod a+x /usr/local/bin/entrypoint.sh

EXPOSE 5000
EXPOSE 80
EXPOSE 443

WORKDIR /var/www

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
