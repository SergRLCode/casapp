from passlib.hash import pbkdf2_sha256 as sha256
from flask import Flask, jsonify, request
from datetime import datetime as dt
import serial, time as t
import redis

redis = redis.Redis(host='localhost', port=6379)
server = Flask(__name__)
# arduino = serial.Serial("/dev/ttyACM0", 9600)
t.sleep(1)

spotlightData = {
	"status": "",
	"hourStart": "",
	"hourEnd": "",
	"timeElapsed": ""
}

userData = {
	"username": "",
	"password": ""
}

def strTodate(theDate):
	return dt.strptime(theDate, '%Y-%m-%d %H:%M:%S.%f')

def getTotalTimeSwitchedOn(spotlight):
	# hours, minutes, seconds = "", "", "" <- in case when all the variables will contain diferent value
	hours = minutes = seconds = ""
	_spotlight = redis.hgetall(spotlight)
	_spotlight = {key.decode('utf-8'): value.decode('utf-8') for (key, value) in _spotlight.items()}
	timeElapsed = (strTodate(_spotlight['hourEnd'])-strTodate(_spotlight['hourStart'])).seconds
	hours = int(timeElapsed/3600)
	minutes = int((timeElapsed%3600)/60)
	seconds = (timeElapsed%3600)%60
	return("Tiempo encendido: {} horas, {} minutos, {} segundos".format(hours, minutes, seconds))

@server.route('/spotlight/<room>', methods=['POST'])
def spotlight_route(room):
	if (request.method == 'POST'):
		data = request.get_json()
		params = ('living_room', 'kitchen', 'bathroom', 'bedroom')
		idents = ('1', '2', '3', '4')
		for x in range(0,len(params)):
			if room == params[x]:
				room = idents[x]
		if data["status"] == "on":
			spotlightData['status'] = 'on'
			spotlightData['hourStart'] = '{}'.format(dt.now())
			redis.hmset(room, spotlightData)
			instruction = "{}{}".format(room, data["status"])
			# arduino.write(instruction.encode('utf-8'))
		elif data["status"] == "off":
			spotlightData['status'] = 'off'
			spotlightData['hourEnd'] = '{}'.format(dt.now())
			redis.hmset(room, spotlightData)
			spotlightData['timeElapsed'] = getTotalTimeSwitchedOn(room)
			redis.hmset(room, spotlightData)
			instruction = "{}{}".format(room, data["status"])
			# arduino.write(instruction.encode('utf-8'))
		objectToSend = {
			"status": data['status'], 
			"timeElapsed": redis.hget(room, 'timeElapsed').decode('utf-8') if data["status"] == "off" else ""
		}
		return jsonify(objectToSend)

@server.route('/login', methods=['POST'])
def login_user():
	if(request.method == 'POST'):
		data = request.get_json()
		user = redis.hgetall(data['username'])
		dataDecoded = {key.decode('utf-8'): value.decode('utf-8') for (key, value) in user.items()}
		spotlights = dataDecoded['spotlights'].replace(" ", "").split(',')
		spotlightsAndStatus = []
		for x in range(0, len(spotlights)):
			spotlightsAndStatus.append(spotlights[x])
			spotlightsAndStatus.append(redis.hget(str(x+1), 'status').decode('utf-8'))
		if sha256.verify(data['password'], dataDecoded['password']):
			return jsonify({'message': '{}'.format(data['username']), 'spotlightsAndStatus': spotlightsAndStatus}), 200
		else:
			return jsonify({'message': 'Wrong access'}), 401

@server.route('/addUpdate', methods=['POST'])
def add_update():
	if(request.method == 'POST'):
		data = request.get_json()
		spotlights = data['spotlights']
		data['spotlights'] = str(spotlights).strip('[]')
		for value in ('password', 'username', 'spotlights'):
			userData[value] = data[value] if value!='password' else sha256.hash(data[value])
		redis.hmset(data['username'], userData)
		return jsonify({'message': 'Saved!'})

if __name__ == '__main__':
	server.run(debug=True, port=5000)
	# arduino.close()
