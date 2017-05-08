# Grand Lyon Vélo'V stations
This small project intend to demonstrate how to carry out basic analysis of the open data on
[*Vélo'V stations*](https://velov.grandlyon.com/en.html) in *Le Grand Lyon* with Apache Spark.
*Le Grand Lyon* is an urban area composed of Lyon city and 50 surrounding towns.
*Vélo'V* stations are only located in Lyon and the neighboring towns (Caluire-et-cuire, Vaulx-en-velin, Venissieux, Villeurbanne).

The data flow is available [here](https://download.data.grandlyon.com/ws/rdata/jcd_jcdecaux.jcdvelov/all.json) in **JSON** format. The data are in the field *values* and are continuously updated.
As specified before this data is open, it is under [*Licence ouverte*](https://download.data.grandlyon.com/files/grandlyon/LicenceOuverte.pdf), see [*Wiki open licence*](https://en.wikipedia.org/wiki/Open_licence_(French)).

The class **Starter** in `starter.py` provides a basic API for getting structured live data as *Apache Spark* resilient distributed datasets (RDD).
It creates a SparKContext object that is configured for running *Spark* in **local mode**. In file `starter.py`:  
```Python
configuration = SparkConf().setMaster("local").setAppName(Starter.applicationName)
```
The syntax for the constructor of class starter.Starter is:  
`Starter([minPartitions])`  
The argument *minPartitions* can be defined for specifying the minimal number of partitions to be used in RDDs.  
Example:
```Python
from starter import *

sObj = Starter(2) # Minimum number of paritions is 2
```
The RDD providing the data in the field *values* can be access with the property *valuesRDD*. Each value of this RDD is a `dict` object.
The other properties are:
* *sparkContext* which provides the *pyspark.SparkContext* object instanciated by the *Starter* object
* *stationNumber* (`int`) provides the number of bike stations open
* *fieldsNames* (`list`) is the list of fields name (`str`), that is the keys of the `dict` values in *Starter.valuesRDD*


# Availability of bikes
The Python script `availability_by_town.py` is a use case where the percentage of bikes availability is calculated for each town of *Le Grand Lyon* (where there are bike stations).
Simply run the use case with `spark-submit`:  
```
$>spark-submit spark-submit availability_by_town.py

Average availability of bikes in stations by town:
Caluire-et-cuire    26 %
Lyon 1 er           31 %
Lyon 2 ème          28 %
Lyon 3 ème          25 %
Lyon 4 ème           9 %
Lyon 5 ème          18 %
Lyon 6 ème          20 %
Lyon 7 ème          32 %
Lyon 8 ème          37 %
Lyon 9 ème          29 %
Vaulx-en-velin       0 %
Venissieux          50 %
Villeurbanne        27 %

May 7 2017, 21:53:12
```
