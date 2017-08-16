bigstring = 'M0ch09:0,M0ch04:0,M0ch02:0,M0ch31:0,M0aux02:0,M0ch16:0,M0ch24:0,M0ch21:0,M0ch27:0,M0ch29:0,M0bus07:0,M0ch01:1,M0bus10:0,M0ch28:0,M0bus12:0,M0aux01:0,M0bus05:0,M0ch08:0,M0aux03:0,M0ch14:0,M0bus02:0,M0ch15:0,M0ch26:0,M0bus11:0,M0ch12:0,M0ch20:0,M0bus13:0,M0ch18:0,M0ch23:0,M0ch17:0,M0bus03:0,M0ch03:0,M0ch10:0,M0ch25:0,M0bus04:0,M0bus06:0,M0bus15:0,M0ch11:0,M0aux06:0,M0ch22:0,M0bus16:0,M0ch07:0,M0ch19:0,M0bus01:0,M0main01:0,M0bus08:0,M0ch05:0,M0ch13:0,M0ch30:0,M0aux05:0,M0aux04:0,M0bus14:0,M0bus09:0,M0ch32:0,M0ch06:0'
biglist = bigstring.split(',')
chlist = []
auxlist = []
buslist = []
mainlist = []
for control in biglist:
    if 'bus' in control:
        buslist.append(control)
    elif 'aux' in control:
        auxlist.append(control)
    elif 'main' in control:
        mainlist.append(control)
    elif 'ch' in control:
        chlist.append(control)
buslist = sorted(buslist)
auxlist = sorted(auxlist)
mainlist = sorted(mainlist)
chlist = sorted(chlist)
sorted_controls = chlist + auxlist + buslist + mainlist
print(','.join(sorted_controls))