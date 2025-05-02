# Dockerfile
FROM python:3.10.5

RUN mkdir usr/app

COPY requirements.txt .

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "projectapp.py"]
