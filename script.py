from datetime import datetime
import re
import csv

fmt = "%Y-%m-%d %H:%M:%S"

freq_obj = {}

f = open("usa-slovenia-2010.tsv")
r = csv.reader(f, delimiter = '\t')

base_time = "2010-06-18 13:45:00"
base_time = datetime.strptime(base_time, fmt)

while (1):
    try:
        t= r.next()
    except StopIteration:
        break
    print r.line_num

    mat=re.match('(\d{4})[/.-](\d{2})[/.-](\d{2})\s(\d{2})[/.:](\d{2})[/.:](\d{2})$',t[0])
    if mat is not None:
        d = datetime.strptime(t[0],fmt)
        #d = d - base_time
        #key = d.seconds/60
        key = format(d.hour,"02d")+":"+format(d.minute,"02d")
        freq_obj[key] = freq_obj.get(key,0)+1
    else:
        continue

f.close()
f = open("result","w")
for key in sorted(freq_obj.keys()):
    f.write(str(key)+"\t"+str(freq_obj[key])+"\n")
f.close()

print "max is ", max(freq_obj.values())

print "COMPLETED"


