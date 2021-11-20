FROM joyzoursky/python-chromedriver:3.9-alpine
#https://stackoverflow.com/questions/47955548/docker-image-with-python3-chromedriver-chrome-selenium
#RUN apk add --no-cache bash nano

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 80

CMD [ "python3", "-m" , "flask", "run", "--port=80", "--host=0.0.0.0" ]