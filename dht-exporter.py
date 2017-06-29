#! /usr/bin/env python

import Adafruit_DHT as dht
import argparse
import sys
import time

from prometheus_client import Gauge
from prometheus_client import start_http_server

TEMPERATURE_GAUGE = Gauge('home_temperature', 'Current temperature', ['room'])
RELATIVE_HUMIDITY_GAUGE = Gauge('home_relative_humidity', 'Current relative humidity', ['room'])
ABSOLUTE_HUMIDITY_GAUGE = Gauge('home_absolute_humidity', 'Current absolute humidity', ['room'])

sensor_args = {'11': dht.DHT11, '22': dht.DHT22, '2302': dht.AM2302}


def calculate_absolute_humidity(_relative_humidity, _temperature):
    return (6.112 * ((17.67 * _temperature) / (_temperature + 243.5)) * _relative_humidity * 2.1674) / (273.15 + _temperature)


def update_metrics():
    if sensor in sensor_args:
        relative_humidity, temperature = dht.read_retry(sensor_args[sensor], pin)
        TEMPERATURE_GAUGE.labels(room).set("{0:0.1f}".format(temperature))
        RELATIVE_HUMIDITY_GAUGE.labels(room).set("{0:0.1f}".format(relative_humidity))

    if relative_humidity is not None and temperature is not None:
        absolute_humidity = calculate_absolute_humidity(relative_humidity, temperature)
        ABSOLUTE_HUMIDITY_GAUGE.labels(room).set("{0:0.2f}".format(absolute_humidity))

    print('Temp={0:0.1f}*  Relative Humidity={1:0.1f}%  Absolute Humidity={2:0.2f}'.format(temperature,
                                                                                           relative_humidity, absolute_humidity))

parser = argparse.ArgumentParser(description='Collects DHT sensor readings and export them as Prometheus metrics')
parser.add_argument('--sensor', dest='sensor', type=str, metavar='[11|22|2302]', required=True, help='DHT sensor type')
parser.add_argument('--pin', dest='pin', type=str, metavar='N', required=True, help='GPIO Pin connected to the sensor')
parser.add_argument('--room', dest='room', type=str, metavar='<room name>',
                    default="None", help='Specify a specific room')
parser.add_argument('--listen-port', dest='port', type=str, metavar='N',
                    default="1337", help='Listen port for Prometheus metrics endpoint')

args = parser.parse_args()

pin = args.pin
port = int(args.port)
relative_humidity = None
room = args.room
sensor = args.sensor
temperature = None

if __name__ == '__main__':
    print("Starting server on http://0.0.0.0:{}".format(port))
    start_http_server(port)

    while True:
        update_metrics()
        time.sleep(10)
