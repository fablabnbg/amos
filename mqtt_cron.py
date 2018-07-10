#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from hx711 import HX711
import RPi.GPIO as GPIO
from datetime import datetime

mqtt_host = '192.168.178.63'
mqtt_port = 1883
mqtt_base = 'test/amos/tele/'

# defines format of MQTT payload
plset = '{{"time":"{time}",{data},"weightunit":"g"}}'

# defines format of a single sensor in payload
dataset = '"hx711-{hxno}":{{"weight":{weight},"raw":{raw},"offset":{offset},"scale_ratio":{ratio}}}'

# GPIO settings and parameters for HX711
#            Dat, Clk, Offset, Ratio 
hxconfig = ((  4,  18),
			( 17,  27),
			( 22,  23),
			( 24,  10),
			(  9,  25),
			( 11,   8),
			(  7,   5),
			(  6,  12),
			( 13,  16),
			( 19,  26),
			( 20,  21, 348000, 19.369),
			)

hxno = 0
data = []

for item in hxconfig:
	hx = HX711(dout_pin=item[0], pd_sck_pin=item[1], gain_channel_A=128, select_channel='A')
	
	# parameters could be set in object but as we also want to utilize raw-values
	# we calculate by ourselfs later. This block stays for reference
	#hx.set_offset(offset=item[2])
	#hx.set_scale_ratio(scale_ratio=item[3])

	raw = int(hx.get_raw_data_mean(10))

	if raw:
		weight = int((raw - item[2]) / item[3])
		if weight < 0: weight = 0

		data.append(dataset.format(hxno=hxno, weight=weight, raw=raw, offset=item[2], ratio=item[3]))


	# increase sensor number
	hxno += 1


if not data: data.append('""')

payload = plset.format(time=datetime.now().replace(microsecond=0).isoformat(), data=','.join(data))

client = mqtt.Client()
client.connect(mqtt_host, mqtt_port, keepalive=60)
client.publish(mqtt_base+'sensor', payload, 0, False)

GPIO.cleanup()
