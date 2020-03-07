import appdaemon.plugins.hass.hassapi as hass
from influxdb import InfluxDBClient
from datetime import datetime, timedelta, timezone
import json
import re

class HassToInfluxdb(hass.Hass):
    print_debug = True
    handle = None
    filters = {}
    parameters={}
    influxdb_database=''
    influxdb = None
    frequency = 5*60


    def initialize(self):
        if 'filters' in self.args:
            self.filters = self.args["filters"]
        if 'frequency' in self.args:
            self.frequency = self.args["frequency"]
        self.init_influxdb_parameters()
        self.handle = self.run_every(self.loop, datetime.now(timezone.utc) + timedelta(seconds=5) , self.frequency)


    def init_influxdb_parameters(self):
        if 'influxdb_host' in self.args:
            self.parameters['host'] = self.args['influxdb_host']
        else:
            self.parameters['host'] = 'localhost'
        if 'influxdb_port' in self.args:
            self.parameters['port'] = self.args['influxdb_port']
        else:
            self.parameters['port'] = 8086
        if 'influxdb_database' in self.args:
            self.influxdb_database = self.args['influxdb_database']
        else:
            self.influxdb_database = 'home_assistant'
        if 'influxdb_username' in self.args:
            self.parameters['username'] = self.args['influxdb_username']
        if 'influxdb_password' in self.args:
            self.parameters['password'] = self.args['influxdb_password']
        if 'influxdb_ssl' in self.args:
            self.parameters['ssl'] = self.args['influxdb_ssl']
        if 'influxdb_verify_ssl' in self.args:
            self.parameters['verify_ssl'] = self.args['influxdb_verify_ssl']


    def push_influxdb(self, points):
        try:
            client = InfluxDBClient(**self.parameters)
            client.switch_database(self.influxdb_database)
            client.write_points(points)
        except:
            print("issue while pushing data to influxdb")


    def loop(self, event_name):
        #self.debug('looping')
        points = []
        states = self.get_state()
        current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        for i in states:
            current = {'tags':{}, 'fields':{}}

            # Seems to happen when HA is stopped while executing this loop.
            if states[i] is None :
                continue

            entity_id = states[i]['entity_id']
            entity_infos = states[i]['entity_id'].split('.')

            if self.is_filtered(entity_id):
                continue

            if 'attributes' in states[i] and 'unit_of_measurement' in states[i]['attributes']:
                current['measurement'] = states[i]['attributes']['unit_of_measurement']
            else:
                current['measurement'] = states[i]['entity_id']

            current['tags']['domain'] = entity_infos[0]
            current['tags']['entity_id'] = entity_infos[1]
            if 'device_class' in states[i]['attributes']:
                current['tags']['device_class'] = states[i]['attributes']['device_class']
            if 'friendly_name' in states[i]['attributes']:
                current['tags']['friendly_name'] = states[i]['attributes']['friendly_name']

            try:
                value = float(states[i]['state'])
            except:
                value = states[i]['state']

            current['fields']['value'] = value
            current['time'] = current_time
            points.append(current)
            #self.debug(i + " | " + json.dumps(current))

        self.push_influxdb(points)

    def is_filtered(self, entity_id):
        if 'include' in self.filters:
            for filter in self.filters['include']:
                pattern = re.compile(filter)
                pattern.match(entity_id)
                if pattern.match(entity_id) != None:
                    return False
            return True
        if 'exclude' in self.filters:
            for filter in self.filters['exclude']:
                pattern = re.compile(filter)
                pattern.match(entity_id)
                if pattern.match(entity_id) != None:
                    return True
            return False


    def debug(self, message):
        if self.print_debug:
            print('adhasstoinfluxdb: ' + message)
