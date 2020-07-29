# Con-PCA API

## Setup

Required for install:

<!--Please add required software information here-->

- [Docker](https://docs.docker.com/install/ "Docker")
- [MongoDB](https://docs.mongodb.com/manual/installation/ "MongoDB")
- [Python3+](https://www.python.org/download/releases/3.0/ "Python3+")

## Additional Suggestions

Here are some additional software to use along with develpment.
These items are not required.

<!--Please add addational software information here-->

- [VS Code](https://code.visualstudio.com/ "VS Code")
- [MongoDB Compass](https://www.mongodb.com/products/compass "MongoDB Compass")

VS Code is an IDE that supports pluggins to help centalize development.

MongoDB Compass is a GUI for MongoDB. This will help in visually exploring your
data.

## Local Install and Deployment

<!--Please add steps for local deployment of software information here-->

Note: Currently this is forcused on running locally on a Mac using Python3.

### Git Clone Project

Make sure you have a github account and access to the correct repo.

To install project run

```shell
git clone git@github.com:cisagov/con-pca-api.git
cd con-pca-api/
```

Use `Makefile` to install and run services.

### Setup and Build

To create `.env` files for containers, use this command to generate them.
These files are used as configuration in deployment.

Create your .env file

- `cp etc/env.dist .env`
- **Note:** visit `localhost:3333/settings` to get your
API key. Save it into your `.env` file

Build containers

- `make build`

Run your web application locally

- `make up`

Run Django logs in the terminal

- `make logs`

Initialize GoPhish & generate random data into mongo

- `make init`

Stop containers

- `make stop`

Remove containers

- `make down`

Access Django shell

- `make shell`

Drop DB of all data

- `make db_drop_mongo`

Collect static files

- `make collectstatic`

Compile mjml files to html for emails

- `make build_emails`

Send sample reports emails

- `make send_emails`

### Creating and loading random data

Using the makefile command: `make dummy` you can create data in
the db and get an output file containing all the id's of the created data.
This will also create initial data for gophish.

Incase you want to clear out all data in the DB, use: `make db_drop_mongo`

WARNING: This will drop ALL DATA in the connected docker mongodb

### To access the Django API

Django base app located at [localhost:8000](http://localhost:8000)

## Api Usage

To run the containers, use:

- `make up`

Your output will look like:

```shell
-> % make up
docker-compose up -d
Creating network "pca_backend" with the default driver
Creating pca-mongodb  ... done
Creating pca-api      ... done
```

Dev Access

You can use these endpoints to debug and develop, suggested access:

- [drf-yasg - Yet another Swagger generator](https://drf-yasg.readthedocs.io/en/latest/)

- [curl](https://curl.haxx.se/docs/manpage.html)

- [PostMan](https://www.postman.com/)

### drf-yasg / Swagger

Here we are using genrated docs via swagger that also give us a
few ways of viewing them.

Once running, navigate to the
[Api Swagger UI](http://localhost:8000/api/v1/swagger/)
located at: `http://localhost:8000/api/v1/swagger/`

You can also see the redoc version of the api at, navigate to the
[Api redoc UI](http://localhost:8000/api/v1/redoc/)
located at: `http://localhost:8000/api/v1/redoc/`

To download the api docs as yaml or json, use the following enpoints:
[Api Swagger json](http://localhost:8000/api/v1/swagger.json)
[Api Swagger YAML](http://localhost:8000/api/v1/swagger.yaml)

Here you can see how the calls are defined. These objects are defined under `api.serializers.*`
When created, it is genrated from those files and is validated when sending.

## Database Dump and Restore

### Dump

To Dump latest DB run the make command. This creates a timestamped `.dump` and
overwrites `latest.dump` to `src/scripts/data/db_dumps/..`

- `make mongo_dump`

```shell
$ make mongo_dump
docker exec pca-mongodb sh -c 'mongodump --host mongodb --port 27017 -u <USER> -p <PASS> --authenticationDatabase admin -d pca_data_dev --archive' > src/scripts/data/db_dumps/2020-06-26--16-02-50.dump
2020-06-26T20:02:50.611+0000  writing pca_data_dev.template to archive on stdout
2020-06-26T20:02:50.611+0000  writing pca_data_dev.tag_definition to archive on stdout
2020-06-26T20:02:50.612+0000  writing pca_data_dev.subscription to archive on stdout
2020-06-26T20:02:50.612+0000  writing pca_data_dev.customer to archive on stdout
2020-06-26T20:02:50.623+0000  done dumping pca_data_dev.template (163 documents)
2020-06-26T20:02:50.623+0000  writing pca_data_dev.dhs_contact to archive on stdout
2020-06-26T20:02:50.626+0000  done dumping pca_data_dev.customer (2 documents)
2020-06-26T20:02:50.626+0000  writing pca_data_dev.target to archive on stdout
2020-06-26T20:02:50.638+0000  done dumping pca_data_dev.tag_definition (44 documents)
2020-06-26T20:02:50.639+0000  done dumping pca_data_dev.dhs_contact (2 documents)
2020-06-26T20:02:50.640+0000  done dumping pca_data_dev.subscription (4 documents)
2020-06-26T20:02:50.645+0000  done dumping pca_data_dev.target (1 document)
cp src/scripts/data/db_dumps/2020-06-26--16-02-50.dump src/scripts/data/db_dumps/latest.dump
```

### Restore

To load latest `latest.dump` file into the db use `make mongo_restore`

```shell
$ make mongo_restore
docker exec -i pca-mongodb sh -c 'mongorestore --host mongodb --port 27017 -u root -p rootpassword --authenticationDatabase admin -d pca_data_dev --archive' < src/scripts/data/db_dumps/db.dump
2020-06-26T19:51:02.108+0000  the --db and --collection args should only be used when restoring from a BSON file. Other uses are deprecated and will not exist in the future; use --nsInclude instead
2020-06-26T19:51:02.118+0000  preparing collections to restore from
2020-06-26T19:51:02.127+0000  reading metadata for pca_data_dev.template from archive on stdin
2020-06-26T19:51:02.127+0000  restoring pca_data_dev.template from archive on stdin
2020-06-26T19:51:02.133+0000  reading metadata for pca_data_dev.dhs_contact from archive on stdin
2020-06-26T19:51:02.133+0000  restoring pca_data_dev.dhs_contact from archive on stdin
2020-06-26T19:51:02.138+0000  reading metadata for pca_data_dev.subscription from archive on stdin
2020-06-26T19:51:02.138+0000  restoring pca_data_dev.subscription from archive on stdin
2020-06-26T19:51:02.141+0000  reading metadata for pca_data_dev.tag_definition from archive on stdin
2020-06-26T19:51:02.141+0000  restoring pca_data_dev.tag_definition from archive on stdin
2020-06-26T19:51:02.157+0000  error: multiple errors in bulk operation:
  - E11000 duplicate key error collection: pca_data_dev.dhs_contact index: _id_ dup key: { : ObjectId('5ef4db29c29997a6ef020303') }
  - E11000 duplicate key error collection: pca_data_dev.dhs_contact index: _id_ dup key: { : ObjectId('5ef4db29c29997a6ef020305') }

2020-06-26T19:51:02.157+0000  no indexes to restore
2020-06-26T19:51:02.157+0000  finished restoring pca_data_dev.dhs_contact (2 documents)
2020-06-26T19:51:02.157+0000  reading metadata for pca_data_dev.customer from archive on stdin
2020-06-26T19:51:02.157+0000  error: multiple errors in bulk operation:
  - E11000 duplicate key error collection: pca_data_dev.subscription index: _id_ dup key: { : ObjectId('5ef4db2bc29997a6ef02030b') }
  - E11000 duplicate key error collection: pca_data_dev.subscription index: _id_ dup key: { : ObjectId('5ef4db32c29997a6ef020312') }
  - E11000 duplicate key error collection: pca_data_dev.subscription index: _id_ dup key: { : ObjectId('5ef4dcd1c29997a6ef02033f') }
  - E11000 duplicate key error collection: pca_data_dev.subscription index: _id_ dup key: { : ObjectId('5ef4e84926a59d295ea4e11f') }

.....

2020-06-26T19:51:02.173+0000  finished restoring pca_data_dev.template (163 documents)
2020-06-26T19:51:02.173+0000  done
```

## Troubleshooting

### Know Issues

When running and calling api:

`Unauthorized`

This is due to the DB not having the correct creds.

1.) check `.env`

```shell
....

# MongoDB
DB_HOST=mongodb
DB_PORT=27017
DB_PW=rootpassword
DB_USER=root

# DB
MONGO_INITDB_ROOT_PASSWORD=rootpassword
MONGO_INITDB_ROOT_USERNAME=root
MONGO_INITDB_DATABASE=pca_data_dev
```

### AWS

AWS_ENDPOINT_URL= `http://host.docker.internal:4566`
AWS_ACCESS_KEY_ID=mock_access_key
AWS_SECRET_ACCESS_KEY=mock_secret_key
AWS_STORAGE_BUCKET_NAME=con-pca-local-bucket
AWS_STORAGE_BUCKET_IMAGES_NAME=con-pca-local-image-bucket
AWS_S3_REGION_NAME=us-east-1
DEFAULT_FILE_STORAGE=storages.backends.s3boto3.S3Boto3Storage

`DB_PW` and `DB_USER` should match `MONGO_INITDB_ROOT_PASSWORD` and `MONGO_INITDB_ROOT_USERNAME`

2.) Wipe DB

first take down containers `make down`

Remove docker volumes

```shell
docker volume prune

WARNING! This will remove all local volumes not used by at least one container.
Are you sure you want to continue? [y/N]
```

once this completes, bring images back up

`make up`

now api should return empty.

```shell
-> % curl -i -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:8000/api/v1/subscriptions/
HTTP/1.1 200 OK
Date: Tue, 14 Apr 2020 17:25:34 GMT
Server: WSGIServer/0.2 CPython/3.8.2
Content-Type: application/json
Allow: GET, POST, HEAD, OPTIONS
X-Frame-Options: DENY
Content-Length: 2859
X-Content-Type-Options: nosniff

[]
```

Notes: see
[additional docker refs](https://linuxize.com/post/how-to-remove-docker-images-containers-volumes-and-networks/)
for trouble shooting Docker

## Testing

### Requirements

Make sure when running any tests, from the CLI or VS Code, that a
virtual environment is being used with the application requirements and
testing requirements installed.

```bash
python -m venv .venv
source .venv/bin/activate # Linux
.venv/Scripts/Activate.ps1 # Windows
pip install -r requirements.txt
pip install -r test_requirements.txt
```

- [black](https://pypi.org/project/black/) - Uniform styling.

- [coverage](https://coverage.readthedocs.io/en/coverage-5.1/) -
Calculates code coverage from tests.

- [pytest](https://docs.pytest.org/en/latest/) - Easier to use
testing framework.

- [pytest-django](https://pytest-django.readthedocs.io/en/latest/) -
Library to better integrate pytest with Django

- [pytest-env](https://github.com/MobileDynasty/pytest-env) - Allows
environment variables to be put in pytest.ini for loading.

- [pytest-mock](https://github.com/pytest-dev/pytest-mock/) - Mock
integration with pytest.

- [pytest-pythonpath](https://pypi.org/project/pytest-pythonpath/) -
Allows additional python paths to be defined in pytest.ini.

- [radon](https://radon.readthedocs.io/en/latest/) - Calculates
code complexity.

### Setting up VS Code

1. Create and activate virtual environment in VS Code [https://code.visualstudio.com/docs/python/environments](https://code.visualstudio.com/docs/python/environments)

2. Configure pytest in VS Code. [https://code.visualstudio.com/docs/python/testing#_enable-a-test-framework](https://code.visualstudio.com/docs/python/testing#_enable-a-test-framework)

3. Discover Tests. [https://code.visualstudio.com/docs/python/testing#_test-discovery](https://code.visualstudio.com/docs/python/testing#_test-discovery)

4. Run Tests. [https://code.visualstudio.com/docs/python/testing#_run-tests](https://code.visualstudio.com/docs/python/testing#_run-tests)


### Pytest / Coverage

To get code coverage, it needs to be done from the command line.
After running the below steps, open `htmlcov/index.html` with a browser
to view code coverage and further details.

```bash
coverage run --omit *.venv* -m pytest ./src/ --disable-warnings
coverage html
```

Or use make command.

```bash
make coverage
```

### Cyclomatic Complexity

To determine cyclomatic complexity, use the radon package.

```bash
radon cc ./src/ -e "*.venv*" -s -o SCORE
```

Or use make command.

```bash
make cc
```

### Styling

For uniform styling, the black library can be used.

- [black](https://pypi.org/project/black/)

```bash
black /path/to/file
```
