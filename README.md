## required: Django 2.0, PostgreSQL

## clone the repo, handle venv, etc.

## prepare the database, adjust settings.DATABASES

    mkdir logs
    python3 manage.py makemigrations
    python3 manage.py migrate
    python3 manage.py loaddata fixtures/data.json

## check the backend functionality:
    
    python3 test_model.py
    python3 test_view.py

