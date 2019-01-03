FROM python:3-alpine

ARG db_user
ARG db_password
ARG db_host
ARG db_database
ARG db_port

ENV db_user "${db_user}"
ENV db_password "${db_password}"
ENV db_database "${db_database}"
ENV db_host "${db_host}"
ENV db_port "${db_port}"


COPY ./ /opt/cronScripts

WORKDIR /opt/cronScripts

RUN pip install -r requirement.txt

COPY crontab /etc/cron.d/cb-Scripts

RUN chmod 0644 /etc/cron.d/cb-Scripts

RUN service cron start


