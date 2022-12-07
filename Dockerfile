FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && \
    apt-get install -y python3-pip python-dev

RUN apt-get install -y nodejs npm chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true

WORKDIR /var/www/

COPY ./src/package*.json ./
RUN npm install

ADD ./requirements.txt /var/www/requirements.txt
RUN pip install --upgrade pip \
    pip install -r requirements.txt
###
# For a list of pre-defined annotation keys and value types see:
# https://github.com/opencontainers/image-spec/blob/master/annotations.md
#
# Note: Additional labels are added by the build workflow.
###
# github@cisa.dhs.gov is a very generic email distribution, and it is
# unlikely that anyone on that distribution is familiar with the
# particulars of your repository.  It is therefore *strongly*
# suggested that you use an email address here that is specific to the
# person or group that maintains this repository; for example:
# LABEL org.opencontainers.image.authors="vm-fusion-dev-group@trio.dhs.gov"
LABEL org.opencontainers.image.authors="mostafa.abdelbaky@inl.gov"
LABEL org.opencontainers.image.vendor="Idaho National Laboratory"

###
# Unprivileged user setup variables
###
ARG CISA_UID=421
ARG CISA_GID=${CISA_UID}
ARG CISA_USER="cisa"
ENV CISA_GROUP=${CISA_USER}
ENV CISA_HOME="/home/${CISA_USER}"

###
# Upgrade the system
#
# Note that we use apk --no-cache to avoid writing to a local cache.
# This results in a smaller final image, at the cost of slightly
# longer install times.
###
RUN apk --update --no-cache --quiet upgrade

###
# Create unprivileged user
###
RUN addgroup --system --gid ${CISA_GID} ${CISA_GROUP} \
    && adduser --system --uid ${CISA_UID} --ingroup ${CISA_GROUP} ${CISA_USER}

###
# Dependencies
#
# Note that we use apk --no-cache to avoid writing to a local cache.
# This results in a smaller final image, at the cost of slightly
# longer install times.
###
ENV DEPS \
    ca-certificates \
    openssl \
    py-pip
RUN apk --no-cache --quiet add ${DEPS}

###
# Make sure pip and setuptools are the latest versions
#
# Note that we use pip --no-cache-dir to avoid writing to a local
# cache.  This results in a smaller final image, at the cost of
# slightly longer install times.
###
RUN pip install --no-cache-dir --upgrade pip setuptools

ADD ./src/ /var/www/

ENV PYTHONPATH "${PYTHONPATH}:/var/www"

# Install GeoIPUpdate
WORKDIR /tmp
RUN wget https://github.com/maxmind/geoipupdate/releases/download/v4.6.0/geoipupdate_4.6.0_linux_amd64.tar.gz
RUN tar -xzf geoipupdate_4.6.0_linux_amd64.tar.gz
RUN cp geoipupdate_4.6.0_linux_amd64/geoipupdate /usr/local/bin
COPY etc/GeoIP.conf /usr/local/etc/GeoIP.conf

RUN chmod a+x /var/www/msoffice-crypt.exe

# Entrypoint
COPY ./etc/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod a+x /usr/local/bin/entrypoint.sh

EXPOSE 5000
EXPOSE 80
EXPOSE 443

WORKDIR /var/www

###
# Install Python dependencies
#
# Note that we use pip --no-cache-dir to avoid writing to a local
# cache.  This results in a smaller final image, at the cost of
# slightly longer install times.
###
RUN wget --output-document sourcecode.tgz \
    https://github.com/cisagov/skeleton-python-library/archive/v${VERSION}.tar.gz \
    && tar --extract --gzip --file sourcecode.tgz --strip-components=1 \
    && pip install --no-cache-dir --requirement requirements.txt \
    && ln -snf /run/secrets/quote.txt src/example/data/secret.txt \
    && rm sourcecode.tgz

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
