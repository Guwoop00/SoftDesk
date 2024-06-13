# SoftDesk

API-SoftDesk is a RESTful API for reporting and tracking technical issues.

## Project Initialization

### Windows :
Navigate to the desired folder.
###### • Clone the project

```
git clone https://github.com/Guwoop00/SoftDesk
```

###### • Activate the virtual environment

```
python -m venv env 
env\Scripts\activate
```

###### • Install the required packages

```
pip install -r requirements.txt
```


### MacOS et Linux :
Navigate to the desired folder.
###### • Clone the project
```
git clone https://github.com/Guwoop00/SoftDesk
```

###### • Activate the virtual environment
```
python3 -m venv env 
source env/bin/activate
```

###### • Install the required packages
```
pip install -r requirements.txt
```

## Usage

#### Run migrations (if necessary):

```
python manage.py makemigrations
python manage.py migrate
```

#### Start the Django server:

```
python manage.py runserver
```
We highly recommend using the Postman tool to navigate the API:
(https://www.postman.com/)