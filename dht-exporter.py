#! /usr/bin/env python

import Adafruit_DHT as dht
import argparse
import sys


def calculate_absolute_humidity(_humidity, _temperature):
    return (6.112 * ((17.67 * _temperature) / (_temperature + 243.5)) * _humidity * 2.1674) / (273.15 + _temperature)

sensor_args = {'11': dht.DHT11, '22': dht.DHT22, '2302': dht.AM2302}

parser = argparse.ArgumentParser(description='Collects DHT sensor readings and export them as Prometheus metrics')
parser.add_argument('--sensor', dest='sensor', type=str, metavar='[11|22|2302]', required=True, help='DHT sensor type')
parser.add_argument('--pin', dest='pin', type=str, metavar='N', required=True, help='GPIO Pin connected to the sensor')

args = parser.parse_args()

humidity = None
pin = args.pin
sensor = args.sensor
temperature = None

if sensor in sensor_args:
    humidity, temperature = dht.read_retry(sensor_args[sensor], pin)

if humidity is not None and temperature is not None:
    absolute_humidity = calculate_absolute_humidity(humidity, temperature)

    print('Temp={0:0.1f}*  Humidity={1:0.1f}%  Absolute Humidity={2:0.2f}'.format(temperature, humidity, absolute_humidity))
    sys.exit(0)
else:
    print('Failed to get reading. Try again!')
    sys.exit(1)
