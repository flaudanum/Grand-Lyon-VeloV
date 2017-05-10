#-*- coding: UTF-8 -*-
'''
Apache Spark Python script
Run with:
$> spark-submit run.py
compatibility: python 3.X
'''

from starter import *
from misc import *
import argparse
import sys
import cProfile

def main(numPart, profile):
    
    if profile:
        sObj = Starter(numPart,profile=True) # profile mode
    else:
        sObj = Starter(numPart) # normal mode


    # Get the name of towns where bike stations are located
    towns = sObj.factors('commune')
    # Print the min number of parition used for the RDDs
    print("Min number of partitions for the RDDs: {0}".format(sObj.valuesRDD.getNumPartitions()))

    averageRatio = dict()
    for town in towns:
        # Filter data by town
        townRDD = sObj.valuesRDD.filter(lambda value: value['commune']==town)
        
        def ratio(value):
            """
            Calculate the availability ratio for a given station (data value)
            """
            # If the station is closed the availability ratio is 0%
            if value['status']=='CLOSED':
                return 0.
            try:
                bikes = float(value['available_bikes']) 
                total = float(value['available_bikes'])+float(value['available_bike_stands'])
                # If the effective number of operating stands is zero the availability ratio is 0%
                if total==0:
                    return 0.
                else:
                    # Some bike stands are out of service. The ratio is then calculated as the sum of stands with available 
                    # bikes plus the stands available for parking bikes
                    return bikes / total
            except:
                message = 'Error at '+town
                message+=' ; (bikes,stands)=({0},{1})'.format(float(value['available_bikes']),float(value['available_bike_stands']))
                message+=' ; status is {0}'.format(value['status'])
                sys.stderr.write(message+'\n')
                return 0.
        
        # Compute the availability ratio for every station in the town
        availabilityRatio = townRDD.map(ratio)
        
        # Compute the average availability ratio of stations in the town
        
        # --> version 1: 'aggregate' approach
    #    sumCount = availabilityRatio.aggregate((0,0),\
    #    (lambda acc, val: (acc[0]+val, acc[1]+1)), (lambda acc1,acc2: (acc1[0]+acc2[0],acc1[1]+acc2[1])) )
    #    averageRatio[town] = sumCount[0]/sumCount[1]
        
        # --> version 2: per-partition approach
    #    def partCounters(ratios):
    #        """Compute sum and counting of ratios for a given partition"""
    #        sumCount = [0,0]
    #        for r in ratios:
    #            sumCount[0] += r
    #            sumCount[1] += 1
    #        return [sumCount] # Must return an iterator of pairs
    #    
    #    def combCounters(acc1, acc2):
    #        return (acc1[0]+acc2[0],acc1[1]+acc2[1])
    #    
    #    sumCount = availabilityRatio.mapPartitions(partCounters).reduce(combCounters)
    #    averageRatio[town] = sumCount[0]/float(sumCount[1])
        
        # --> version 3: with statistic RDD operation mean()
        averageRatio[town] = availabilityRatio.mean()

    print('\nAverage availability of bikes in stations by town:')
    for town in sorted(towns):
        # First capital letter
        textList = list(town.lower())
        textList[0] = textList[0].upper()
        townText = ''.join(textList)
        print('{0:18s} {1:3.0f} %'.format(townText, averageRatio[town]*100.))

    print('\n'+timestamp()+'\n')

    if profile:
        sObj.sparkContext.show_profiles()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Run use case \'Availability by town\'')
    parser.add_argument('--num-part', dest='numPart', default=2, type=int, help='Number of partitions for the RDDs')
    parser.add_argument('-p','--profile', action='store_true', help='Profiling mode')
    args = parser.parse_args()
    
    if args.profile:
        cProfile.run('main(args.numPart,profile=args.profile)','./availability_by_town.pstats')
    else:
        main(args.numPart,profile=args.profile)






