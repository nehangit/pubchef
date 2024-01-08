# pubchef_rest_api

## Create and activate virtual environment (Windows)

`python -m venv backenv`

`cd backenv`

`.\Scripts\activate.bat`

## Install Python dependencies

`git clone https://github.com/nehangit/pubchef_rest_api.git`

`cd pubchef_rest_api`

`pip install -r requirements.txt`

## Create SQLite databse, run migrations

`(python manage.py makemigrations chefs)`

`python manage.py migrate`

## Run Django dev server

`python manage.py runserver`
