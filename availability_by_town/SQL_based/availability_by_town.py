#-*- coding: UTF-8 -*-
'''
Apache Spark Python script
Run with:
$> spark-submit run.py
compatibility: python 3.X
'''

import sys
sys.path.append('../..')

from starter import *
import misc
from pyspark.sql.functions import *
import argparse
import cProfile

def main(numPart, profile):

    if profile:
        sObj = Starter(numPart,profile=True) # profile mode
    else:
        sObj = Starter(numPart) # normal mode

    # Get the name of towns where bike stations are located
    towns = [val.town for val in sObj.stationsDf.select('town').distinct().collect()]
    # Print the min number of parition used for the RDDs
    print("Min number of partitions for the RDDs: {0}".format(sObj.stationsDf.rdd.getNumPartitions()))


    ratiosDf = None
    for town in towns:
        townQry = sObj.sqlContext.sql('SELECT town, status, available_bikes, available_bike_stands from stations WHERE town==\"{0}\"'.format(town))

        sumDf = townQry.select(townQry.town, townQry.status, townQry.available_bikes.alias('bikes'), (townQry.available_bikes + townQry.available_bike_stands).alias('total') )
        rDf = sumDf.select(sumDf.town, when((sumDf.total>0) & (sumDf.status=='OPEN'),(sumDf.bikes/sumDf.total)).otherwise(0.).alias('ratio'))

        if ratiosDf != None:
            ratiosDf = ratiosDf.union( rDf )
        else:
            ratiosDf = rDf

    avgRatioByTownDf = ratiosDf.groupBy('town').mean('ratio').sort('town')
    avgRatioByTownDf = avgRatioByTownDf.select('town', (avgRatioByTownDf['avg(ratio)']*100.).alias('percent'))

    print('\nAverage availability of bikes in stations by town:')
    for row in avgRatioByTownDf.collect():
        town = row['town']
        availability = row['percent']
        print('{0:18s} {1:3.0f} %'.format(misc.firstCapital(town), availability))

    print('\n'+misc.timestamp()+'\n')

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
