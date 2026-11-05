#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import geocoder
from builtins import *

#create a boolean containing False value
addressIsValid = False

#loop until the boolean is not False anymore 
while not addressIsValid :
    
    print("Please enter a valid address")
    
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

    #if the address has NOT been geocoded
    else:
        print("the address is not valid")