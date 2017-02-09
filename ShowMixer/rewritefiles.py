infile = open('/home/mac/Shows/Pauline/Pauline_cues_w_cuetypes.xml','r')
#outfile = open('/home/mac/Shows/Pauline/Pauline_cues_w_cuetypes-1.xml','w')

for each_line in infile:
    this_line = each_line.strip()
    #print(each_line)
    if this_line.startswith('<Entrances>'):
        new_line = this_line.replace('ch1,', 'ch01,').replace('ch1')
        print(this_line)
        print(new_line)
    elif this_line.startswith('<Exits>'):
        print(this_line)
    elif this_line.startswith('<Levels>'):
        print(this_line)

infile.close()
#outfile.close()