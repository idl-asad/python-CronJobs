FROM python:3-slim-stretch

ARG db_user
ARG db_password
ARG db_host
ARG db_database
ARG db_port
ARG docker_network

ENV db_user "${db_user}"
ENV db_password "${db_password}"
ENV db_database "${db_database}"
ENV db_host "${db_host}"
ENV db_port "${db_port}"
ENV docker_network "${docker_network}"

COPY ./ /opt/cronScripts

WORKDIR /opt/cronScripts

RUN apt-get update && apt-get -y install cron && apt-get install curl \
        curl -sSL https://get.docker.com/ | sh

RUN pip install -r requirement.txt

RUN chmod +x /opt/cronScripts/manager.py
RUN chmod +x /opt/cronScripts/worker.py
RUN chmod +x /opt/cronScripts/cron.sh

COPY crontab /etc/cron.d/cb-scripts

RUN chmod 0644 /etc/cron.d/cb-scripts
 
RUN touch /var/log/cron.log

VOLUME /var/run/docker.sock

CMD ["/bin/bash", "-c", "declare -p | grep -E 'db_user|db_host|db_password|db_port|db_database' > /container.env && cron && crontab /etc/cron.d/cb-scripts && tail -f /var/log/cron.log"]


