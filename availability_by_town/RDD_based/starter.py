#-*- coding: UTF-8 -*-
"""
Class starter definition
python 3.X
"""


from pyspark import SparkConf, SparkContext, StorageLevel

import json
import urllib.request
import os.path
import shutil


class Starter:

    applicationName = 'Read Data Grand Lyon - Geo Velov'
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
    def valuesRDD(self):
        return self.__vrdd
    
    @property
    def fieldsNames(self):
        return self.__fields
    
    def __init__(self, minPartitions=None, profile=False):
        self.__conf = SparkConf().setMaster("local").setAppName(Starter.applicationName)
        if profile:
            self.__conf.set("spark.python.profile", "true")
            localFsSavePath = os.path.abspath("./rdd_profile")
            if os.path.isdir(localFsSavePath):
                shutil.rmtree(localFsSavePath)
            self.__conf.set("spark.python.profile.dump",localFsSavePath)
        self.__sc = SparkContext(conf = self.__conf)
        sc = self.__sc
        
        
        with urllib.request.urlopen(Starter.dataSrcUrl) as response: # Type: <class 'http.client.HTTPResponse'>
            byteObj = response.read() # Type: <class 'bytes'>

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
        
        # Make the RDD persist
        # valuesRDD.persist(StorageLevel.MEMORY_ONLY) 
        
        # Store the RDD as an attribute
        self.__vrdd = valuesRDD
        
        # Number of Vélo'V stations
        self.__snum = valuesRDD.count()
        
    
    
    def saveAsTextFile(self, vRDD=None):
        
        def formatting(value):
            
            colorTranslation = {'Orange':'Orange', 'Bleu':'Blue', 'Vert':'Green', 'Gris':'Grey'}
            
            strObj = str()
            strObj += "Name of Velo\'V station: {0}\n".format(value["name"])
            strObj += "Adress:                 {0}\n".format(value["address"])
            if value["address2"]!="None" and value["address2"]!="":
                strObj += "                        {0}\n".format(value["address2"])
            strObj += "Town:                   {0}\n".format(value["commune"])
            try:
                strObj += "Latitude/Longitude:     ({lat:.16f} / {lng:.16f})\n".format(lat=float(value["lat"]),lng=float(value["lng"]))
            except:
                pass
            if value["status"]=="OPEN":
                strObj += "Status:                 Open\n"
            else:
                strObj += "Status:                 Closed\n"
            try:
                strObj += "Available bikes:        {0:d}\n".format(int(value["available_bikes"]))
            except:
                pass
            try:
                strObj += "Availabel empty stands: {0:d}\n".format(int(value["available_bike_stands"]))
            except:
                pass
            strObj += "Last data update:       {0}\n".format(value["last_update"])
            strObj += "Availability level:     {0}\n".format(colorTranslation[value["availability"]])
            
            return strObj

        if vRDD==None:
            vRDD = self.valuesRDD
        
        summaryRDD = vRDD.map(lambda value: formatting(value) )

        localFsSavePath = os.path.abspath("./summary")

        if os.path.isdir(localFsSavePath):
            shutil.rmtree(localFsSavePath)

        summaryRDD.saveAsTextFile("file://"+localFsSavePath )
        print("Data were saved in file "+localFsSavePath)


    def factors(self,feature):
        if not(feature in self.fieldsNames):
            return None
        
        factorRDD = self.valuesRDD.map(lambda value: value[feature]).distinct()
        return factorRDD.collect()
        
        
    # Implémenter une méthode refresh() pour reconstruire les RDD avec les données à jour
    # On perd l'immutabilité mais on évite un processus lourd de l'objet SparContext
        








