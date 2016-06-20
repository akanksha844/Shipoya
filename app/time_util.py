from datetime import date , datetime

def seconds(x):
	x = str(x)
	sx = x
	if len(sx) == 14:		
		hour = int(x[8])*10 + int(x[9])
		minutes = int(x[10])*10 + int(x[11])
		seconds = int(x[12])* 10 + int(x[13])
		# print "%d %d %d" %(hour , minutes , seconds)
		x = long(0)
		x += int(seconds)
		x += 60 * int(minutes)
		x += 60 * 60 * int(hour)
	else:
		print x
		print "timestamp error expected length is 14"
		assert(False)
	return x

def findDate(x):
	hour = int(x[8])*10 + int(x[9])
	minutes = int(x[10])*10 + int(x[11])
	seconds = int(x[12])* 10 + int(x[13])
	day =int(x[0]) * 10 + int(x[1]);
	month = int(x[2]) * 10 + int(x[3]);
	year = int(x[4])*1000 + int(x[5])*100 + int(x[6])*10 + int(x[7]);
	currentdate = datetime(year , month , day , hour , minutes , seconds)
	# print currentdate
	return currentdate

def single_elapsed(x):
	standard = "11111111111111"
	fdate = findDate(standard)
	sdate = findDate(str(x))
	elapsed = (sdate - fdate).total_seconds()
	return elapsed

def elapsed(x , y):
	fdate = findDate(str(x))
	sdate = findDate(str(y))
	elapsed = (sdate - fdate).total_seconds()
	# print elapsed
	return elapsed

def cmp_dates(x , y):
	fdate = findDate(x[2])
	sdate = findDate(y[2])

	ftime = x[2].split(' ')
	stime = y[2].split(' ')
	mindate = datetime(1 , 1 , 1 , 1 , 1 , 1)
	e1 = (fdate - mindate).total_seconds()
	e2 = (sdate - mindate).total_seconds()
	if e1 > e2:
		return 1;
	if e1 == e2:
		return 0;
	return -1;
