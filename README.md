# ADHassToInfluxDB

Appdaemon module to push data from Home Assistant to InlfuxDB on a configurable frequency. 

## Why

If like me, you use influxdb to keep history of your sensors from Home Assistant, you may face an issue:
Home Assistant only data from a sensor when it's modified. 

This result in holes in my graphs. Let me explain. 
Graphana queries influxdb with the time range you want to display, typically 1 day. 
If your sensor did not change during this day, your sensor is not visible. 
If your sensor changed only 1 time during this day, you won't see it's previous value, so the graph will begin in the middle of your time frame. 

This particullary anoying for me as I have some electricity measurement that are used only a few times during the month. 

## what it does

This AppDaemon app run a main function that grabs ALL entities and send them to InfluxDB. 
The frequency can be configured via apps.yaml. 

## Requirements

You need: 
 - Appdaemon
 - python influxdb module
 
 ## Configuration 
 
 ### Base
 
 Add the following configuration to your apps.yaml
 ```
 HassToInfluxdb:
  module: adhasstoinfluxdb
  class: HassToInfluxdb
  influxdb_host: <host>
  influxdb_port: 8086
  influxdb_database: <db>
  influxdb_username: <user>
  influxdb_password: <pass>
  influxdb_ssl: <True/False>
  influxdb_verify_ssl: <True/False>
  frequency: 60
```

### Filters



You can add filters to include only entities based on regular expression. 

```
  filters:
    include:
      - "switch.*"
      - "sensor.*"
      - "light.*"
      - "switch.*"
      - "cover.*"
```

You can add filters to exclude entities based on regular expression
If you have an include filter, exclude is ignored. 
```
    exclude:
      - "updater.+"
      - "zigate.+"
      - "timer.+"
      - "zwave.+"
      - "camera.*"
```

