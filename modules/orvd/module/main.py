from flask import Flask, request, jsonify
import requests
import random 

app = Flask(__name__)

class Orvd():
    def __init__(self):
        pass

    def route_check(self):
        data = request.get_json()
        route = list(data.get("route"))
        #result = False if (random.randint(0, 3) == 0) else True
        result = True
        return jsonify({"route_approve": result}), 200

    def log_boat_pos(self):
        data = request.get_json()
        boat_pos = data.get("current_pos")
        print(f"Boat current pos log: {boat_pos}")
        return jsonify({"status": "Boat current pos successfully logged"}), 200

orvd = Orvd()

@app.route('/route-check', methods=['POST'])
def route_check():
    return orvd.route_check()

@app.route('/log-boat-pos', methods=['POST'])
def log_boat_pos():
    return orvd.log_boat_pos()

def start_web():
    app.run(host='0.0.0.0', port=8000, threaded=True)
    