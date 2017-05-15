# Grand Lyon Vélo'V stations
This small project intends to demonstrate how to carry out basic analysis of the open data on
[*Vélo'V stations*](https://velov.grandlyon.com/en.html) in *Le Grand Lyon* with **Apache Spark**.
*Le Grand Lyon* is an urban area composed of Lyon city and 50 surrounding towns.
*Vélo'V* stations are only located in Lyon and the neighboring towns (Caluire-et-cuire, Vaulx-en-velin, Venissieux, Villeurbanne).

Two solutions are provided for this application: one based on **RDDs** and the other on **Spark SQL**

## Open data
The data flow is available [here](https://download.data.grandlyon.com/ws/rdata/jcd_jcdecaux.jcdvelov/all.json) in **JSON** format. The data are in the field *values* and are continuously updated.
As specified before this data is open, it is under [*Licence ouverte*](https://download.data.grandlyon.com/files/grandlyon/LicenceOuverte.pdf), see [*Wiki open licence*](https://en.wikipedia.org/wiki/Open_licence_(French)).

## API for the RDD based solution
The class **Starter** in `starter.py` provides a basic API for getting structured live data as *Apache Spark* resilient distributed datasets (RDD).
The constructor creates a SparKContext object that is configured for running *Spark* in **local mode** (in file `starter.py`):  
```Python
configuration = SparkConf().setMaster("local").setAppName(Starter.applicationName)
```
The syntax of the constructor of class starter.Starter is:  

`Starter([minPartitions=2,profile=False])`  

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

## API for the solution based on *Spark SQL*

The class **Starter** in `starter.py` provides a basic API for getting structured live data as a *Spark SQL DataFrame* or a reference to an *SQL table*.
The constructor creates a SparKContext object that is configured for running *Spark* in **local mode** in the same way as presented in the previous section. The syntax of the constructor of this class is:

`Starter([minPartitions=2,profile=False])`  

The data are accessible from the property `stationsDf` which provides a `DataFrame` object and the global SQL table named `"stations"`. The other properties are given below:

|Property      | Type         | Description     |
|--------------|--------------|--------------|
|sparkContext  | [`pyspark.SparkContext`](https://spark.apache.org/docs/2.0.0/api/python/pyspark.html?highlight=sparkcontext#pyspark.SparkContext)| *SparkContext* abstraction|
|config | [`pyspark.SparkConf`](https://spark.apache.org/docs/2.0.0/api/python/pyspark.html?highlight=sparkconf#pyspark.SparkConf)|Spark configuration|
|stationNumber | `int`      |Number of Vélo'V stations|
|stationsDf| [`pyspark.sql.DataFrame`](https://spark.apache.org/docs/2.0.0/api/python/pyspark.sql.html#pyspark.sql.DataFrame)|Data on Vélo'V stations.|
|sqlContext| [`SqlContext`](https://spark.apache.org/docs/2.0.0/api/python/pyspark.sql.html#pyspark.sql.SQLContext)|*Spark SQL context* associated to the created *Spark context*|
|fieldsNames|`list(str)`|List of the field in the source data (not exactly the same as the name of columns in stationsDf)|



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

### Profiling

The analysis of the performance of the codes is carried out with 3 tools:
* the shell command `/user/bin/time`
* the python module `pstats`
* *pTimeStats* a python module computing time statistics on the elapsed time when running the application. `pTimeStats.py` is available [here](https://github.com/flaudanum/pTimeStats)

In order to have some performance reference, here is my configuration:

| Item | Designation |
|--------------------|
|OS           | Fedora 25 (64 bits) |
|Core         | Intel® Core™ i5 @ quad core 2.67GHz |
|Apache Spark | version 2.0.0 |
|API Python   | 3.5.2, Anaconda 4.2.0 (64-bit)  [GCC 4.4.7 20120313 (Red Hat 4.4.7-1)] |


#### RDD based solution
When run in *profiling* mode, a directory `rdd_profile/` is created in the current path. *pstats* files related to every RDD created during the execution of the script can be found inside. Besides this directory, the file `availability_by_town.pstats` is created. It gives a general profiling of the run out of *Spark* activities.  

Most of the time is spent reading from sockets with `socket.socket.recv_into()` which is related to *Spark* activities.
This aspect is demonstrated in the [detailed analysis of the profiling of the *SQL based solution*](availability_by_town/docs/SQL-based_profile.md).

`socket.recv_into()`. Here is an [extract from the python.org documentation](https://docs.python.org/3.5/library/socket.html?highlight=socket.recv_into#socket.socket.recv_into):

`socket.recv_into(buffer[, nbytes[, flags]])`  
Receive up to nbytes bytes from the socket, storing the data into a buffer rather than creating a new bytestring. If nbytes is not specified (or 0), receive up to the size available in the given buffer. Returns the number of bytes received. See the Unix manual page recv(2) for the meaning of the optional argument flags; it defaults to zero.
```
$> /usr/bin/time -f "real:%E cpu:%P mem:%K" spark-submit availability_by_town.py -p
...
$> python -m pstats ./availability_by_town.pstats
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
Time statistics are listed below. The process performance is very stable with small confidence intervals for the
elapsed time and the CPU load.
```
Total number of CPU-seconds that the process spent in user mode divided by the CPU load
Min value:       5.78 sec
Mean value:      6.19 sec
Max value:       7.18 sec
90% confidence:  [6.16 , 6.64] sec

Percentage of a CPU that this job got
Min value:       150.00 %
Mean value:      177.57 %
Max value:       186.00 %
90% confidence:  [178.50 , 185.09] %

Elapsed real time
Min value:       6.03 sec
Mean value:      6.42 sec
Max value:       7.43 sec
90% confidence:  [6.38 , 6.89] sec
```


#### SQL based solution
When running the *Spark SQL* based solution, the analysis of the file `./availability_by_town.pstats` leads to the same conclusion than when running the *RDD based one*: most of the time reading sockets with `socket.recv_into()`. However, there are thrice the number of calls and the total time is thrice also.
A [detailed analysis of the profile](availability_by_town/docs/SQL-based_profile.md) at different steps of the code reveals that the operations using `DataFrame` objects are
very efficient but there are some small overheads:
* creation of the `DataFrame` from an RDD
* calls to the `DataFrame.collect()` method that provide an iterator to the `Row` objects in the `DataFrame`.

```
$> /usr/bin/time -f "real:%E cpu:%P mem:%K" spark-submit availability_by_town.py -p
...
real:0:14.31 cpu:230% mem:0
$> python -m pstats availability_by_town.pstats
Welcome to the profile statistics browser.
availability_by_town.pstats% sort time
availability_by_town.pstats% stats 5
Fri May 12 23:41:24 2017    availability_by_town.pstats

         285082 function calls (278216 primitive calls) in 13.229 seconds

   Ordered by: internal time
   List reduced from 2881 to 5 due to restriction <5>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     1135   12.202    0.011   12.202    0.011 {method 'recv_into' of '_socket.socket' objects}
      161    0.245    0.002    0.245    0.002 {method 'read' of '_ssl._SSLSocket' objects}
        1    0.079    0.079    0.079    0.079 {method 'do_handshake' of '_ssl._SSLSocket' objects}
      270    0.059    0.000    0.059    0.000 {built-in method marshal.loads}
        4    0.041    0.010    0.056    0.014 {built-in method _socket.getaddrinfo}
        availability_by_town.pstats% sort cumtime
        availability_by_town.pstats% stats 10
        Fri May 12 23:41:24 2017    availability_by_town.pstats

                 285082 function calls (278216 primitive calls) in 13.229 seconds

           Ordered by: cumulative time
           List reduced from 2881 to 10 due to restriction <10>

           ncalls  tottime  percall  cumtime  percall filename:lineno(function)
            328/1    0.010    0.000   13.229   13.229 {built-in method builtins.exec}
                1    0.000    0.000   13.229   13.229 <string>:1(<module>)
                1    0.002    0.002   13.229   13.229 /home/flaudanum/DEV/Projects/Grand-Lyon-VeloV.dev/availability_by_town/SQL_based/availability_by_town.py:18(main)
             1296    0.005    0.000   12.458    0.010 /home/flaudanum/anaconda3/lib/python3.5/socket.py:561(readinto)
             1217    0.032    0.000   12.327    0.010 {method 'readline' of '_io.BufferedReader' objects}
             1129    0.003    0.000   12.297    0.011 /home/flaudanum/Applications/spark-2.0.0-bin-hadoop2.7/python/lib/py4j-0.10.1-src.zip/py4j/java_gateway.py:672(send_command)
             1129    0.019    0.000   12.291    0.011 /home/flaudanum/Applications/spark-2.0.0-bin-hadoop2.7/python/lib/py4j-0.10.1-src.zip/py4j/java_gateway.py:813(send_command)
             1135   12.202    0.011   12.202    0.011 {method 'recv_into' of '_socket.socket' objects}
          571/486    0.005    0.000   10.627    0.022 /home/flaudanum/Applications/spark-2.0.0-bin-hadoop2.7/python/lib/py4j-0.10.1-src.zip/py4j/java_gateway.py:923(__call__)
                1    0.000    0.000    6.457    6.457 /home/flaudanum/DEV/Projects/Grand-Lyon-VeloV.dev/availability_by_town/SQL_based/starter.py:46(__init__)
```
Here are the time statistics:
```
$> python pTimeStats.py command 'spark-submit availability_by_town.py' 30

Percentage of a CPU that this job got
Min value:       220.00 %
Mean value:      227.57 %
Max value:       238.00 %
90% confidence:  [227.50 , 234.36] %

Elapsed real time
Min value:       14.23 sec
Mean value:      14.62 sec
Max value:       15.30 sec
90% confidence:  [14.56 , 15.15] sec

Total number of CPU-seconds that the process spent in user mode divided by the CPU load
Min value:       13.88 sec
Mean value:      14.25 sec
Max value:       14.96 sec
90% confidence:  [14.19 , 14.80] sec
```


#### Conclusion

Every *Spark* operation from the creation of data with RDD or DataFrames, their transformations and final actions imply communications involving reading data on sockets.
Operations on DataFrames are acknowledged to be more efficient than those on RDDs. Considering the overhead when creating and reading (with `collect()`) from DataFrames,
that assertion is probably true for applications dealing with bigger volumes of data. Considering the small one of input data involved in this use case, a simple python
application with `threading` or `multiprocessing` modules may provide more efficient solutions. 
