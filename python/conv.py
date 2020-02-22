import simplekml
kml = simplekml.Kml(open=1)
file = open("work2.txt", "r")
lines = file.readlines()
file.close()
increment = 20  # TODO: maybe make an arg
avg = 0

for i in range(0, len(lines), increment):
    denom = 0
    for line in lines[i:i + increment]:
        if line is not None and not "None" in line:

            line_list = line.split()
            #print(line)
            avg += int(line_list[2])
            denom += 1
    if denom != 0:
        avg /= denom
    else:
        avg /= 20
    print("avg: " + str(avg))
    coords = []
    level = 0
    for line in lines[i:i + increment]:
        if line is not None and not "None" in line:
            line_list = line.split()
            if float(line_list[0]) != 0.0 and float(line_list[1]) != 0.0:
                coords.append((float(line_list[1]), float(line_list[0])))#+ ", " + line_list[0] + "\n")
            #print(line_list)
            if int(line_list[2]) > avg * 5 and float(line_list[0]) != 0.0 and float(line_list[1]) != 0.0:
                print("5")
                if level == 0:
                    line_string = kml.newlinestring(name="wow2")
                if level < 5:
                    level = 5
            elif int(line_list[2]) > avg * 3 and float(line_list[0]) != 0.0 and float(line_list[1]) != 0.0:
                print("4")
                if level == 0:
                    line_string = kml.newlinestring(name="wow2")
                if level < 4:
                    level = 4
            elif int(line_list[2]) > avg * 2 and float(line_list[0]) != 0.0 and float(line_list[1]) != 0.0:
                print("3")
                if level == 0:
                    line_string = kml.newlinestring(name="wow2")
                if level < 3:
                    level = 3
            elif int(line_list[2]) > avg * 1.5 and float(line_list[0]) != 0.0 and float(line_list[1]) != 0.0:
                print("2")
                if level == 0:
                    line_string = kml.newlinestring(name="wow2")
                if level < 2:
                    level = 2
            elif int(line_list[2]) > avg * 1.25 and float(line_list[0]) != 0.0 and float(line_list[1]) != 0.0:
                print("1")
                if level == 0:
                    line_string = kml.newlinestring(name="wow2")
                if level < 1:
                    level = 1


        else:
            break
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
kml.save('lines2.kml')
print("All done")