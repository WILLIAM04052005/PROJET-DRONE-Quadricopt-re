# -*- coding: utf-8 -*-
"""
follow_me.py — Mode « Follow me » (Livrable MIA, semestre 2)

Projet Drone DJI F450 — Groupe III — UCAC-ICAM, Bachelor Général Engineering (2023-2024)
Responsable MIA : NZABA Aubain

Le smartphone (application MIT App Inventor « Send_location ») envoie sa
position GPS et une action (go / rlt / none) à un serveur web de l'ICAM.
Ce script interroge ce serveur toutes les secondes, fait décoller le drone
puis le dirige vers chaque nouvelle position reçue. L'action « rlt »
déclenche le retour au point de départ (RTL).

Format du fichier lu sur le serveur :  "<latitude> <longitude> <action>"

Lancement (simulation SITL démarrée automatiquement) :  python follow_me.py
Lancement sur un vrai drone :  python follow_me.py --connect <chaine_de_connexion>
"""


from __future__ import print_function
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative


# Create vairable to store the latitude, longitude and action
latitudes = []
longitudes = []
actions = [""]
last_array = [0,0,""]
change = False

def request():

    # Ask information from op-dev server
    import ssl
    context = ssl._create_unverified_context()
    import urllib.request
    
    try:

        url = "https://op-dev.icam.fr/~icam/dawn_iii.txt"
        response = urllib.request.urlopen(url, context=context)
        data = response.read()
        global array, last_array, change
        array = data.decode('utf-8').split()

        if array != last_array :
            print(array)

            # Store the latitude and longitude in the variables
            if array[2] == "go" and (last_array[0] != array[0] or last_array[1] != array[1]) :
                latitudes.append(float(array[0]))
                longitudes.append(float(array[1]))
                change = True
            
            else:
                change = False
            
            if last_array[2] != array[2] :
                actions.append(str(array[2]))
        
        else:
            change = False
        
        last_array = array

    except urllib.error.URLError as e:
    
        print("URL Error:", e.reason)
        last_array = [0,0,""]
        array = [0,0,""]
        return


def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto
    #  (otherwise the command after Vehicle.simple_takeoff will execute
    #   immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

# Set up option parsing to get connection string
import argparse
parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
parser.add_argument('--connect',
                    help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
sitl = None


# Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    request()
    sitl = dronekit_sitl.start_default(float(array[0]), float(array[1]))
    connection_string = sitl.connection_string()


# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)


arm_and_takeoff(3)

print("Set default/target airspeed to 3")
vehicle.airspeed = 3

t = 0

def check_distance():
    from geopy.distance import geodesic
    global distance, t          
    distance = geodesic((vehicle.location.global_frame.lat, vehicle.location.global_frame.lon), (latitudes[t], longitudes[t])).meters
    return distance

# Follow the user
while True:
    request()

    if actions[len(actions)-1] == "go" and change:

        print("Going towards target (groundspeed set to 1 m/s) ...")
        target = LocationGlobalRelative(latitudes[t], longitudes[t], 3)
        vehicle.simple_goto(target, groundspeed=1)
    
        #Set a waiting time as long as the drone have not joined the wanted coordinates
        while actions[len(actions) - 1] == "go" and check_distance() > 0.2 :
            
            request()
            print(f'Around {distance} meters left to Target, Altitude: {vehicle.location.global_relative_frame.alt}')
            time.sleep(1)
                
        print("Target joined")
        
        if t < len(latitudes):
            t = t + 1

    elif actions[len(actions) - 1] == "rlt":
        print("Returning to Launch")
        vehicle.mode = VehicleMode("RTL")

        while vehicle.location.global_relative_frame.alt > 0:
            print(" Altitude: ", vehicle.location.global_relative_frame.alt)
            time.sleep(1)

        # Close vehicle object before exiting script
        print("Close vehicle object")
        vehicle.close()

        # Shut down simulator if it was started.
        if sitl:
            sitl.stop()
        
        break