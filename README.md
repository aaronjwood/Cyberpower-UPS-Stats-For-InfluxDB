**Cyberpower UPS Data Collector For InfluxDB**
------------------------------

This script allows you to collect data about a CyberPower UPS and send it to InfluxDB

**Usage**

Put your Plex and Influx info in config.ini and run CyberpowerUpsStats.py


***Requirements***

Python 3

You will need the influxdb library installed to use this - [Found Here](https://github.com/influxdata/influxdb-python)

~~You also need PowerPanel Business Edition running - [Found Here](https://cyberpowersystems.com/products/software/)~~

Now you only need the personal edition. For a lot of the consumer-focused models the business edition doesn't work. For example, my model is CP1350PFCLCD and the business edition works for about a day or two until it stops communicating with the UPS. All of the data about the UPS is then frozen on the last collected values which ruins the data going to Influx.