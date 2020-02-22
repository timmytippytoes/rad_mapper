import simplekml
from gps import *
import numbers
import RPi.GPIO as GPIO
import time
from argparse import ArgumentParser
import simplekml

kml = simplekml.Kml(open=1)# setup a kml for map data

# set up args received from teh cmd line
parser = ArgumentParser()
parser.add_argument("-f", "--file", dest="filename",
                    help="write report to FILE", metavar="FILE", default="rads.txt")
parser.add_argument("-k", "--kml", dest="kml",
                    help="write report to kml", default="overlay.kml")
parser.add_argument("-p", "--print", dest="printIt",
                    help="print text to screen", metavar="PRINT", default=False)
parser.add_argument("-i", "--increment", dest="increment",
                    help="the number of counts collected for averaging", metavar="INC", default=20)
args = parser.parse_args()

gps_data = "None"
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN) # plugged into pin 5
hits = 0
file = open(args.filename,"w") # open raw datafile to write to
def incrementIt(channel):
    # increment hits if GPIO rise detected
    global hits
    hits += 1

GPIO.add_event_detect(5,GPIO.RISING, callback=incrementIt) # setup to check for rising on pin 5 and call method when true
print ("'ctrl c' to exit")
# print info if arg is set
if args.printIt:
    print ("lat/lon/hits ")
gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)
try:
    while True:
        start = time.time()
        # get gps data
        report = gpsd.next()
        if report['class'] == 'TPV':
            gps_data = [getattr(report,'lat', 0.0),getattr(report, 'lon', 0.0)]

        # print data every .5 seconds
        if (time.time() - start >= .5):
            start = time.time()
            # print data if arg is set
            if args.printIt:
                print (str(gps_data[0]) + " " + str(gps_data[1]) + " " + str(hits))  # print gps data and hits
            # check if gps data is being received
            if isinstance(gps_data[0], numbers.REAL):
                file.write(str(gps_data[0]) + " " + str(gps_data[1]) + " " + str(hits) + "\n") # write raw gps and hits data
            hits = 0 # reset hit counter
except KeyboardInterrupt:
    file.close()# close raw data file

    # open raw data file and read in each line and store as a list
    file = open(args.filename, "r")
    lines = file.readlines()
    file.close()

    increment = args.increment # averaging increment

    # for look to cycle through all lines in chunks (set of data points) of size increment
    # ex: increment = 20
    # cycle through 20 lines of data at a time until the end of the data (however long it is) is reached
    for i in range(0, len(lines), increment):
        denom = 0 # denominator for averaging
        avg = 0 # average for this chunk
        # go through each line in this chunk
        for line in lines[i:i+increment]:
            # if there is data then use it for averaging of hits received
            if line is not None and not "None" in line:
                line_list = line.split()# break up the line into words
                avg += int(line_list[2])# add hit count to average
                denom += 1 # counts this as a valid bit of data
        if denom != 0:# check if we have any valid hit data
            avg /= denom # divide avg by number of valid hit data points
        else:
            avg /= increment # prevent div by 0
        coords = []
        level = 0
        # go through each line in this chunk(set of data points) again
        for line in lines[i:i+increment]:
            if line is not None and "None" not in line:
                line_list = line.split()
                # if there is valid gps data then add it to our set of coordinates, this is kind of redundant but
                # I just wanted to make sure nothing would mess up my data
                if float(line_list[0]) != 0.0 and float(line_list[1]) != 0.0:
                    coords.append((float(line_list[1]),float(line_list[0])))

                # This all decides what importance to assign each chunk(set of data points)
                # importance is assigned on how much higher each value is above the average for this chunk
                # Ex: if a hit count is 90 but the the average is 50 for the chunk then the the importance level will be
                #     level 2.  This is because 90/50 = 1.8 which is greater than 1.5 * avg but less than 2 * avg
                # The whole point of this is to find jumps in rads above the background.
                if float(line_list[2]) > avg*5 and float(line_list[0]) != 0.0 and float(line_list[1]) != 0.0:
                    if level == 0:# check if level has not been set yet (there already exists a line)
                        line_string = kml.newlinestring(name="Alert") # create new generic line in the kml
                    if level < 5:# if set then check if the current level for the chunk is lower, if it is then up it
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

        # the following builds our lines based on importance level and color codes them
        if level == 5:
            line_string.name = "Really High Rads"
            line_string.style.linestyle.width = 5
            line_string.coords = coords
            line_string.style.linestyle.color = simplekml.Color.red
        elif level == 4:
            line_string.name = "High Rads"
            line_string.style.linestyle.width = 5
            line_string.coords = coords
            line_string.style.linestyle.color = simplekml.Color.orange
        elif level == 3:
            line_string.name = "Med Rads"
            line_string.style.linestyle.width = 5
            line_string.coords = coords
            line_string.style.linestyle.color = simplekml.Color.yellow
        elif level == 2:
            line_string.name = "Moderate Rads"
            line_string.style.linestyle.width = 5
            line_string.coords = coords
            line_string.style.linestyle.color = simplekml.Color.green
        elif level == 1:
            line_string.name = "Lil Extra Rads"
            line_string.style.linestyle.width = 5
            line_string.coords = coords
            line_string.style.linestyle.color = simplekml.Color.blue
    kml.save(args.kml) # saves the kml file to specified name defined in args
    print ("All done")
except Exception as e:
    print ("Something Failed " + e.message) # looks for errors