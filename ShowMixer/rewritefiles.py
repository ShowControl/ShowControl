import re

infile = open('/home/mac/Shows/Pauline/Pauline_cues_w_cuetypes.xml','r')
#outfile = open('/home/mac/Shows/Pauline/Pauline_cues_w_cuetypes-1.xml','w')

for each_line in infile:
    this_line = each_line.strip()
    #print(each_line)
    if this_line.startswith('<Entrances>'):
        splitline = this_line.split(',')
        for chan in splitline:
            print(chan)
        chnums = re.findall(r'\d+', chan)
        chtext = re.findall(r'[<>/a-zA-Z]+',chan)
        print(chnums)
        new_line = ''
        for x in range(chtext.__len__()):
            if x == 0:
                new_line +=  chtext[x] + '{:1}'.format(int(chnums[x]))
            elif x < chtext.__len__() - 1:
                new_line += chtext[x] + '{:02}'.format(int(chnums[x]))
            else:
                new_line += chtext[x]
        print(this_line)
        # print(new_line)
    elif this_line.startswith('<Exits>'):
        print(this_line)
    elif this_line.startswith('<Levels>'):
        print(this_line)

infile.close()
#outfile.close()