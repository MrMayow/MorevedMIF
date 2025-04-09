from flask import Flask, render_template, request, jsonify
import requests
import random

app = Flask(__name__)

BOAT_START_URL = "http://boat:8000/start_boat"
ORVD_ROUTE_CHECK_URL = "http://orvd:8000/route-check"

class Ckob:
    def __init__(self):
        pass

    def send_route_to_boat(self, route):
        try:
            payload = {"route": route}
            response = requests.post(BOAT_START_URL, json=payload)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}


    def request_route_approve(self, route):
        try:
            print(f"Request root approve from ORVD")
            payload = {"route": route}
            response = requests.post(ORVD_ROUTE_CHECK_URL, json=payload)
            json_data = response.json()
            return json_data.get("route_approve")
        except Exception as e:
            return {"status": "error", "message": str(e)}


ckob = Ckob()

@app.route('/log-boat-data', methods=['POST'])
def log_boat_data():
    data = request.get_json()
    boat_pos = data.get("current_pos")
    sensors_data = data.get("sensors_data")
    print(f"Boat data log: boat_pos: {boat_pos}, sensors_data: {sensors_data}")
    return jsonify({"status": "Boat data successfully logged"}), 200


current_coords = {"lat": 55.751244, "lon": 37.618423}
@app.route("/")
def index():
    return render_template("index.html", coords=current_coords)


@app.route("/update_coords", methods=["POST"])
def update_coords():
    data = request.get_json()
    current_coords["lat"] = data.get("lat")
    current_coords["lon"] = data.get("lon")
    return jsonify(status="updated")


@app.route("/get_coords")
def get_coords():
    return jsonify(current_coords)


@app.route("/submit_route", methods=["POST"])
def submit_data():
    data = request.get_json()
    route = list(data.get("route"))
    print(route)
    root_approve = ckob.request_route_approve(route)
    if not root_approve:
        return jsonify({"status": "Route not approved"})
    result = ckob.send_route_to_boat(route)
    return jsonify(result), 200


def start_web():
    app.run(host='0.0.0.0', port=8000, threaded=True)
    