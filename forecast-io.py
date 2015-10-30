#!/usr/bin/env python

# Jan-Piet Mens, February 2013

import paho.mqtt.client as paho
import urllib2
import json
import time
import datetime
import sys

apikey = 'c114129d5fd0df9c7e68761a8d66b6bd'
lat = "38.14465"
lon = "23.85891"

broker = '127.0.0.1'
broker_port = 1883
root_topic = 'openhab/home/weather'
delay = (10 * 60)
retain=True

def get_forecastio(lat, lon, apikey, tics, units="si"):

    URL = 'https://api.forecast.io/forecast/%s/%s,%s,%s?units=%s' % (
                apikey, lat, lon, tics, units)
    data = None
    try:
        response = urllib2.urlopen(URL)
        data = json.loads(response.read())
    except Exception, e:
        print "Cannot get or decode %s: %s" % (URL, str(e))

    return data

def data2topics(mqttc, branch, data, keys=None):

    for k in data.keys():
        if keys is not None and k not in keys:
            continue
        topic = '%s/%s/%s' % (root_topic, branch, k)
        payload = data[k]
        mqttc.publish(topic, str(payload), qos=0, retain=retain)

#        print "%s: %s" % (topic, payload)

        # Also create ISO timestamp and HH:MM format for time values
        if 'Time' in k or 'time' in k:
            topic_iso = '%s-iso' % topic
            dt = datetime.datetime.fromtimestamp(int(payload))
            mqttc.publish(topic_iso, str(dt.isoformat()), qos=0, retain=retain)

            topic_hhmm = '%s-hhmm' % topic
            hh_mm = dt.strftime('%H:%M')
            mqttc.publish(topic_hhmm, str(hh_mm), qos=0, retain=retain)
if __name__ == '__main__':

    keys = [
                'cloudCover',
                'temperatureMin',
                'summary',
                'temperatureMax',
                'moonPhase',
                'sunsetTime',
                'precipProbability',
                'icon',
                'humidity',
                'windSpeed',
                'time',
                'precipIntensity',
                'sunriseTime',
    ]

    mqttc = paho.Client('forecastio1', clean_session=True)
    mqttc.connect(broker, broker_port, 60)
    mqttc.loop_start()

    while True:
        try:
            tics = int(time.time())
            data = get_forecastio(lat, lon, apikey, tics)
            if data is not None:
                data2topics(mqttc, 'current', data['currently'], None)
#		print "Published"
                daily_data = data['daily']['data'][0]
                data2topics(mqttc, 'today', daily_data, keys)

            morrow = tics + (24 * 60 * 60)
            data = get_forecastio(lat, lon, apikey, morrow)
            if data is not None:
                daily_data = data['daily']['data'][0]
                data2topics(mqttc, 'tomorrow', daily_data, keys)
#		print "Published"
            time.sleep(delay)
        except KeyboardInterrupt:
            break
        except:
            raise
    mqttc.loop_stop()
    mqttc.disconnect()
