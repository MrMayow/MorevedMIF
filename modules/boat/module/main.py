from flask import Flask, request, jsonify
import time
import threading
import random
import requests

app = Flask(__name__)

CKOB_BOAT_DATA_LOG_URL = "http://ckob:8000/log-boat-data"
ORVD_BOAT_POS_LOG_URL = "http://orvd:8000/log-boat-pos"

CKOB_UPDATE_COORDS = "http://ckob:8000/update_coords"

class Point:
    def __init__(self, uid, x, y):
        self.x = x
        self.y = y
        self.uid = uid

    def __repr__(self):
        return f"Point(uid={self.uid}, x={self.x}, y={self.y})"
    
    def to_dict(self):
        return {"uid": self.uid, "x": self.x, "y": self.y}


class Boat:
    def __init__(self, coordinates_array):
        self.current_point = Point(0, 0, 0)
        self.is_moving = False
        self.route = self.format_route(coordinates_array)
        

    def format_route(self, coordinates_array):
        final_route = [self.current_point]
        for i, v in enumerate(coordinates_array):
            final_route.append(Point(i + 1, v[0], v[1]))
        return final_route

    def start_moving(self):
        print(f"Boat start moving with route: {self.route}")
        self.is_moving = True
        while self.is_moving and self.current_point.uid < len(self.route) - 1:
            current_point = self.current_point
            next_point = self.route[self.current_point.uid + 1]
            print(f"Moving from {current_point} to {next_point}")
            self.move_to_point(current_point, next_point)
            self.current_point = next_point
            self.send_data_to_ckob()
            self.send_data_to_orvd()
            time.sleep(7)
        print("Route completed!")

    def move_to_point(self, current_point, next_point):
        print(f"Calculating direction from ({current_point.x}, {current_point.y}) to ({next_point.x}, {next_point.y})")
        print(f"Arrived at ({next_point.x}, {next_point.y})")

    def get_sensors_data(self):
        radiation = random.randint(0, 4)
        ph = random.randint(0, 14)
        return {"radiation": radiation, "ph": ph}

    def send_data_to_ckob(self):
        try:
            pos_data = self.current_point.to_dict()  # Преобразуем в словарь
            sensors_data = self.get_sensors_data()
            print(f"Send current boat data to CKOB: Pos: {pos_data}, Sensors: {sensors_data}")
            payload = {"current_pos": pos_data, "sensors_data": sensors_data}
            response = requests.post(CKOB_BOAT_DATA_LOG_URL, json=payload)
            json_data_1 = response.json()

            payload = {"lat": self.current_point.x, "lon": self.current_point.y}
            response = requests.post(CKOB_UPDATE_COORDS, json=payload)
            json_data_2 = response.json()
              
        except Exception as e:
            return {"status": "error", "message": str(e)}
        
    def send_data_to_orvd(self):
        try:
            pos_data = self.current_point.to_dict()  # Преобразуем в словарь
            print(f"Send current boat pos to ORVD: {pos_data}")
            payload = {"current_pos": pos_data}  # Пример без использования jsonify
            response = requests.post(ORVD_BOAT_POS_LOG_URL, json=payload)
            json_data = response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

@app.route('/start_boat', methods=['POST'])
def start():
    data = request.get_json()
    route = list(data.get("route"))
    print(route)
    boat = Boat(route)
    threading.Thread(target=boat.start_moving).start()
    return jsonify({"status": "Boat started moving"}), 200


def start_web():
    app.run(host='0.0.0.0', port=8000, threaded=True)
