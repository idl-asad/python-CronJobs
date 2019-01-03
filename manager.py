import mysql.connector
import sys
import os
from croniter import croniter
from datetime import datetime

config = {
  'user': os.environ['db_user'],
  'password': os.environ['db_password'],
  'host': os.environ['db_host'],
  'database': os.environ['db_database'],
  'port': int(os.environ['db_port']),
  'raise_on_warnings': True
}

try:
    cnx = mysql.connector.connect(**config)
except mysql.connector.Error as err:
    sys.exit("Something went wrong: {}".format(err))

query = ("SELECT modelid AS model_id, id AS metric_id, schedule AS scheduleTime FROM metric "
         "WHERE modelid IS NOT NULL "
         "UNION "
         "SELECT A.model_id AS model_id, A.metric_id AS metric_id,COALESCE(B.schedule, A.scheduleTime) AS scheduleTime "
         "FROM(SELECT model.id AS model_id, met.id AS metric_id, met.schedule AS scheduleTime FROM metric met "
         "CROSS JOIN model WHERE modelid IS NULL) A "
         "LEFT JOIN modelmetric B ON A.model_id = B.modelid AND A.metric_id = B.metricid; ")

cursor = cnx.cursor()
cursor.execute(query)
metrics = cursor.fetchall()

for item in metrics:
    scheduledQuery = "Select * from schedulerlist where model_id='%s' AND metric_id='%s'"
    cursor.execute(scheduledQuery, (item[0], item[1]))
    scheduled = cursor.fetchall()
    base = datetime.now() if len(scheduled) == 0 or not scheduled[0][7] else scheduled[0][7]
    iterator = croniter(item[2], base)
    nextScheduleTime = iterator.get_next(datetime)
    addScheduler = ("INSERT INTO schedulerlist "
                    "(model_id, metric_id, status, schedule_Time, next_schedule_time) "
                    "VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE schedule_Time=%s, "
                    "next_schedule_time=%s")
    schedulerData = (item[0], item[1], "wait", item[2], nextScheduleTime.isoformat(), item[2],
                     nextScheduleTime)
    cursor.execute(addScheduler, schedulerData)
    cnx.commit()

tobeReadyList = ("UPDATE schedulerlist SET status=%s, last_schedule_time=%s, update_date=%s"
                 "Where failure_occurence < %s AND (status=%s OR status=%s OR status=%s) "
                 "AND next_schedule_time <= %s")
readyValues = ('ready', datetime.now(), datetime.now(), 3, 'wait', 'inprogress', 'inqueued', datetime.now())

cursor.execute(tobeReadyList, readyValues)
cnx.commit()
cnx.close()

