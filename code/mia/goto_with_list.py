# -*- coding: utf-8 -*-
"""
goto_with_list.py — Mission « goto » multi-points (Livrable MIA, semestre 1)

Projet Drone DJI F450 — Groupe III — UCAC-ICAM, Bachelor Général Engineering (2023-2024)
Responsable MIA : NZABA Aubain

Crée un drone virtuel (SITL ArduCopter) à une adresse ou à des coordonnées GPS
choisies, puis lui fait survoler une liste de points (adresses géocodées via
OpenStreetMap ou coordonnées saisies), avec une vitesse par point, avant un
retour au point de départ (RTL) et l'atterrissage.

Dépend de quadcopter_simulator.py (fourni par l'ICAM) dans le même dossier.
Lancement :  python goto_with_list.py
Visualisation : Mission Planner connecté en TCP sur 127.0.0.1:5763.
"""

# Authors & MIA Responsable: the all team & Aubain Ramath NZABA
# Drone Project Team III
# 1st semester

#for geting adresse
from __future__ import print_function
import geocoder
from builtins import *

#for vehicule and arming
from quadcopter_simulator import init_vehicle
import time
from dronekit import VehicleMode, LocationGlobalRelative
from geopy.distance import geodesic

#presentationpip
print("\nThis programme will allow you to create virtual drone wherever you on the earth"
      "\nand makes it fly over wanted addresses before returning to launch.")

start_point = []

choiceIsValid=False

while not choiceIsValid :

    print("Choose an option:\n"
        "Press 1 to enter adresses\n"
        "Press 2 to enter gps coordinates manualy")
    choice=int(input(": "))

    if choice == 1:
        choiceIsValid=True

        #create a boolean containing False value
        addressIsValid = False

        #loop until the boolean is not False anymore 
        while not addressIsValid :
            
            #print some text in the console
            print("\nPlease enter a starting address for your virtual drone :")
            
            #asks the user to enter the address
            textAddress = input() #for example ICAM Bretagne, Vannes, France
            
            #asks OpenStreetMap to geocode the address
            g = geocoder.osm(textAddress)

            #assign True/False regarding the previous operation's result
            addressIsValid = g.ok

            #if the address has been geocoded
            if addressIsValid :
                print("the address is valid")
                print("latitude" , g.lat)
                print("longitude" , g.lng)

                #asking for confirmation
                c=input("Do you agree this address (Y/n)? : ")
                if c=="Y":
                    print("Confirmed address")

                    start_point.append(g.lat)
                    start_point.append(g.lng)

                else:
                    print("Uncomfirmed address")
                    # Reset the addressIsValid flag to False to re-enter the loop
                    addressIsValid = False

            #if the address has NOT been geocoded
            else:
                print("the address is not valid")

    elif choice == 2 :
        choiceIsValid=True
        print("Set star point coordinates")
        la=float(input("Set latitude: "))
        lo=float(input("Set longitude: "))  

        c=input("Do you agree this address (Y/n)? : ")
        if c=="Y":
            print("Confirmed address")
            start_point.append(la)
            start_point.append(lo)

        else:
            print("Uncomfirmed address")
            # Reset the addressIsValid flag to False to re-enter the loop
            addressIsValid = False

    else:
        print("Invalid choice")


print( "\nStarting simulator...")

# Connect to the Vehicle, located at the asked coordinates ( start_point[0], start_point[1])
vehicle = init_vehicle(start_point[0], start_point[1])
print("Drone created")

# ask the user the number of address he/she want to visit 
n=int(input("\nHow many places do you want to visite ? \n"))

AddressList=[]
latitudes=[]
longitudes=[]
speed=[]
r=1

#ask adresses 
for loop in range(n):
    if choice==1 :
        #create a boolean containing False value
        addressIsValid = False

        #loop until the boolean is not False anymore 
        while not addressIsValid :
        
            #print some text in the console
            print("\nPlease enter a valid address")
        
            #asks the user to enter the address
            textAddress = input() #for example ICAM Bretagne, Vannes, France
        
            #asks OpenStreetMap to geocode the address
            g = geocoder.osm(textAddress)

            #assign True/False regarding the previous operation's result
            addressIsValid = g.ok

            #if the address has been geocoded
            if addressIsValid :
                print("the address is valid")
                print("latitude" , g.lat)
                print("longitude" , g.lng)

                distance=geodesic(start_point, (g.lat, g.lng)).meters
                print(f"It's at around {round(distance)} meters from your launch")

                #asking for comfirmation
                c=(input("Do you agree to go there (Y/n)? : "))
                if c=="Y":
                    print("Confirmed address")

                    #add the wanted values to lists
                    AddressList.append(textAddress)
                    latitudes.append(g.lat)
                    longitudes.append(g.lng)

                    speed.append(int(input("Please set speed between 1~15 (m/s): ")))

                else:
                    print("Uncomfirmed address")
                    # Reset the addressIsValid flag to False to re-enter the loop
                    addressIsValid = False

            #if the address has NOT been geocoded
            else:
                print("the address is not valid")

    elif choice==2:
        print(f"Set coordinates for point{r}")
        la=float(input("Set latitude: "))
        lo=float(input("Set longitude: "))  

        c=input("Do you agree this address (Y/n)? : ")
        if c=="Y":
            print("Confirmed address")

            AddressList.append(f"point{r}")
            latitudes.append(la)
            longitudes.append(lo)

            speed.append(int(input("Please set speed between 1~15 (m/s): ")))
            r=r+1

# Start the drone
def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("\nBasic pre-arm checks")
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

arm_and_takeoff(10)

print("Set default/target airspeed to 180 \n")
vehicle.airspeed = 180

#send the drone
r=0
marge = 0.00001

for loop in range(n):
    print(f"Going towards {AddressList[r]} (groundspeed set to {speed[r]}m/s) ... ")
    point = LocationGlobalRelative( latitudes[r], longitudes[r], 20)
    vehicle.simple_goto(point, groundspeed=speed[r])
    
    #Set a waiting time as long as the drone have not joined the wanted coordinates
    while abs(latitudes[r] - vehicle.location.global_frame.lat) >= marge and abs(longitudes[r] - vehicle.location.global_frame.lon) >= marge:
        distance=geodesic((vehicle.location.global_frame.lat, vehicle.location.global_frame.lon), (latitudes[r], longitudes[r])).meters
        print(f"Around {round(distance)} meters left to {AddressList[r]}, Altitude: {vehicle.location.global_relative_frame.alt}")
        time.sleep(5)

    print(f"{AddressList[r]} joined \n")
    r=r+1

#bring back the drone
print("Returning to Launch")
vehicle.mode = VehicleMode("RTL")

#Set a waiting time as long as the drone have not joined the wanted coordinates
while abs(start_point[0] - vehicle.location.global_frame.lat) >= marge and abs(start_point[1] - vehicle.location.global_frame.lon) >= marge :
    distance=geodesic((vehicle.location.global_frame.lat, vehicle.location.global_frame.lon), (start_point[0], start_point[1])).meters
    print(f"Around {round(distance)} meters left to Home, Altitude: {vehicle.location.global_relative_frame.alt}")
    time.sleep(5)
print("Home joined")


print("\nLanding")
while vehicle.location.global_relative_frame.alt >= 0.8:
    print(f"Altitude: {vehicle.location.global_relative_frame.alt}")
    time.sleep(2)
print("The drone have landed")
time.sleep(5)

# Close vehicle object before exiting script
print("\nClose vehicle object")
vehicle.close()

# Authors & MIA Responsable: The all team & Aubain Ramath NZABA
# Drone Project Team III