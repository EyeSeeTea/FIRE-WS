FROM ubuntu:latest
ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
RUN apt-get update 
RUN apt-get -y install python virtualenv 
RUN useradd -u 1000 -d /home/fire -ms /bin/bash fire
USER fire
WORKDIR /home/fire
RUN virtualenv --python /usr/bin/python3.5 .env
ADD firews.tar /home/fire
RUN .env/bin/pip install -r requirements.txt
ENV CONFIG_FILE fire-ws.conf
ENV FLASK_APP fire/api/server.py
RUN .env/bin/flask db upgrade
RUN .env/bin/flask seed
EXPOSE 5000
CMD .env/bin/flask run -h 0.0.0.0
