
import paho.mqtt.client as mqtt
from flask import Flask, render_template, redirect, url_for, request, session, flash,request
from flask_socketio import SocketIO, emit
from functools import wraps
import json
import sqlite3
import yaml
import time
import smtplib
import collections
import pyaudio
import numpy as np
from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, session
from flask import Flask, render_template, redirect, url_for ,request 
from wtforms import StringField, PasswordField, BooleanField,SelectField
from flask_sqlalchemy  import SQLAlchemy
import datetime
#import context  # Ensures paho is in PYTHONPATH
import paho.mqtt.publish as publish
import datetime
from datetime import datetime
from time import gmtime, strftime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sakib!'
socketio = SocketIO(app)
app.debug = True


app = Flask(__name__)
app.config['SECRET_KEY'] = 'sakib!'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ncs.db'
app.config['debug'] = True
toolbar = DebugToolbarExtension(app)
socketio = SocketIO(app)
global topic_login 


# def convert(data):
    # if isinstance(data, basestring):
        # return str(data)
    # elif isinstance(data, collections.Mapping):
        # return dict(map(convert, data.iteritems()))
    # elif isinstance(data, collections.Iterable):
        # return type(data)(map(convert, data))
    # else:
        # return data

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))

    return wrap

def play_shit(samples, fs, volume):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=fs,
                    output=True)
 
    # play. May repeat with different volume values (if done interactively) 
    stream.write(volume*samples)
    stream.stop_stream()
    stream.close()
    p.terminate()	

def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))
    pass	
	
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
	client.subscribe("icu")
	client.subscribe("ccu")
	#client.subscribe("crv")
	#client.subscribe("clz")
	#client.subscribe("fwd")
	client.subscribe("mwd")
	client.subscribe("eps8266/4")
	client.subscribe("eps8266/5")
	#client.subscribe("cab")
	#client.subscribe("dng")
	#client.subscribe("dps")
	client.subscribe("dcu")

# The callback for when a PUBLISH message is received from the ESP8266.
#dividing the data according to their topic
def on_message(client, userdata, message):
	#print(session['topic_login'])
	t = message.topic 
	print(t)
	print(message)
	a=time.strftime("%I:%M:%S")
	x = yaml.load(message.payload)
	#	print(x['device'],a)
	#	print(x['message'],a) 
	#print(x['bed']
	print(x)
	conn = sqlite3.connect('ncs.db')
	c=conn.cursor()
	c.execute('SELECT bed FROM map WHERE device=(?)',(x['device'],))
	bed_no=c.fetchall()
	c.execute('select dept from map where device = (?)',(x['device'],))
	topic = c.fetchall()
	#topic = u", ".join(topic[0])
	print(bed_no)
	if bed_no:
		bed_no = u", ".join(bed_no[0])
	else:
		bed_no = None
	
	
	#print(bed_no)
	x.update({'bed':bed_no})

		
	c.execute("INSERT INTO ncsreadings(device,message,currentdate,currentime,bed) VALUES(?,?,date('now'),?,?)",(x['device'], x['message'],a,x['bed']))
	conn.commit()
	conn.close()
	admin_data=[x]
	
	socketio.emit('topic_all',t)
	socketio.emit('admin', admin_data)
	#global topic_login
	#print('on message  '+ topic_login)
	# if topic_login == 'ccu' and topic == 'ccu':
		# admin_data_CCU=[x]
		# socketio.emit('admin', admin_data_CCU)
	# elif topic_login == 'mwd' and topic == 'mwd':
		# admin_data_CCU=[x]
		# socketio.emit('admin', admin_data_CCU)
	print(x['message'],x['device'],topic,bed_no,t)
	#bed_no = '03'
#	publish.single("esp8266/4", "1", hostname="localhost")

#	mes = '1'+ ':'+ bed_no + ':'+  strftime("%Y-%m-%d %H:%M:%S", gmtime()) +':'+ t 
# original	mes = x['message']+'/' + t+ '/'+ bed_no + '/'+  str(datetime.now()) 
	try:
		mes = x['message']+'/' + t+ '/'+ bed_no + '/'+  str(datetime.now()) 
		publish.single("esp8266/4",mes, hostname="localhost")
		print mes
	except (RuntimeError, TypeError, NameError):
		pass 
		
#	if x['message'] == 'Clear' or x['message']=='Presence':
#		publish.single("esp8266/4", mes, hostname="localhost")
	
	#topic_login = session.get('topic_login',None)
	#print(topic_login)
	#print(session['topic_login'])

	# if (topic == 'ccu' and session['topic_login'] == 'ccu'): 
		# admin_data_CCU=[x]
		# print('CCU inside if')
		# socketio.emit('admin', admin_data_CCU)
	# elif(topic == 'mwd' and session['topic_login'] == 'mwd'):	
		# print('mwd inside if')
		# admin_data_MWD=[x]
		# socketio.emit('admin', admin_data_MWD)
	if x['message'] == 'Calling':
		f = 440.0        # sine frequency, Hz, may be float    
		duration = 1.0   # in seconds, may be float
		fs = 44100       # sampling rate, Hz, must be integer
# generate samples, note conversion to float32 array
# for paFloat32 sample values must be in range [-1.0, 1.0]
		samples = (np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)
 
		#while True:
		#	play_shit(samples, fs, volume=1)
		#	sound = yaml.load(message.payload)
		#	if sound['message'] == 'Present':
		#		break;
	#while True:	
		#x = yaml.load(message.payload)
#	socketio.emit('admin', admin_data)
	#	on_message(client, userdata, message)
	#	if (x['message'] == 'Presence' ):
	#		break;
	#	if (x['message'] == 'Clear'):
	#		break;
	
#	socketio.emit('HW', 'hello world')
#	if message.topic == "ccu":
#		socketio.emit('admin', admin_data_CCU)
#		print('CCU update CCU')
		
#	if message.topic == "mwd":
#		socketio.emit('admin', admin_data_MWD)
#		print('CCU update MWD')		
		#socketio.emit('message',x['message'])
    # # socketio.emit('admin', admin_data) 
    # # if message.topic == "icu":
        # # print("NCS table update")
        # print(message.payload.json())
        # print(dhtreadings_json['temperature'])
        # print(dhtreadings_json['humidity'])
        # # y=yaml.load(message.payload)
	# # data=[y]
	# # print(data)
        # # socketio.emit('message',data)
# sakib
	# # print(y)
		
        # dhtreadings_json = json.loads(y)
	# # a=time.strftime("%I:%M:%S")
	# # print(y['device'])		

        # connects to SQLite database. File is named "sensordata.db" without the quotes
        # WARNING: your database file should be in the same directory of the app.py file or have the correct path
        # # conn=sqlite3.connect('ncs.db')
        # # c=conn.cursor()

        # # c.execute("INSERT INTO ncsreadings(device,message,currentdate,currentime,bed) VALUES(?,?,date('now'),?,?)",(y['device'], y['message'],a,y['bed']))

        # # conn.commit()
        # # conn.close()		
    # if message.topic == "ccu":
        # print("NCS table update robiul")
		# x = yaml.load(message.payload)
		# print(x['device'])
        # #print(message.payload.json())
        # #print(dhtreadings_json['temperature'])
        # #print(dhtreadings_json['humidity'])
        # #z=yaml.load(message.payload)
	# data1=[x]
	# print(data1)
        # socketio.emit('message1',data1)
# #sakib
	# print(x)
		# #
        # #dhtreadings_json = json.loads(y)
	# #a=time.strftime("%I:%M:%S")
	# print(x['device'])		

        # # connects to SQLite database. File is named "sensordata.db" without the quotes
        # # WARNING: your database file should be in the same directory of the app.py file or have the correct path
        # #conn=sqlite3.connect('ncs.db')
        # #c=conn.cursor()

        # #c.execute("INSERT INTO ncsreadings(device,message,currentdate,currentime,bed) VALUES(?,?,date('now'),?,?)",(x['device'], x['message'],a,x['bed']))

        # #conn.commit()
        # #conn.close()


# mqttc=mqtt.Client()
# mqttc.on_connect = on_connect
# mqttc.on_message = on_message
# mqttc.connect("localhost",1883,60)
# mqttc.loop_start()

#@socketio.on('connect')
@socketio.on('connect')                                                         
# def connect():                                                                  
    # global thread                                                               
    # if thread is None:                                                          
        # thread = socketio.start_background_task(target=background_thread)       


#@socketio.on('connect')
#login part
#it will come after hitting base url
#contains two table-log and log_archive

@app.route('/',methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        a=request.form['username']
        b=request.form['password']
        #department=request.form['department']
        con = sqlite3.connect("ncs.db")
        cur = con.cursor()
        query=cur.execute('SELECT * FROM log WHERE username=(?) AND password=(?)',(a,b))
        results=query.fetchall()




        #result = cur.execute('INSERT INTO log (username,password) VALUES(?,?)', (request.form['username'], request.form['password']))
        #con.commit()
        #if request.form['username'] != results[0][1] or request.form['password'] != results[0][2] :
        if len(results)==0:
            error = 'Invalid Credentials. Please try again.'
        else:
			session['logged_in']=True
			print('sakib')
			q=cur.execute('INSERT INTO log_archive (uname,pword,entry_time) VALUES(?,?,current_timestamp)',(a,b))
			con.commit()
			logout_id=cur.execute('SELECT max(id) FROM log_archive WHERE uname=(?) AND pword=(?)',(a,b))
			array_id=cur.fetchall()
			id=array_id[0][0]
			print(id)
			session['username']=a
			session['password']=b
			session['id']=id
			query_type=cur.execute('SELECT user_Type,department FROM log WHERE username=(?) AND password=(?)',(a,b))
			type=cur.fetchall()
			print(type[0][0])
			print(type[0][1])
			#print(type(type[0][1]))
			#global topic_login 
		#	topic_login = type[0][1]
		#	print(topic_login)
			#print('print type' +type)
			session['topic_login'] = type[0][1]
			print('background ',session['topic_login'])
			#print('session'+session['topic_login'])
            #con = sqlite3.connect("ncs.db")
            #cur=con.cursor()
			login_time = cur.execute('UPDATE log SET login_time=current_timestamp WHERE username=(?) AND password=(?)',(a,b))
			con.commit()
			session['view'] = type[0][0] 
			print(session['view'])
			return redirect(url_for('admin_home'))
			# mqttc=mqtt.Client()
			# mqttc.on_connect = on_connect
			# mqttc.on_message = on_message
			# mqttc.connect("localhost",1883,60)
			#mqttc.loop_start()
			# if(type[0][0]=="ADMIN"):
				# return redirect(url_for('admin_home'))
			# elif(type[0][0]!="ADMIN" and type[0][1]=="ccu"):
				# return redirect(url_for('icu_user'))
			# elif(type[0][0]!="ADMIN" and type[0][1]=="mwd"):
				# return redirect(url_for('ccu_user'))

    return render_template('home.html', error=error)

   

#@app.route("/index")
#def index():
#    return render_template('realtime.html',async_mode=socketio.async_mode) 


@app.route('/test')
def test():
	return render_template('audio.html')

#admin page
#it will come up if an admin logs in
@app.route('/admin_home')
@login_required
def admin_home():
	print(session['view'])
	conn=sqlite3.connect('ncs.db')
	conn.row_factory = dict_factory
	c=conn.cursor()
	c.execute("SELECT * FROM ncsreadings ORDER BY id DESC LIMIT 10")
	l=conn.cursor()
	l.execute("SELECT * FROM log_archive ORDER BY id DESC LIMIT 10")
	readings = c.fetchall()
	logs=l.fetchall()
	messages = session.get('message',None)
	session.pop('message',None)
	response=session.get('response',None)
	session.pop('response',None)
	return render_template('admin.html',async_mode=socketio.async_mode,readings=readings,logs=logs,messages=messages,response=response, view = session['view'])

    
#icu user page
#it will come up if an icu user logs in 
@app.route('/icu_user')
@login_required
def icu_user():
    return render_template('icu_user.html',async_mode=socketio.async_mode)

    
#ccu user page
#it will come up if a ccu user logs in
@app.route('/ccu_user')
@login_required
def ccu_user():
    return render_template('ccu_user.html',async_mode=socketio.async_mode)

#adding user part 
#only admin can do this 
@app.route('/addUser',methods=['GET', 'POST'])
@login_required
def addUser():
    error = None
    if request.method == 'POST':
        u = request.form['name']
        print(u)
        p = request.form['password']
        email=request.form['email']
        print(email)
        usertype=request.form['user_type']
        department=request.form['dep']
        con1 = sqlite3.connect("ncs.db")
        cur1 = con1.cursor()
        add_user=cur1.execute('INSERT INTO log (username,password,user_type,department) VALUES(?,?,?,?)',(u,p,usertype,department))
        con1.commit()
        gmail_user ="sakibm2510@gmail.com"
        gmail_pwd = "Sakib1004015"
        FROM = gmail_user
        TO = email
        SUBJECT = "Username and Password"
        TEXT = "Your Username is: "+ u + " And Password is: "+p
        message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
            """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login("sakibm2510@gmail.com", "Sakib1004015")
            #msg = "Your Username is: "+u+ "And Password is: "+p
            server.sendmail("sakibm2510@gmail.com",email, message)
            server.close()
            print('successfully sent the mail')
        except:
            print("failed to send mail")

    return ('', 204)    
#admin can delete user from here    
@app.route('/deleteUser',methods=['GET', 'POST'])
def delete():
    messages = None
    if request.method == 'POST':
        user_name=request.form['user_name']
        con2 = sqlite3.connect("ncs.db")
        cur2 = con2.cursor()
    cur2.execute('SELECT username FROM log WHERE username=(?)',(user_name,))
    user_check=cur2.fetchall()
    if len(user_check)==0:
        messages='User Don exist, please try again'
        session['message']=messages
    else:
        messages="User has deleted"
        session['message']=messages
        delete_user = cur2.execute('DELETE FROM log WHERE username=(?)',(user_name,))
        con2.commit()

    return redirect(url_for('admin_home'))
    

#showing the database record    
#this part is not necessary
#just for testing
@app.route('/record') 
@login_required
def sakib():
   # connects to SQLite database. File is named "sensordata.db" without the quotes
   # WARNING: your database file should be in the same directory of the app.py file or have the correct path
   conn=sqlite3.connect('ncs.db')
   conn.row_factory = dict_factory
   c=conn.cursor()
   c.execute("SELECT * FROM ncsreadings ORDER BY id DESC LIMIT 10")
   readings = c.fetchall()
   #print(readings)
   return render_template('record.html', readings=readings) 
    
#for mapping portion
#mapping is between device against bed and floor    
@app.route('/map',methods=['GET', 'POST'])
def map():
    if request.method=='POST':
		a=request.form['device']
        #print(a)
		b=request.form['bed']
		c=request.form['submit']
		print(a,b) 
		print(c)
		#print c
		con = sqlite3.connect("ncs.db")
		cur = con.cursor()
		#print(c)
		if c == 'Update':
			result = cur.execute('UPDATE map SET dept = ?,bed=? WHERE device=?',( request.form['department'],request.form['bed'],request.form['device']))
			con.commit()
			print 'updated'
		if c=='Connect':
			result=cur.execute('INSERT INTO map (device,bed,dept) VALUES(?,?,?)', (request.form['device'],request.form['bed'],request.form['department']))
			con.commit()
			print 'insert' 
    return ('',204)
    
@app.route('/show')
@login_required
def show():
    con = sqlite3.connect("ncs.db")
    cur = con.cursor()
    query = cur.execute('SELECT * FROM map')
    return render_template('show.html',items=query.fetchall())
    
#logout part    
@app.route('/logout')
@login_required
def logout():
	print('logout portion')
	a=session.get('username',None)
	b=session.get('password',None)
	c=session.get('id',None)
	con = sqlite3.connect("ncs.db")
	cur = con.cursor()
	logout_time = cur.execute('UPDATE log SET logout_time=current_timestamp WHERE username=(?) AND password=(?)',(a,b))
	con.commit()
	out_time=cur.execute('UPDATE log_archive SET out_time=current_timestamp WHERE uname=(?) AND pword=(?) AND id=(?)',(a,b,c))
	con.commit()
	session.pop('logged_in',None)
	session.clear()
	return redirect(url_for('login'))       
    
@app.route('/updateUser',methods=['GET', 'POST'])
def update():
    response = None
    if request.method == 'POST':
        user_name=request.form['user_name']
        dept=request.form['dep']
        con2 = sqlite3.connect("ncs.db")
        cur2 = con2.cursor()
	cur2.execute('SELECT username FROM log WHERE username=(?)', (user_name,))
        user_check = cur2.fetchall()
	if len(user_check)==0:
            response='User Do not exist, please try again'
	    session['response']=response
	else:	
	    response='User has updated'
	    session['response']=response
            cur2.execute('UPDATE log SET department=(?) WHERE username=(?)',(dept,user_name,))
            con2.commit()

    return redirect(url_for('admin_home'))
    

    
mqttc=mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.on_publish = on_publish
mqttc.connect("localhost",1883,60)
mqttc.loop_start()   





if __name__ == "__main__":
#	db.create_all()
	app.run(host='0.0.0.0', port=8080,threaded=True, debug=True)
  # app.run(threaded =True)
	socketio.run(app, debug=True)
