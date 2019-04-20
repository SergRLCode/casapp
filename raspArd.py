from flask import Flask, jsonify, request
from datetime import datetime as dt
import serial, time as t
import redis

redis = redis.Redis(host='localhost', port=6379)
server = Flask(__name__)
arduino = serial.Serial("/dev/ttyACM0", 9600)
t.sleep(1)

spotlightData = {
	"status": "",
	"hourStart": "",
	"hourEnd": "",
	"timeElapsed": ""
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
    
# curl -d '{"status": "on"}' -H 'Content-Type: application/json' http://localhost:5000/spotlight/one --> para hacer los POST ggg

@server.route('/spotlight/<room>', methods=['POST'])
def spotlight_route(room):
    if (request.method == 'POST'):
        data = request.get_json()
        if data["status"] == "on":
        		spotlightData['status'] = 'on'
        		spotlightData['hourStart'] = '{}'.format(dt.now())
        		redis.hmset(room, spotlightData)
        		instruction = "{}_{}".format(room, data["status"])
        		arduino.write(instruction.encode('utf-8'))
        elif data["status"] == "off":
        		spotlightData['status'] = 'off'
        		spotlightData['hourEnd'] = '{}'.format(dt.now())
        		redis.hmset(room, spotlightData)
        		spotlightData['timeElapsed'] = getTotalTimeSwitchedOn(room)
        		redis.hmset(room, spotlightData)
        		instruction = "{}_{}".format(room, data["status"])
        		arduino.write(instruction.encode('utf-8'))
        return jsonify(data, redis.hget(room, 'timeElapsed').decode('utf-8'))

if __name__ == '__main__':
    server.run(debug=True, host='192.168.1.67', port=5000)
    arduino.close()
