import requests
import time
import subprocess
from boat.module.main import Point 

CONNECTION_ORDV_URL = 'http://localhost:8003'
CONNECTION_BOAT_URL = 'http://localhost:8001'


route = [[10 , 15] , [48 , 9] , [70 , 32] , [69 , 68] , [34 , 99]]
point_route = [Point(0,0,0)]+[Point(i+1, route[i][0], route[i][1]) for i in range(len(route))]
test_route_json = {"route" : route}


def test_container_output(app_name):
    logs = subprocess.check_output(
        ['docker-compose', 'logs', '--no-color', app_name],
        text=True
    )
    return logs


def test_fuctionality():
    
    send_route_to_ordv = requests.post(f'{CONNECTION_ORDV_URL}/route-check' , json = test_route_json)
    assert ((send_route_to_ordv.json()).get("route_approve") == True or (send_route_to_ordv.json()).get("route_approve") == False) and send_route_to_ordv.status_code == 200
    send_route_to_boat = requests.post(f'{CONNECTION_BOAT_URL}/start_boat' , json=test_route_json)
    assert send_route_to_boat.json().get("status") == "Boat started moving" and send_route_to_boat.status_code == 200

    time.sleep(25)

    ckob_logs = test_container_output('ckob')
    orvd_logs = test_container_output('orvd')
    boat_logs = test_container_output('boat')
    
    assert f"Boat start moving with route: {point_route}" in boat_logs

    for i in range(len(route) - 1):
        assert f"Moving from {point_route[i]} to {point_route[i+1]}" in boat_logs
        assert f"Calculating direction from {point_route[i].x, point_route[i].y} to {point_route[i+1].x, point_route[i+1].y}" in boat_logs
        assert f"Arrived at {point_route[i+1].x, point_route[i+1].y}" in boat_logs
        assert f"Send current boat data to CKOB: Pos: {point_route[i+1].to_dict()}, Sensors: " in boat_logs
        assert f"Send current boat pos to ORVD: {point_route[i+1].to_dict()}" in boat_logs
        assert f"Boat data log: boat_pos: {point_route[i+1].to_dict()}" in ckob_logs
        assert f"Boat current pos log: {point_route[i+1].to_dict()}" in orvd_logs
    assert 'Route completed!' in boat_logs

if __name__ == "__main__":
    test_fuctionality()


