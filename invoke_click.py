#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import random
import string
from os import environ

DATA_LEN = 6

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    if rc != 0:
        print("Connection Failed with result code {}".format(rc))
    else:
        print("Connected with result code {}".format(rc))
        topic = "{base_topic}{device_id}/garage_door_clicker/open/set".format(**userdata)
        data = ''.join(random.choice(string.ascii_lowercase) for i in range(DATA_LEN))
        print("Publishing click message")
        print(topic, data)
        client.publish(topic, data)

    client.disconnect()

def main(broker_host, broker_port, broker_username, broker_password, base_topic, device_id):
    # initialise mqtt client and register callbacks
    client = mqtt.Client()

    client.on_connect = on_connect

    # set username and password if given
    if broker_username and broker_password:
        client.username_pw_set(broker_username, broker_password)

    # save data to be used in the callbacks
    client.user_data_set({
            "base_topic": base_topic,
            "device_id": device_id
        })

    # start connection
    print("Connecting to mqtt broker {} on port {}".format(broker_host, broker_port))
    client.connect(broker_host, broker_port, 60)

    # Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
    client.loop_forever()

# ensure base topic always ends with a '/'
def base_topic_arg(s):
    s = str(s)
    if not s.endswith('/'):
        s = s + '/'
    return s

BASE_TOPIC_DEFAULT = "homie/"

def env_loader():
    abort_flag = False
    for env_name in ["BROKER_HOST", "BROKER_PORT", "BROKER_USERNAME", "BROKER_PASSWORD", "DEVICE_ID"]:
        if not environ.get(env_name):
            print("No environmental variable", env_name)
            abort_flag = True

    if not abort_flag:
        main(broker_host     = environ.get("BROKER_HOST"),
             broker_port     = int(environ.get("BROKER_PORT")),
             broker_username = environ.get("BROKER_USERNAME"),
             broker_password = environ.get("BROKER_PASSWORD"),
             base_topic      = base_topic_arg(environ.get("BASE_TOPIC", BASE_TOPIC_DEFAULT)),
             device_id       = environ.get("DEVICE_ID"))
    else:
        print("Cannot find all requirement environmental variables, aborting.")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='write a resource on a device')

    # specify arguments
    parser.add_argument('-l', '--broker-host',     type=str,            required=False,
                        help='host name or ip address of the MQTT broker', default="127.0.0.1")
    parser.add_argument('-p', '--broker-port',     type=int,            required=False,
                        help='port of the MQTT broker', default=1883)
    parser.add_argument('-u', '--broker-username', type=str,            required=False,
                        help='username used to authenticate with the MQTT broker')
    parser.add_argument('-d', '--broker-password', type=str,            required=False,
                        help='password used to authenticate with the MQTT broker')
    parser.add_argument('-t', '--base-topic',      type=base_topic_arg, required=False,
                        help='base topic of the homie devices on the broker', default=BASE_TOPIC_DEFAULT)
    parser.add_argument('-i', '--device-id',       type=str,            required=True,
                        help='homie device id')

    # workaround for http://bugs.python.org/issue9694
    parser._optionals.title = "arguments"

    # get and validate arguments
    args = parser.parse_args()

    # Invoke the business logic
    main(args.broker_host, args.broker_port, args.broker_username,
         args.broker_password, args.base_topic, args.device_id)
