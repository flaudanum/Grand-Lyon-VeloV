#-*- coding: UTF-8 -*-
"""
Class starter definition
python 3.X
"""


from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext, Row
import json
import urllib.request
import os.path
import shutil



class Starter:

    applicationName = 'Read Data Grand Lyon - Geo Velov (Spark SQL based)'
    dataSrcUrl = 'https://download.data.grandlyon.com/ws/rdata/jcd_jcdecaux.jcdvelov/all.json'

    @property
    def sparkContext(self):
        return self.__sc

    @property
    def config(self):
        return self.__conf

    @property
    def stationNumber(self):
        return self.__snum

    @property
    def stationsDf(self):
        return self.__df

    @property
    def sqlContext(self):
        return self.__sqlCtxt

    @property
    def fieldsNames(self):
        return self.__fields

    def __init__(self, minPartitions=None, profile=False):
        self.__conf = SparkConf().setMaster("local").setAppName(Starter.applicationName)
        # profile break #1
        if profile:
            self.__conf.set("spark.python.profile", "true")
            localFsSavePath = os.path.abspath("./profile")
            if os.path.isdir(localFsSavePath):
                shutil.rmtree(localFsSavePath)
            self.__conf.set("spark.python.profile.dump",localFsSavePath)
        self.__sc = SparkContext(conf = self.__conf)
        # profile break #2
        sc = self.__sc
        self.__sqlCtxt = SQLContext(sc)
        sqlc = self.__sqlCtxt
        # profile break #3

        with urllib.request.urlopen(Starter.dataSrcUrl) as response: # Type: <class 'http.client.HTTPResponse'>
            byteObj = response.read() # Type: <class 'bytes'>
        # profile break #4

        # Parse JSON data
        data = json.loads(byteObj.decode("UTF-8"))

        # Get fields' names
        # I could directly retrieve this information from the items in "values" but I choose to trust that field list
        self.__fields = data["fields"]

        # Store "values" data in an RDD. Each "value" is related to one Vélo'V station
        if minPartitions==None:
            valuesRDD = sc.parallelize(data["values"])
        else:
            valuesRDD = sc.parallelize(data["values"],minPartitions)

        rowRDD = valuesRDD.map(lambda val: Row(status=val['status'], town=val['commune'], name=val['name'], availability=val['availability'],\
        available_bike_stands=val['available_bike_stands'], available_bikes=val['available_bikes'], address=val['address'], lat=val['lat'],\
        lng=val['lng'], address2=val['address2']) )
        # profile break #5

        # Store the DataFrame object as an attribute associated to the property stationsDf
        self.__df = sqlc.createDataFrame(data=rowRDD)
        df = self.__df

        # Register the DataFrame object as a table for SQL queries
        sqlc.registerDataFrameAsTable(df, "stations")
        # profile break #6

        # Number of Vélo'V stations
        self.__snum = df.count()
