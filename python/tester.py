import simplekml
from gps import *
import numbers
import RPi.GPIO as GPIO
import time
from argparse import ArgumentParser
import simplekml
kml = simplekml.Kml(open=1)
parser = ArgumentParser()
parser.add_argument("-f", "--file", dest="filename",
                    help="write report to FILE", metavar="FILE", default="rads.txt")
parser.add_argument("-k", "--kml", dest="kml",
                    help="write report to kml", default="overlay.kml")
parser.add_argument("-p", "--print", dest="printIt",
                    help="print text to screen", metavar="PRINT", default=False)
args = parser.parse_args()
gps_data = "None"
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN)
hits = 0
file = open(args.filename,"w")
def incrementIt(channel):
    global hits
    hits += 1

GPIO.add_event_detect(5,GPIO.RISING, callback=incrementIt)
if args.printIt:# TODO: check what needs to be passed
    print ("lat/lon/hits ")
gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)
try:
    while True:
        start = time.time()
        report = gpsd.next()
        if report['class'] == 'TPV':
            gps_data = [getattr(report,'lat', 0.0),getattr(report, 'lon', 0.0)]
        if (time.time() - start >= .5):
            start = time.time()
            if args.printIt:# TODO: check what needs to be passed
                print (str(gps_data[0]) + " " + str(gps_data[1]) + " " + str(hits))
            if isinstance(gps_data[0], numbers.REAL):
                file.write(str(gps_data[0]) + " " + str(gps_data[1]) + " " + str(hits) + "\n")
            hits = 0
except KeyboardInterrupt:
    file.close()
    file = open(args.filename, "r")
    lines = file.readlines()
    file.close()
    increment = 20 #TODO: maybe make an arg
    avg = 0
    for i in range(0, len(lines), increment):
        denom = 0
        for line in lines[i:i+increment]:
            if line is not None and not "None" in line:
                line_list = line.split()
                avg += int(line_list[2])
                denom += 1
        if denom != 0:# not grabbing end hits?
            avg /= denom
        else:
            avg /= 20
        coords = []
        level = 0
        for line in lines[i:i+increment]:
            if line is not None and "None" not in line:
                line_list = line.split()
                if float(line_list[0]) != 0.0 and float(line_list[1]) != 0.0:
                    coords.append((float(line_list[1]),float(line_list[0])))
                if float(line_list[2]) > avg*5 and float(line_list[0]) != 0.0 and float(line_list[1]) != 0.0:
                    if level == 0:
                        line_string = kml.newlinestring(name="Alert")
                    if level < 5:
                        level = 5
                elif float(line_list[2]) > avg*3 and float(line_list[0]) != 0.0 and float(line_list[1]) != 0.0:
                    if level == 0:
                        line_string = kml.newlinestring(name="Alert")
                    if level < 4:
                        level = 4
                elif float(line_list[2]) > avg * 2 and float(line_list[0]) != 0.0 and float(line_list[1]) != 0.0:
                    if level == 0:
                        line_string = kml.newlinestring(name="Alert")
                    if level < 3:
                        level = 3
                elif float(line_list[2]) > avg * 1.5 and float(line_list[0]) != 0.0 and float(line_list[1]) != 0.0:
                    if level == 0:
                        line_string = kml.newlinestring(name="Alert")
                    if level < 2:
                        level = 2
                elif float(line_list[2]) > avg * 1.25 and float(line_list[0]) != 0.0 and float(line_list[1]) != 0.0:
                    if level == 0:
                        line_string = kml.newlinestring(name="Alert")
                    if level < 1:
                        level = 1
            else:
                break
        if level == 5:
            line_string.name = "Really High Rads"
            linestring.style.linestyle.width = 5
            linestring.coords = coords
            line_string.style.linestyle.color = simplekml.Color.red
        elif level == 4:
            line_string.name = "High Rads"
            linestring.style.linestyle.width = 5
            linestring.coords = coords
            line_string.style.linestyle.color = simplekml.Color.orange
        elif level == 3:
            line_string.name = "Med Rads"
            linestring.style.linestyle.width = 5
            linestring.coords = coords
            line_string.style.linestyle.color = simplekml.Color.yellow
        elif level == 2:
            line_string.name = "Moderate Rads"
            linestring.style.linestyle.width = 5
            linestring.coords = coords
            line_string.style.linestyle.color = simplekml.Color.green
        elif level == 1:
            line_string.name = "Lil Extra Rads"
            linestring.style.linestyle.width = 5
            linestring.coords = coords
            line_string.style.linestyle.color = simplekml.Color.blue
    kml.save(args.kml)
    print ("All done")
except Exception as e:
    print ("Something Failed " + e.message)