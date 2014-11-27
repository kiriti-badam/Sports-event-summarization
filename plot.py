import numpy as n

def important_moments(input_file):
    """
        Given a input_file in which each line contains time\tfrequency, returns the important_moments to be considered
        based on the changes in the slope values and the values above a particular threshold.
        Returns an array of important_moments to be considered in the match
    """
    f = open(input_file,"r")
    lines = f.readlines()

    values = []
    for line in lines:
        [key,value] = line.split("\t")
        values.append(int(value))

    values = n.array(values)
    abs_values = n.absolute(values)
    
    slopes = []
    for index in range(0,len(values)-1):
        slopes.append(values[index+1]-values[index])

    slopes = n.array(slopes)
    
    threshold = n.median(abs_values) + 0.5*abs_values.std() #Emperical parameter, decided based on the training

    print "Median,std of values is ", n.median(abs_values), abs_values.std()

    result = []
    for i in range(1,len(slopes)-1):
        if slopes[i-1]>0 and slopes[i]<0 and values[i] > threshold: 
            result.append(i)
            print "index, value, slope (i-1,i)", i, values[i], slopes[i-1],slopes[i]
    return result

