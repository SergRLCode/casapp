from flask import Flask, jsonify, request
from pymongo import MongoClient
from datetime import datetime
import serial, time as t

mongo = MongoClient()
spotlights = mongo.casApp.spotlight

server = Flask(__name__)
arduino = serial.Serial("/dev/ttyACM0", 9600)
t.sleep(2)

def getTotalTimeSwitchedOn(spotlight):
    # hours, minutes, seconds = "", "", "" <- in case when all the variables will contain diferent value
    hours = minutes = seconds = "" 
    _spotlight = spotlights.find_one({"number": spotlight})
    timeElapsed = (_spotlight['hourEnd']-_spotlight['hourStart']).seconds
    hours = int(timeElapsed/3600)
    minutes = int((timeElapsed%3600)/60)
    seconds = (timeElapsed%3600)%60
    return("Tiempo encendido: {} horas, {} minutos, {} segundos".format(hours, minutes, seconds))
# curl -d '{"status": "on"}' -H 'Content-Type: application/json' http://localhost:5000/spotlight/one --> para hacer los POST ggg
@server.route('/spotlight/<room>', methods=['POST'])
def spotlight_route(room):
    if (request.method == 'POST'):
        data = request.get_json()
        _spotlight = spotlights.find_one({"number": room})
        if data["status"] == "on":
            spotlights.update({"number": room},{"$set":{"status": "on", "hourStart": datetime.now()}})
            instruction = "{}_{}".format(room, data["status"])
            arduino.write(instruction.encode('utf-8'))
        elif data["status"] == "off":
            spotlights.update({"number": room},{"$set":{"status": "off", "hourEnd": datetime.now()}})      
            instruction = "{}_{}".format(room, data["status"])
            spotlights.update({"number": room},{"$set":{"timeElapsed":getTotalTimeSwitchedOn(room)}})
            arduino.write(instruction.encode('utf-8')) 
        return jsonify(data)

if __name__ == '__main__':
    server.run(debug=True)
    arduino.close()