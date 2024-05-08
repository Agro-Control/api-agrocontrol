FROM python:3.11
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT ["python3", "-u", "simulador.py", "--start"]