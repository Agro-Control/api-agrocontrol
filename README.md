# api-agrocontrol

bla bla bla api for project agro control.

Obs: This project was built for using with docker, if you not want to use it you will need to change the connections parameters.

## Requirements
[Python](https://www.python.org/) version 3.8+
[PIP](https://pip.pypa.io/en/stable/installation/)
[Docker](https://www.docker.com/) (optional)
[Postgres](https://www.postgresql.org/) version 15.6+ (optional)
[Mongo](https://www.mongodb.com/pt-br) version 6.0+ (optional)

## Getting Started
First, make sure you have all the requirements installed, otherwise you may encounter some problems.
Now setup and install all the libraries required for this project
1. Clone this repo 
2. Create a virtual environment for this project directory```python -m venv venv``` (optional)
3. Activete a virtual environment (optional)
3.1 On Linux/Mac ```source venv/bin/activate```
3.2 On Windows ```venv\Scripts\activate```
4. Run ```pip install -r requirements.txt```

Or if you have docker installed just run ```docker compose -f docker-compose.yml up```, and no setup is required

Obs: There is a database start files for this project in /config, you can use it to start up the databases

## Run this project
To run this project locally, do in your terminal ```uvicorn app:app --host 0.0.0.0 --port 5000```
For development mode add ```--reload```

Obs: uvicorn is supported only on Linux/Mac distro, to run on Windows please use docker.

## Documentation

This api have two documentation, located in ```/docs``` or ```/redoc```

