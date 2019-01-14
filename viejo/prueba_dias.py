from datetime import timedelta
import datetime
def next_weekday(d, weekday_list):

	days=[]
	for weekday in weekday_list:
	    days_ahead = weekday - d.weekday()
	    if days_ahead <= 0: # Target day already happened this week
	        days_ahead += 7
	    days.append(d + datetime.timedelta(days_ahead))
	return days

d=datetime.date(2019,1,15)
weekday=[0,2,4]

dia_que_quiero = datetime.date(2019,2,7)

array_dates = next_weekday(d,weekday)

print(array_dates)

for date in array_dates:
	aux_date=date
	while aux_date <=dia_que_quiero:
		if aux_date == dia_que_quiero:
			print('hijo de mill',aux_date)
			break
		else:
			aux_date+=timedelta(days=7)

print('fin')