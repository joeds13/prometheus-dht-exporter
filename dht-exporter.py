#! /usr/bin/env python

import argparse
import sys
import time

import Adafruit_DHT as dht

from prometheus_client import Gauge
from prometheus_client import start_http_server


def calculate_absolute_humidity(_relative_humidity, _temperature):
    return (6.112 * ((17.67 * _temperature) / (_temperature + 243.5)) * _relative_humidity * 2.1674) / (273.15 + _temperature)


def get_readings(_sensor_connection):
    temperature = None
    relative_humidity = None
    absolute_humidity = None

    if _sensor_connection == "gpio":
        if sensor_version in sensor_args:
            relative_humidity, temperature = dht.read_retry(sensor_args[sensor_version], sensor_pin)

        if relative_humidity is not None and temperature is not None:
            absolute_humidity = calculate_absolute_humidity(relative_humidity, temperature)

    if _sensor_connection == "envirophat":
        temperature = weather.temperature()

    return temperature, relative_humidity, absolute_humidity


def update_metrics(_temperature, _relative_humidity, _absolute_humidity):
    if _temperature is not None:
        TEMPERATURE_GAUGE.labels(room).set("{0:0.1f}".format(_temperature))
    if _relative_humidity is not None:
        RELATIVE_HUMIDITY_GAUGE.labels(room).set("{0:0.1f}".format(_relative_humidity))
    if _absolute_humidity is not None:
        ABSOLUTE_HUMIDITY_GAUGE.labels(room).set("{0:0.2f}".format(_absolute_humidity))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Collects DHT/envirophat sensor readings and exports them as Prometheus metrics')
    parser.add_argument('--sensor-connection', type=str,
                        metavar='[gpio|envirophat]', required=True, help='Sensor connection type')
    parser.add_argument('--sensor-version', type=str, metavar='[11|22|2302]', help='DHT sensor version')
    parser.add_argument('--sensor-pin', type=str, metavar='N', help='GPIO Pin connected to the sensor')
    parser.add_argument('--room', type=str, metavar='<room name>', default="None", help='Named room for metric label')
    parser.add_argument('--listen-port', type=int, metavar='N', default=1337,
                        help='Listen port for Prometheus metrics endpoint')

    args = parser.parse_args()

    port = args.listen_port
    room = args.room

    sensor_args = {'11': dht.DHT11, '22': dht.DHT22, '2302': dht.AM2302}
    sensor_connection = args.sensor_connection
    sensor_pin = args.sensor_pin
    sensor_version = args.sensor_version

    if sensor_connection == "gpio":
        # TODO make the requirement of these args better
        if sensor_pin is None and sensor_version is None:
            print "--sensor-pin and --sensor-version required for GPIO connection"
            sys.exit(1)

        # envirophat does not measure humidity
        RELATIVE_HUMIDITY_GAUGE = Gauge('room_relative_humidity', 'Current room relative humidity', ['room'])
        ABSOLUTE_HUMIDITY_GAUGE = Gauge('room_absolute_humidity', 'Current room absolute humidity', ['room'])
    elif sensor_connection == "envirophat":
        # selectively import envirophat as it's init fails if there's no envirophat device
        from envirophat import weather
    else:
        print "Invalid sensor connection"
        sys.exit(1)

    TEMPERATURE_GAUGE = Gauge('room_temperature', 'Current room temperature', ['room'])

    print "Starting server on http://0.0.0.0:{}".format(port)
    start_http_server(port)

    try:
        while True:
            temperature, relative_humidity, absolute_humidity = get_readings(sensor_connection)
            update_metrics(temperature, relative_humidity, absolute_humidity)
            time.sleep(10)
    except KeyboardInterrupt:
        print "Exiting..."
        sys.exit(0)
