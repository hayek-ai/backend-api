# Hayek Backend API

This is a REST API that uses the Flask-Restful extension for Flask.

# Setup

Requirements:

- Python-3.7
- pip3

Create a .env file to store Application settings.

```
touch .env
```

Setup virtualenv

```
pip3 install virtualenv
virtualenv venv --python=python3
source venv/bin/activate
```

Install dependencies

```
pip3 install -r requirements.txt
```

Create docker images of test and development Postgres databases. 
Make sure they are running on different ports so that you can run both at the same time.
Example:

```
docker run --name hayek_test_db \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_USER=michael \
    -e POSTGRES_DB=hayek_test_db \
    -p 5431:5432 \
    -d postgres

docker run --name hayek_development_db \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_USER=michael \
    -e POSTGRES_DB=hayek_development_db \
    -p 5432:5432 \
    -d postgres
```

Connect application to databases in .env file.  Example:

```
TEST_DATABASE_URI="postgresql://michael:postgres@localhost:5431/hayek_test_db"
DEV_DATABASE_URI="postgresql://michael:postgres@localhost:5432/hayek_development_db"
```

Before testing & development, start up both databases. Example:

```
docker start hayek_test_db
docker start hayek_development_db
```

Build Command

```
gunicorn application:app
```
