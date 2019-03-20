from flask import Flask,render_template,request,escape,session,make_response
from DBcm import UseDatabase
import calendar
import random
import pdfkit

app = Flask(__name__)
app.secret_key='shubham'

app.config['dbconfig']={'host':'127.0.0.1',                   #setup the db configuration
						'user':'shubham',                     #database user
						'password':'shubham123',              #db user password
						'database':'ferrydb'}                 #database name


@app.route('/')
@app.route('/GTentry',methods=['POST','GET'])
def GTentry():
#	if request.form['submit']=='WebFerry':
	return render_template('GTentry.html',the_title='GRAND TRAVEL BOOKING PORTAL')

	
@app.route('/add',methods=['POST','GET'])
def add():
	return render_template()
	
@app.route('/admin',methods=['POST','GET'])
def admin():
	if request.form['submit'] == 'Add':
		return render_template('alter.html',the_title ='SOURCE MAINTAINENCE MENU',the_req_title='Source',the_action='/add')
	elif request.form['submit'] == 'Modify':
		return render_template('alter.html',the_title ='DESTINATION MAINTAINENCE MENU',the_req_title='Destination')
	elif request.form['submit'] == 'Delete': 
		return render_template('alter.html',the_title ='DEPATURE TIME MAINTAINENCE MENU',the_req_title='Departure time')
	else:
		pass
	
@app.route('/entry',methods=['POST','GET'])
def entry_page():
	if request.form['submit']=='WebFerry':
		return render_template('entry.html',the_title='GRAND TRAVEL BOOKING PORTAL')
	elif request.form['submit'] == 'Admin':
		return render_template('admin.html',the_title='ADMIN MAINTAINENCE')
	else:
		return render_template('invalidtime.html',the_title='This is not my module ;-)')

@app.route('/download',methods=['POST','GET'])
def receipt():
	no_tickets=str(session.get('no_tickets'))
	no_tickets=int(no_tickets)
	my_source = session.get('my_source')
	my_dest = session.get('my_dest')
	my_dep_time = session.get('my_dep_time')
	my_arr_time = session.get('my_arr_time')
	my_total_fare =session.get('my_total_fare')
	my_dis_fare = session.get('my_dis_fare')
	my_date = session.get('my_date')
	my_book_id=session.get('my_book_id')
	with UseDatabase(app.config['dbconfig']) as cursor:
		_SQL="""select name,age from pass_details where booking_id =%s"""
		cursor.execute(_SQL,(my_book_id,))
		data=cursor.fetchall()
	print('book_id:',my_book_id)
	print(data)	

	rendered = render_template('receipt.html',the_title='GT PAYMENT RECEIPT',the_book_id=my_book_id,the_source=my_source.upper(),the_dest=my_dest.upper(),the_name_age=data,the_dep=my_dep_time,the_arr=my_arr_time,the_fare=my_total_fare,the_discount=my_dis_fare,the_date=my_date)
	css=['hf.css']
	pdf=pdfkit.from_string(rendered,False)
	response = make_response(pdf)
	response.headers['Content-Type']= 'application/pdf'
	response.headers['Content-Disposition'] = 'attachment; filename=receipt.pdf'
	return response
	entry_page()

	
@app.route('/post_pay',methods=['POST','GET'])
def post_pay():
	print(request.form['card_name'],request.form['card_number'],request.form['cvv'])
	if request.form['card_name'] == '' or request.form['card_number'] == '' or request.form['cvv'] == '' :
		return render_template('invalidtime.html',the_title='You have not entered payment details. Please go back and enter.')
	else:
		return render_template('post_pay.html',the_title='PAYMENT RECEIVED SUCCESSFULLY')
	
@app.route('/payment',methods=['POST','GET'])
def payment_method():

	return render_template('payment_method.html',the_title='Choose your payment method')
	
@app.route('/credit',methods=['POST','GET'])
def cards():
	if request.form['submit'] == 'Credit Card':
		return render_template('credit.html',the_title='PAYMENT PAGE',the_card='Credit Card')
	else:
		return render_template('credit.html',the_title='PAYMENT PAGE',the_card='Debit Card')
	
	
	
@app.route('/tickets',methods=['POST','GET'])
def tickets():
	with UseDatabase(app.config['dbconfig']) as cursor:
		_SQL="""select booking_id from pass_details"""
		cursor.execute(_SQL)
		data=cursor.fetchall()
	while(True):
		book_id = random.randint(1,999999)
		if book_id in data:
			pass
		else:
			break
	no_tickets=str(session.get('no_tickets'))
	print(no_tickets)
	no_tickets=int(no_tickets)
	l_age=[]
	l_name_age=[]
	for i in range(0,no_tickets):
		n='name'+str(i)
		a='age'+str(i)
		l_name_age.append((request.form[n],request.form[a]))
#		l_name_age.append(request.form[a])
		l_age.append(int(request.form[a]))
		with UseDatabase(app.config['dbconfig']) as cursor:
			_SQL = """insert into pass_details(booking_id,name,age) values (%s,%s,%s)"""
			cursor.execute(_SQL,(book_id,request.form[n],request.form[a]))
			
	session['my_l_name_age']=l_name_age
	session['my_book_id']=book_id
	my_date = session.get('my_date')
	my_fare = int(session.get('my_fare'))
	discounted_fare = (my_fare) * 0.25
	total_fare = 0.0 
	Accompanied_By_Adult=False
	for pas in l_age:
		if pas >= 18:
			Accompanied_By_Adult=True
	if no_tickets == 1 and l_age[0]<12:
		return render_template('invalidtime.html',the_title='Children below 12 years age cannnot travel alone')
	if no_tickets > 1:
		for passenger in l_age:
			if passenger < 10 and Accompanied_By_Adult:
				total_fare+=discounted_fare
			else:
				total_fare+=my_fare
	grand_total = no_tickets * my_fare
	dis=grand_total-total_fare
	with UseDatabase(app.config['dbconfig']) as cursor:
		_SQL = """insert into book_details(booking_id,book_fare,discount,book_date,no_of_pass) values (%s,%s,%s,%s,%s)"""
		cursor.execute(_SQL,(book_id,total_fare,dis,my_date,no_tickets))
	my_source = session.get('my_source')
	my_dest = session.get('my_dest')
	session['my_total_fare']=total_fare
	session['my_dis_fare']=dis
	print(l_name_age)
	return render_template('conf_book.html',the_title='BOOKING CONFIRMATION',the_tickets=no_tickets,the_source=my_source.upper(),the_dest=my_dest.upper(),the_date=my_date,the_name_age=l_name_age,the_fare=total_fare,the_discount=dis)
	
@app.route('/book',methods=['POST','GET'])
def book_tickets():
	
	n_tickets = int(request.form['tickets'])
	session['no_tickets'] = n_tickets
	my_date = session.get('my_date')
	print(my_date)
	with UseDatabase(app.config['dbconfig']) as cursor:
		_SQL="""select sum(no_of_pass) from book_details where book_date =%s"""
		cursor.execute(_SQL,(my_date,))
		data=cursor.fetchall()
	if data[0][0] == None:
		return render_template('book.html',the_title='HAPPY TO SEE YOU ON OUR BOOKING PORTAL',the_number_ticket=n_tickets)
	else:
		if (data[0][0]) + n_tickets > 500:
			return render_template('max_limit.html',the_title='Booking full',the_date=my_date)
		else:
			return render_template('book.html',the_title='HAPPY TO SEE YOU ON OUR BOOKING PORTAL',the_number_ticket=n_tickets)
	
	
@app.route('/search',methods=['POST','GET'])
def search_db():
	sour = request.form['source']                        #fetches source input entered by user
	sour = sour.lower().rstrip()                         #converts to lowercase and strip extra spaces at end
	session['my_source'] = sour
	dest = request.form['destination']                   #fetches destination input entered by user
	dest= dest.lower().rstrip()                          #converts to lowercase and strip extra spaces at end
	session['my_dest'] = dest
	date = str(request.form['date'])                          #fetches date entered by user 
	session['my_date'] = date
	with UseDatabase(app.config['dbconfig']) as cursor:
		_SQL="""select source,destination,dep_time,arr_time,fare from ferry"""
		cursor.execute(_SQL)
		data=cursor.fetchall()
		
	#04/09/2018	
	if len(date) > 10 or len(date) < 10: 
		return render_template('invalidtime.html',the_title="You have entered invalid date format.Please enter date in correct format(DD/MM/YYYY)")
	year=int(date[:4])
	month=int(date[5:7])
	day=int(date[8:])
	if calendar.weekday(year,month,day) == 6:
		return render_template('invalidtime.html',the_title="Ferry is not operational on Sunday.Please enter a weekday")
	sour_dest_l=[]                                 #to store source dest pairs
	for i in data: 
		sour_dest_l.append((i[0],i[1]))            #stores source dest pairs in sour_dest_l
	dep_time_d={}                                  #initialise a depature time dict
	arr_time_d={}                                  #initialise a arrival time dict 
	fare_d = {}                                    #initialise fare dict
	j=k=l=0
	for i in sour_dest_l:                          #store depature times correspoding to pair of (source,dest)
		dep_time_d[i]=data[j][2]
		j+=1	
	for i in sour_dest_l:                          #store arrival times correspoding to pair of (source,dest)
		arr_time_d[i]=data[k][3]
		k+=1
	for i in sour_dest_l:                          #store fares correspoding to pair of (source,dest)
		fare_d[i]=data[l][4]
		l+=1
	
	if (sour,dest) in dep_time_d and (sour,dest) in arr_time_d and (sour,dest) in fare_d:
		dep = str(dep_time_d[(sour,dest)])+ ' UTC'
		session['my_dep_time']= dep
		arr = str(arr_time_d[(sour,dest)])+ ' UTC'
		session['my_arr_time']= arr
		fare = str(fare_d[(sour,dest)])+ ' £'
		print(fare_d[(sour,dest)],type(fare_d[(sour,dest)]))
		session['my_fare'] = (fare_d[(sour,dest)])
		return render_template('time.html',the_title='Journey Time Information',the_source=sour.upper(),the_dest=dest.upper(),the_dep=dep,the_arr=arr,the_fare=fare)
	else:
		return render_template('invalidtime.html',the_title="You have entered invalid source and destination location pair.Please go back and enter Correct Source and Destination")

	
	
app.run(debug=True)