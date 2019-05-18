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
	"password": "",
	"usertype": ""
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
        if data["status"] == "on":
        	spotlightData['status'] = 'on'
        	spotlightData['hourStart'] = '{}'.format(dt.now())
        	redis.hmset(room, spotlightData)
        	instruction = "{}_{}".format(room, data["status"])
        	# arduino.write(instruction.encode('utf-8'))
        elif data["status"] == "off":
        	spotlightData['status'] = 'off'
        	spotlightData['hourEnd'] = '{}'.format(dt.now())
        	redis.hmset(room, spotlightData)
        	spotlightData['timeElapsed'] = getTotalTimeSwitchedOn(room)
        	redis.hmset(room, spotlightData)
        	instruction = "{}_{}".format(room, data["status"])
        	# arduino.write(instruction.encode('utf-8'))
        return jsonify(data, redis.hget(room, 'timeElapsed').decode('utf-8'))

@server.route('/login', methods=['POST'])
def login_user():
	if(request.method == 'POST'):
		data = request.get_json()
		user = redis.hgetall(data['username'])
		dataDecoded = {key.decode('utf-8'): value.decode('utf-8') for (key, value) in user.items()}
		if sha256.verify(data['password'], dataDecoded['password']):
			return jsonify({'message': 'Hello {}'.format(data['username'])})
		else:
			return jsonify({'message': 'Wrong access'})

@server.route('/addUpdate', methods=['POST'])
def add_update():
	if(request.method == 'POST'):
		data = request.get_json()
		for value in ('username', 'password', 'usertype'):
			userData[value] = data[value] if value!='password' else sha256.hash(data[value])
		redis.hmset(data['username'], userData)
		return jsonify({'message': 'Saved!'})

@server.route('/deleteUser/<name>', methods=['DELETE'])
def delete_user(name):
	if(request.method == 'DELETE'):
		redis.delete(name)
		return jsonify({'message': 'Borrado'})

if __name__ == '__main__':
    server.run(debug=True, port=5000)
    # arduino.close()
