FROM python:3
COPY rest_api/ /app
ADD docker/api/entrypoint.sh /app
ADD docker/tools/telegraf /usr/bin/
ADD docker/api/api_telegraf.conf /app
RUN  apt update -y
RUN apt install postgresql postgresql-contrib -y
WORKDIR /app
RUN pip3 install -r requirements.txt
RUN chmod +x /usr/bin/telegraf
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
