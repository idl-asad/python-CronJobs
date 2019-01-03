import mysql.connector
import sys
import os
import subprocess
import logging
from datetime import datetime, timedelta

config = {
  'user': os.environ['db_user'],
  'password': os.environ['db_password'],
  'host': os.environ['db_host'],
  'database': os.environ['db_database'],
  'port': os.environ['db_port'],
  'raise_on_warnings': True
}

try:
    cnx = mysql.connector.connect(**config)
except mysql.connector.Error as err:
    sys.exit("Something went wrong: {}".format(err))

cursor = cnx.cursor()

cursor.execute("select model_id, group_concat(metric_id ) from schedulerlist where status=%s GROUP BY model_id",
               ('ready', ))
readyToRunMetric = cursor.fetchall()

cursor.execute("Update schedulerlist SET status=%s where status=%s", ('queued', 'ready'))
cnx.commit()

for item in readyToRunMetric:
    startDate = datetime.now().date() - timedelta(days=3)
    endDate = datetime.now().date()
    print("running job......", item[0], item[1], sep='***')
    runJob = ("docker run --rm -e StartDate={0} -e EndDate={1} -e Input_ModelID={2} -e IncludeMetrics={3} "
              "--net=validation-phase2_default cb_datapipeline:test").format(startDate, endDate, item[0], item[1])
    logging.info("Running Job at {0} | {1}".format(datetime.now().isoformat(), runJob))
    subprocess.call(runJob, shell=True)

