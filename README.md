# Grand Lyon Vélo'V stations
This small project intends to demonstrate how to carry out basic analysis of the open data on
[*Vélo'V stations*](https://velov.grandlyon.com/en.html) in *Le Grand Lyon* with **Apache Spark**.
*Le Grand Lyon* is an urban area composed of Lyon city and 50 surrounding towns.
*Vélo'V* stations are only located in Lyon and the neighboring towns (Caluire-et-cuire, Vaulx-en-velin, Venissieux, Villeurbanne).

## Open data
The data flow is available [here](https://download.data.grandlyon.com/ws/rdata/jcd_jcdecaux.jcdvelov/all.json) in **JSON** format. The data are in the field *values* and are continuously updated.
As specified before this data is open, it is under [*Licence ouverte*](https://download.data.grandlyon.com/files/grandlyon/LicenceOuverte.pdf), see [*Wiki open licence*](https://en.wikipedia.org/wiki/Open_licence_(French)).

## API
The class **Starter** in `starter.py` provides a basic API for getting structured live data as *Apache Spark* resilient distributed datasets (RDD).
It creates a SparKContext object that is configured for running *Spark* in **local mode** (in file `starter.py`):  
```Python
configuration = SparkConf().setMaster("local").setAppName(Starter.applicationName)
```
The syntax for the constructor of class starter.Starter is `Starter([minPartitions=2,profile=False])`  
The optional argument *minPartitions* can be defined for specifying the minimal number of partitions to be used in RDDs. The other optional argument *profile* start the *python profiler* (`cProfile` object), see the *Profiling* section for further details.  
Example:
```Python
from starter import *

sObj = Starter(2,True) # Minimum number of paritions is 2, profiling is started
```
The RDD providing the data in the field *values* (JSON) in source data can be accessed with the property *valuesRDD*. Each value of this RDD is a `dict` object.
The other properties are:
* *sparkContext* which provides the *pyspark.SparkContext* object instanciated by the *Starter* object
* *stationNumber* (`int`) provides the number of bike stations open
* *fieldsNames* (`list`) is the list of fields name (`str`), that is the keys of the `dict` values in *Starter.valuesRDD*

**UPCOMING UPDATE**: a version of the code based on **Spark SQL** will be uploaded soon.


# Availability of bikes
## Running the use case
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
## Options
The complete syntax and options of the script `availability_by_town.py` are given with the script's help:
```
$> spark-submit availability_by_town.py -h
usage: availability_by_town.py [-h] [--num-part NUMPART] [-p]

Run use case 'Availability by town'

optional arguments:
  -h, --help          show this help message and exit
  --num-part NUMPART  Number of partitions for the RDDs
  -p, --profile       Profiling mode
```
The number of partitions in the RDDs can be specified with the option `--num-part`. Example:
```
$> spark-submit availability_by_town.py --num-part 4
Min number of partitions for the RDDs: 4                                        
...
```
The *profiling* mode (performance assessment) can be started with the option `-p`.

## Profiling
When run in *profiling* mode, a directory `rdd_profile/` is created in the current path. *pstats* files related to every RDD created during the execution of the script can be found inside. Besides this directory, the file `availability_by_town.pstats` is created. It gives a general profiling of the run out of *Spark* activities.  
**Rem:** it worthy to note that this use case is not challenging *Spark* (even in *local mode*) for most of the time is spent in downloading the JSON data.
```
$> /usr/bin/time -f "real:%E cpu:%P mem:%K" spark-submit availability_by_town.py -p
$> python3 -m pstats ./availability_by_town.pstats
Welcome to the profile statistics browser.
./availability_by_town.pstats% sort time
./availability_by_town.pstats% stats 5
Tue May  9 11:54:59 2017    ./availability_by_town.pstats

         156131 function calls (146095 primitive calls) in 5.053 seconds

   Ordered by: internal time
   List reduced from 747 to 5 due to restriction <5>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
      432    4.410    0.010    4.410    0.010 {method 'recv_into' of '_socket.socket' objects}
      167    0.244    0.001    0.244    0.001 {method 'read' of '_ssl._SSLSocket' objects}
      402    0.054    0.000    0.054    0.000 {method 'sendall' of '_socket.socket' objects}
        1    0.046    0.046    0.046    0.046 {method 'do_handshake' of '_ssl._SSLSocket' objects}
       16    0.042    0.003    0.050    0.003 {built-in method _socket.getaddrinfo}
```
Most of the time is spent reading data from the dource URL with the method `socket.recv_into()`. Here is an [extract from the python.org documentation](https://docs.python.org/3.5/library/socket.html?highlight=socket.recv_into#socket.socket.recv_into):

`socket.recv_into(buffer[, nbytes[, flags]])`  
Receive up to nbytes bytes from the socket, storing the data into a buffer rather than creating a new bytestring. If nbytes is not specified (or 0), receive up to the size available in the given buffer. Returns the number of bytes received. See the Unix manual page recv(2) for the meaning of the optional argument flags; it defaults to zero.
