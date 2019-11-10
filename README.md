# Pandas with Flask demo
A simple demonstration of Pandas operation with Flask server.

## Installation

##### Requirements:
* Python 3
* Python PIP 3
* MySQL

For installing python package dependencies, run the following command:
```shell script
pip3 install -r requirements.txt
```

##### Setup MySQL database
Project contains `pandas-flask.sql` sql file. Import this file. Change the database credentials located in `app.py`  file.

```python
db = MySQLdb.connect("localhost", "root", "root", "pandas-flask")
```

## Run the Project 
```shell script
python3 wsgi.py
```

## Deployment
Follow the following link: 
[Link](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-16-04)
