#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
import psycopg2
import datetime


window = 20 # window in minutes

try:
        conn = psycopg2.connect("dbname='gtfs_praha'")
except:
        print ("I am unable to connect to the database")

cur = conn.cursor()

cur.execute(" SELECT stop_id FROM gtfs_stops WHERE stop_name = '"+sys.argv[1]+"';")
stops = map(lambda x: x[0],cur.fetchall())

cur.execute("SELECT route_id FROM gtfs_routes WHERE route_short_name ='"+sys.argv[2]+"';")
route = cur.fetchall()[0][0]

# TODO find day
now = datetime.datetime.now()
day = now.strftime("%A").lower()
time = now.strftime("%X")
time_last = (now+datetime.timedelta(minutes=window)).strftime("%X")
date = now.strftime("%Y-%m-%d")
cur.execute("SELECT service_id FROM gtfs_calendar WHERE "+day+"=1 AND start_date <= '"+date+"' AND end_date >= '"+date+"';")
services = map(lambda x: "'"+x[0]+"'",cur.fetchall())

strservices = ",".join(services)
cur.execute("SELECT DISTINCT trip_id FROM gtfs_trips WHERE route_id = '"+route+"' AND (service_id IN ("+strservices+"));")
trips = map(lambda x: x[0], cur.fetchall())

for trip in trips:
	cur.execute("SELECT stop_sequence FROM gtfs_stop_times WHERE trip_id = "+str(trip)+" AND stop_id IN ('"+"','".join(stops)+"') AND departure_time > '"+time+"' AND departure_time < '"+time_last+"' ORDER BY stop_sequence;")
	try:
		seq = cur.fetchall()[0][0]
	except IndexError:
		continue
	cur.execute("SELECT * FROM gtfs_stop_times WHERE trip_id="+str(trip)+" AND stop_sequence >= "+str(seq)+" ORDER BY stop_sequence;")
	stoptimes = cur.fetchall()
	#print stoptimes
	for stop in stoptimes:
		cur.execute("SELECT stop_name FROM gtfs_stops WHERE stop_id = '"+stop[3]+"';")
		name = cur.fetchall()[0][0]
		print "{:30}	{}	{}".format(name,stop[1],stop[2])
	print "--------------------------"	
		


