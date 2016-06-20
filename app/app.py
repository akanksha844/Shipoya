from flask import Flask , render_template , request 
from geopy.distance import vincenty
import pymongo
from datetime import date , datetime
import numpy
import time_util

app = Flask(__name__)


def connect_db():
	client = pymongo.MongoClient('localhost:27017')
	db = client.raw_data
	return db

def connect_city_db():
	client = pymongo.MongoClient('localhost:27017')
	db = client.citybounds
	return db


"""
city data structure

city_data = {
			district : {
						lat : 
						lng :
						radius : 
						}
		
			}
"""
def loadcity():
	db = connect_city_db()
	data = db.citybounds2.find()
	for keys in data[0]:
		try:
			for items in data[0][keys]:
				for district in data[0][keys][items]:
					x = data[0][keys][items][district]
					try :
						lat = float(x['lat'])
						lng = float(x['lng'])
						radius = float(x['radius'])
						city_data[district] = {}	
						city_data[district]['lat'] = lat
						city_data[district]['lng'] = lng
						city_data[district]['radius'] = radius
					except ValueError:
						pass
		except TypeError:
			pass
	# print city_data
	print "Number of cities " , len(city_data)


trucks_avg_data = {}
def overall_avg():
	file = open("findavg.txt" , "r")
	for line in file:
		line = str(line)
		data = line.split('&')
		source = data[0]
		destination = data[1]
		key = (source , destination)
		if key not in trucks_avg_data:
			trucks_avg_data[key] = []
		try : 
			trucks_avg_data[key].append(float(data[2]))
		except ValueError:
			print line
			pass

	frequent_key = []
	for key in trucks_avg_data:
		if len(trucks_avg_data[key]) >= 2:
			frequent_key.append( (len(trucks_avg_data[key]) , key) )
		# print key , len(trucks_avg_data[key])
	frequent_key.sort(key = lambda x : x[0] , reverse = True)

	for items in frequent_key:
		print items
	# print frequent_key

journey = []
def Journey(truckID):
	db = connect_db()
	data = db.correct_express_cargo.find({"truck_rc" : truckID} , no_cursor_timeout = True)
	points = data[0]['pvt_data']
	global journey 
	journey = []
	for point in points:
		journey.append( (float(point['lat']) , float(point['lng']) , (point['timestamp']) ) )
	journey.sort(time_util.cmp_dates)


city_data = {}
def current_city(latitude , longitude):
	p1 = (latitude , longitude)
	for x in city_data:
		try:
			p2 = (float(city_data[x]['lat']) , float(city_data[x]['lng']))
			if vincenty(p1 , p2).km <= float(city_data[x]['radius']):
				return str(x)
		except ValueError:
			pass
	return None

#average travel time for all source destination pairs
def findavg(truckID):
	print "findavg " , truckID
	Journey(truckID)
	print "journey loaded"
	entry = {}
	exit = {}
	prev = None
	current = None	
	mintime = {}
	maxtime = {}
	vis = {}
	travel = {}
	l = 1
	r = len(journey)
	for item in journey:
		print "done %d left %d" %(l , r - l)
		l += 1
		lat = item[0]
		lng = item[1]
		timestamp = item[2]	
		city = current_city(lat , lng)
		
		if city is None:
			continue
			
		if city == prev:
			maxtime[city] = timestamp
			continue

		if prev is None:	#first city visited
			mintime[city] = timestamp
			maxtime[city] = timestamp
			prev = city
			current = city
			continue
		elapsed = time_util.elapsed(maxtime[prev] , timestamp)
		key = (prev , city)
		if key not in travel:
			travel[key] = []
		travel[key].append(elapsed)
		prev = city
		maxtime[city] = timestamp
	return travel

def init():
	loadcity()
	overall_avg()


@app.route('/table')
def table():
	return render_template('index.html')

@app.route('/')
def home():
	return '<h1> Truck Analysis </h1>'


def convert_seconds_hours(m):
	m = int(m)
	hours = 0
	if m >= 3600:
		hours = m / 3600
	m %= 3600
	minutes = 0
	if m >= 60:
		minutes = m / 60
	m %= 60
	seconds = m

	time = ""
	if hours > 0:
		time = str(hours) + " hours "
	if minutes > 0:
		time = time + str(minutes) + " minutes "
	time = time + str(seconds) + " seconds"
	return time

#TS08UB-7454

#Beautiful projections 
# db.correct_express_cargo.find( {} , {_id : 0 , pvt_data : 0} ).pretty()
@app.route('/journey/<truckID>')
def journey(truckID):
	db = connect_db()
	data = db.correct_express_cargo.find({'truck_rc' : truckID})
	rcount = 0
	for item in data:
		rcount += 1
	if rcount == 0:
		return '<h1> Truck with ID %s not found </h1>' %(truckID)
	route = findavg(truckID)
	jin = []
	for keys in route:
		source = keys[0]
		destination = keys[1]
		if keys in trucks_avg_data:
			m1 = numpy.mean(route[keys])
			m2 = numpy.mean(trucks_avg_data[keys]) 
			duration1 = convert_seconds_hours(m1)
			duration2 = convert_seconds_hours(m2)
			jin.append( (keys[0] , keys[1] , duration1 , duration2) )
	print jin
	jin.append(("" , "" , "" , ""))
	return render_template('journey.html' , jin = jin , item = jin[0])
	# return '<h1> Journey for %s </h1>' %(truckID)

if __name__ == '__main__':
	init()
	app.run(debug = True)