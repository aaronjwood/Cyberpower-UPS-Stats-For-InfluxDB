#!/usr/bin/env python

import configparser
import socket
import os
import sys
import time

from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError

__author__ = 'Matthew Carey'


class CyberpowerUpsStats(object):
    def __init__(self):

        self.config = ConfigManager()
        self.output = self.config.output
        self.delay = self.config.delay

        self.influx_client = InfluxDBClient(self.config.influx_address, self.config.influx_port,
                                            database=self.config.influx_database)

    def write_influx_data(self, json_data):
        """
        Writes the provided JSON to the database
        :param json_data:
        :return:
        """
        if self.output:
            print(json_data)
        try:
            self.influx_client.write_points(json_data)
        except InfluxDBClientError as e:
            if e.code == 404:
                print('Database {} Does Not Exist.  Attempting To Create'.format(
                    self.config.influx_database))
                # TODO Grab exception here
                self.influx_client.create_database(self.config.influx_database)
            else:
                print(e)

    def get_ups_data(self):
        """
        Quick and dirty way to get UPS data from Power Panel.
        :return:
        """

        # Running pwrstat -status through strace reveals how the tool gets its data from the UPS.
        # connect(3, {sa_family=AF_UNIX, sun_path="/var/pwrstatd.ipc"}, 19) = 0
        # sendto(3, "STATUS\n\n", 8, 0, NULL, 0)  = 8
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        address = '/var/pwrstatd.ipc'
        try:
            sock.connect(address)
        except socket.error as e:
            print('Failed to connect to UNIX socket: {}'.format(e))
            return

        message = b'STATUS\n\n'
        try:
            sock.sendall(message)
            ups_data = sock.recv(1024)
        finally:
            sock.close()

        decoded_data = ups_data.decode('utf-8')
        parsed_data = dict(item.split('=')
                           for item in decoded_data.split('\n', 1)[1].split('\n') if item)
        parsed_data['output_volt'] = float(parsed_data['output_volt']) / 1000
        parsed_data['load'] = float(parsed_data['load']) / 1000
        parsed_data['output_watts'] = (float(
            parsed_data['output_rating_watt']) / 1000) * (parsed_data['load'] / 100)
        parsed_data['output_amps'] = parsed_data['output_watts'] / \
            parsed_data['output_volt']

        self._process_ups_data(parsed_data)

    def _process_ups_data(self, ups_data):
        self.write_influx_data([
            {
                'measurement': 'ups',
                'fields': {
                    'utility_voltage': float(ups_data['utility_volt']) / 1000,
                    'output_voltage': ups_data['output_volt'],
                    'battery_voltage': float(ups_data['battery_volt']) / 1000,
                    'output_load': ups_data['load'],
                    'output_watts': ups_data['output_watts'],
                    'output_amps': ups_data['output_amps'],
                    'battery_capacity': int(ups_data['battery_capacity']),
                    'battery_runtime_minute': int(int(ups_data['battery_remainingtime']) / 60)
                }
            }
        ])

    def run(self):
        while True:
            self.get_ups_data()
            time.sleep(self.delay)


class ConfigManager(object):
    def __init__(self):
        print('Loading Configuration File')
        config_file = os.path.join(os.getcwd(), 'config.ini')
        if os.path.isfile(config_file):
            self.config = configparser.ConfigParser()
            self.config.read(config_file)
        else:
            print('ERROR: Unable To Load Config File')
            sys.exit(1)

        self._load_config_values()
        print('Configuration Successfully Loaded')

    def _load_config_values(self):

        # General
        self.delay = self.config['GENERAL'].getint('Delay', fallback=2)
        self.output = self.config['GENERAL'].getboolean(
            'Output', fallback=True)

        # InfluxDB
        self.influx_address = self.config['INFLUXDB']['Address']
        self.influx_port = self.config['INFLUXDB'].getint(
            'Port', fallback=8086)
        self.influx_database = self.config['INFLUXDB'].get(
            'Database', fallback='plex_data')


def main():
    ups_stats = CyberpowerUpsStats()
    ups_stats.run()


if __name__ == '__main__':
    main()
