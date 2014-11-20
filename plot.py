#import matplotlib.pyplot as plt
import numpy as n

f = open("result","r")
lines = f.readlines()

values = []
for line in lines:
    [key,value] = line.split("\t")
    values.append(int(value))

values = n.array(values)

slopes = []
for index in range(0,len(values)-1):
    slopes.append(values[index+1]-values[index])

slopes = n.array(slopes)

slope_median = n.median(slopes)
slope_threshold = 3*slope_median
slope_threshold = slopes.mean() + slopes.std()

print "Median of slopes is ",slope_median
print "Std , Mean is ", slopes.std(), slopes.mean()
print "Slope threshold is ",slope_threshold

#for i in range(0,len(slopes)):
#    if slopes[i] >slope_threshold:
#        print i,slopes[i]

for i in range(1,len(slopes)-1):
    if slopes[i-1]>0 and slopes[i]<0 and values[i] > 2*slopes.std():
        print "index, value, slope (i-1,i)", i, values[i], slopes[i-1],slopes[i]

