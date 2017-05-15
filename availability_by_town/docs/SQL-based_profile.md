# Profiling analysis of the SQL based solution of the *Availability of bikes by town*

## Starting `spark-submit`

Starting command `spark-submit` takes 1.27 seconds with my machine which is not neglectible considering the briefness of the whole run. As we can see no time was spent in function calls:  
```
[flaudanum@new-host SQL_based]$ python -m pstats availability_by_town.pstats
Welcome to the profile statistics browser.
availability_by_town.pstats% sort time
availability_by_town.pstats% stats 10
Sun May 14 12:37:30 2017    availability_by_town.pstats

         7 function calls in 0.000 seconds

   Ordered by: internal time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    0.000    0.000 {built-in method builtins.exec}
        1    0.000    0.000    0.000    0.000 {method 'close' of '_io.TextIOWrapper' objects}
        1    0.000    0.000    0.000    0.000 /home/flaudanum/anaconda3/lib/python3.5/_sitebuiltins.py:19(__call__)
        1    0.000    0.000    0.000    0.000 /home/flaudanum/DEV/Projects/Grand-Lyon-VeloV.dev/availability_by_town/SQL_based/availability_by_town.py:18(main)
        1    0.000    0.000    0.000    0.000 /home/flaudanum/DEV/Projects/Grand-Lyon-VeloV.dev/availability_by_town/SQL_based/starter.py:46(__init__)
        1    0.000    0.000    0.000    0.000 <string>:1(<module>)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
```

## Break point #1: creation of a `SparkConf` object

This break point allows the profiling of the creation of the `SparkConf` object at the beginning of the constructor of class `Starter`:
```
self.__conf = SparkConf().setMaster("local").setAppName(Starter.applicationName)
```
The result of command `time` is `real:0:01.33 CPU:145%` which show that creating a `SparkConf` object is quite short. The profile of the run shows that the function that spend the maximal total time is the method `recv_into` from class `socket` of the `socket` package:
```
ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    14    0.047    0.003    0.047    0.003 {method 'recv_into' of '_socket.socket' objects}
    14    0.000    0.000    0.000    0.000 {method 'sendall' of '_socket.socket' objects}
    14    0.000    0.000    0.049    0.003 /home/flaudanum/Applications/spark-2.0.0-bin-hadoop2.7/python/lib/py4j-0.10.1-src.zip/py4j/java_gateway.py:813(send_command)
    14    0.000    0.000    0.048    0.003 {method 'readline' of '_io.BufferedReader' objects}
  14/2    0.000    0.000    0.000    0.000 /home/flaudanum/anaconda3/lib/python3.5/abc.py:194(__subclasscheck__)
```


## Break point #2: creation of a `SparkContext` object

The creation of the `SparkContext` object is now assessed. See constructor of class `Starter`:
```
self.__sc = SparkContext(conf = self.__conf)
```

The result of command `time` is `real:0:03.05 CPU:182%`. The profile of the run shows like before that most of the time is spent with the method `socket.socket.recv_into()`. It was called 14 times when creating the `SparkConf` object, it is now called 98 times more.

## Break point #3: creation of a `SQLContext` object

The creation of the `SQLContext` is not costly at all. It only requires 4 more calls to the method `socket.socket.recv_into()`.


## Break point #4: read raw data from an URL

This task is performed with the python module `urllib.request` which provides the function `urlopen()` that creates a `http.client.HTTPResponse` object used to read data with the method `read()`:
```
with urllib.request.urlopen(Starter.dataSrcUrl) as response: # Type: <class 'http.client.HTTPResponse'>
    byteObj = response.read()                                # Type: <class 'bytes'>
```
The mean user elapsed time is approximately 3,50 seconds.
This reading operation requires 17 more calls to the method `socket.socket.recv_into()` and 179 calls to the method `read()` from the class `ssl.SSLSocket`.
It is worthy to note that the number of calls to that last method can vary slightly from one call to another, probably depending on the data to be read.
```
ncalls  tottime  percall  cumtime  percall filename:lineno(function)
   133    1.670    0.013    1.670    0.013 {method 'recv_into' of '_socket.socket' objects}
   179    0.328    0.002    0.328    0.002 {method 'read' of '_ssl._SSLSocket' objects}
     1    0.083    0.083    0.083    0.083 {method 'do_handshake' of '_ssl._SSLSocket' objects}
     1    0.040    0.040    0.052    0.052 {built-in method _socket.getaddrinfo}
     2    0.026    0.013    0.026    0.013 {method 'connect' of '_socket.socket' objects}
     1    0.008    0.008    0.008    0.008 {method 'set_default_verify_paths' of '_ssl._SSLContext' objects}
```
The following task consisting of converting `bytes` data to unicode and parsing the *JSON* structure is costless.
```
data = json.loads(byteObj.decode("UTF-8"))
```



## Break point #5: Create an RDD with input data

This operation is quite costless and only requires 4 more calls to the method `socket.socket.recv_into()`.
The mean user elapsed time for the creation of an RDD with a set of 2 repartitions is around 3.56 seconds.
The tool providing these statistics is available [here](https://github.com/flaudanum/pTimeStats).
```
$> python pTimeStats.py command 'spark-submit availability_by_town.py' 25
Percentage of a CPU that this job got
Min value:       178.0%
Mean value:      188.68%
Max value:       194.0%
90% confidence:  [189.0 , 193.34]%

Elapsed real time
Min value:       3.58
Mean value:      3.69
Max value:       3.85
90% confidence:  [3.68 , 3.8104000000000005]

Total number of CPU-seconds that the process spent in user mode divided by the CPU load
Min value:       3.44041450777202
Mean value:      3.556551641939736
Max value:       3.713483146067416
90% confidence:  [3.544973544973545 , 3.6766060087933568]
```
The *map* operation that follows does not require any socket reading and is costless.


## Break point #6: Create a DataFrame and a SQL table

This operation requires 39 more calls to the method `socket.socket.recv_into()`.
It is worthy to note that the time per call has significantly increased from 0.014 to 0.025 which probably means that
the 39 additional calls are very much longer than the previous ones.
```
ncalls  tottime  percall  cumtime  percall filename:lineno(function)
   176    4.471    0.025    4.471    0.025 {method 'recv_into' of '_socket.socket' objects}
   167    0.587    0.004    0.587    0.004 {method 'read' of '_ssl._SSLSocket' objects}
     1    0.074    0.074    0.074    0.074 {method 'do_handshake' of '_ssl._SSLSocket' objects}
```
The time statistics show a visible increase in time.
```
Total number of CPU-seconds that the process spent in user mode divided by the CPU load
Min value:       6.49171270718232
Mean value:      6.901426775262965
Max value:       11.38095238095238
90% confidence:  [6.6571428571428575 , 8.636632243258749]

Elapsed real time
Min value:       6.73
Mean value:      7.145600000000001
Max value:       11.82
90% confidence:  [6.9 , 8.9556]

Percentage of a CPU that this job got
Min value:       105.0%
Mean value:      174.84%
Max value:       187.0%
90% confidence:  [178.0 , 185.01999999999998]%
```
Creating a SQL table requires 1 more call to the method `socket.socket.recv_into()` and some additional calls to
`ssl.SSLSocket.read()`. This last number is still variable but has increased in average.
```
ncalls  tottime  percall  cumtime  percall filename:lineno(function)
   177    4.754    0.027    4.754    0.027 {method 'recv_into' of '_socket.socket' objects}
   182    0.207    0.001    0.207    0.001 {method 'read' of '_ssl._SSLSocket' objects}
   270    0.062    0.000    0.062    0.000 {built-in method marshal.loads}
     1    0.055    0.055    0.055    0.055 {method 'do_handshake' of '_ssl._SSLSocket' objects}
```
The following `count()` operation is costless and requires 1 call to the method `socket.socket.recv_into()`.

## Break point #7: Get the name of towns where bike stations are located
Three operations are applied to the DataFrame `sObj.stationsDf` for getting the the name of the towns where bikes are located:
* a projection with `DataFrame.select()`
* a filtering with `DataFrame.distinct()`
* a call to `DataFrame.collect()`
The time statistics show a significant increase. 22 more calls to the method `socket.socket.recv_into()` were performed.
Moreover, the time spent per call for this method also increased by +37%.
```
Total number of CPU-seconds that the process spent in user mode divided by the CPU load
Min value:       9.13744075829384
Mean value:      9.339860667472523
Max value:       10.356756756756756
90% confidence:  [9.221698113207548 , 10.260979836979837]

Percentage of a CPU that this job got
Min value:       185.0%
Mean value:      207.72%
Max value:       215.0%
90% confidence:  [210.0 , 213.68]%

Elapsed real time
Min value:       9.39
Mean value:      9.6036
Max value:       10.7
90% confidence:  [9.48 , 10.5746]
```
Profiling:
```
ncalls  tottime  percall  cumtime  percall filename:lineno(function)
   198    7.170    0.036    7.170    0.036 {method 'recv_into' of '_socket.socket' objects}
   164    0.234    0.001    0.234    0.001 {method 'read' of '_ssl._SSLSocket' objects}
     1    0.198    0.198    0.198    0.198 {method 'do_handshake' of '_ssl._SSLSocket' objects}
```

## Computing the bikes's availability by town

The following *SQL query* is costless (only one call to `socket.socket.recv_into()` whatever the value of the `WHERE` clause).
```python
townQry = sObj.sqlContext.sql('SELECT town, status, available_bikes, available_bike_stands from stations WHERE town==\"{0}\"'.format(town))
```
The following operation creates a new DataFrame from operation on columns of the `townQry`.
Whatever the content of `townQry`, it always add 20 calls to `socket.socket.recv_into()`.
```python
sumDf = townQry.select(townQry.town, townQry.status, townQry.available_bikes.alias('bikes'), (townQry.available_bikes + townQry.available_bike_stands).alias('total') )
```
The following operation creates a new DataFrame from operation on columns of the `sumDf`.
The number of additional calls to `socket.socket.recv_into()` is always 24, except for the 2nd iteration where it is 76.
```python
rDf = sumDf.select(sumDf.town, when((sumDf.total>0) & (sumDf.status=='OPEN'),(sumDf.bikes/sumDf.total)).otherwise(0.).alias('ratio'))
```
The `union()` operation is costless (only one call to `socket.socket.recv_into()`).
```python
ratiosDf = ratiosDf.union( rDf )
```
The two last operations cost 41 calls to `socket.socket.recv_into()`.
```python
avgRatioByTownDf = ratiosDf.groupBy('town').mean('ratio').sort('town')
avgRatioByTownDf = avgRatioByTownDf.select('town', (avgRatioByTownDf['avg(ratio)']*100.).alias('percent'))
```

The reading of sockets carried out by all these operations **are very short**.
The average elapsed time per call decrease from 0.037 seconds to 0.007.
It can be concluded that computing the bikes's availability by town is **timeless**!
```
ncalls  tottime  percall  cumtime  percall filename:lineno(function)
  1089    8.076    0.007    8.076    0.007 {method 'recv_into' of '_socket.socket' objects}
   164    0.220    0.001    0.220    0.001 {method 'read' of '_ssl._SSLSocket' objects}
   270    0.061    0.000    0.061    0.000 {built-in method marshal.loads}
```


## Reading data directly from rows

The final print task involves get `Row` objects from the DataFrame `avgRatioByTownDf`.
```python
for row in avgRatioByTownDf.collect():
    town = row['town']
    availability = row['percent']
    print('{0:18s} {1:3.0f} %'.format(misc.firstCapital(town), availability))
```
This operation makes 5 very long calls to `socket.socket.recv_into()`.
This approch is **very likely not the more efficient**.
```
ncalls  tottime  percall  cumtime  percall filename:lineno(function)
  1135   12.070    0.011   12.070    0.011 {method 'recv_into' of '_socket.socket' objects}
   170    0.207    0.001    0.207    0.001 {method 'read' of '_ssl._SSLSocket' objects}
   270    0.064    0.000    0.064    0.000 {built-in method marshal.loads}
```
