# Dyplom APP

## Prerequisites

Ensure you have the following tools installed:
- Python 3.8 or newer
- pip (Python Package Installer)
- virtualenv
- PostgreSQL

## Clone the Repository

1. Clone the repository from GitHub
2. Navigate to the cloned repository:
```
cd your_repository
```
## Environment Setup

1. Create a Python virtual environment (venv) using the command:
```
python3 -m venv venv
```
2. Activate the virtual environment:
On Unix or MacOS systems, use the command:
  ```
  source venv/bin/activate
  ```
On Windows systems, use the command:
  ```
  venv\Scripts\activate
  ```

3. Install the required packages using pip:

```
pip install -r requirements.txt
```

## PostgreSQL Database Configuration

1. Start your PostgreSQL service.

2. Create a new database for your project. Recommend pgadmin4 

3. Update the `DATABASES` configuration in your Django `settings.py` file:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database_name',
        'USER': 'your_postgres_username',
        'PASSWORD': 'your_postgres_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Remember to replace `your_project_name`, `your_database_name`, `your_postgres_username`, and `your_postgres_password` with your actual Django project name, PostgreSQL database name, PostgreSQL username, and PostgreSQL password, respectively. Also, ensure you have a `requirements.txt` file that contains all the required packages to run your project.


## Running the Django project
1. Navigate to your Django project directory:
```
cd your_project_name
```
2. Run migrations to database:
```
python manage.py makemigrations
python manage.py migrate
```
3. Load base data by run commands:
```
python manage.py load_citys core/data/city_names_small.csv
python manage.py load_category core/data/advertise_category.csv
```
4. Run django server:
```
python manage.py runserver
```

Your Django project should now be accessible at `http://127.0.0.1:8000/` in your browser.



