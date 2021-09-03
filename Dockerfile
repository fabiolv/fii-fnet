FROM python:3.8-alpine3.13

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

# COPY fiibasic.py fiibasic.py

COPY . .

CMD ["flask", "run"]