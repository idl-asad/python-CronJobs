export db_user=$db_user
export db_password=$db_password
export db_host=$db_host
export db_database=$db_database
export db_port=$db_port
export docker_network=$docker_network

python /opt/cronScripts/manager.py
python /opt/cronScripts/worker.py
