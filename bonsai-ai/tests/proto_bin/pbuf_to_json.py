# Copyright (C) 2018 Bonsai, Inc.

from bonsai_ai.proto.generator_simulator_api_pb2 import ServerToSimulator
from google.protobuf.json_format import MessageToJson
import json
import argparse

N_MESSAGES = 8

# This script will scrape pwd for some files that no longer exist.
# When they existed, they contained serialized versions of the protobuf
# messages that define our wire protocol. They were collected from a
# live cartpole simulator instance during simulation.
# This script was intended to collect the messages from their respective
# files, build a JSON object, and write it to a file for use during unit
# testing. I'm leaving this here on the off chance that this code is
# needed again in future. Note that everything, including filenames, is
# hard coded.

# usage: python pbuf_to_json.py <outfile>


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('fname', metavar='outfile', nargs=1)
    args = parser.parse_args()

    _msg_files = {
        ServerToSimulator.ACKNOWLEDGE_REGISTER: "_on_acknowledge_register",
        ServerToSimulator.SET_PROPERTIES: "_on_set_properties",
        ServerToSimulator.START: "_on_start",
        ServerToSimulator.PREDICTION: "_on_prediction",
        ServerToSimulator.STOP: "_on_stop",
        ServerToSimulator.RESET: "_on_reset"
    }

    _other_msg_types = [
        ServerToSimulator.UNKNOWN,
        ServerToSimulator.FINISHED
    ]

    blob = [None] * N_MESSAGES

    for mtype, fname in _msg_files.items():
        with open(fname, 'rb') as f:
            msg = ServerToSimulator()
            b = f.read()
            msg.ParseFromString(b)
            j = MessageToJson(msg)
            data = json.loads(j)
            blob[mtype] = data

    for mtype in _other_msg_types:
        msg = ServerToSimulator()
        msg.message_type = mtype
        j = MessageToJson(msg)
        data = json.loads(j)
        blob[mtype] = data

    with open(args.fname[0], 'w') as f:
        blob_str = json.dumps(blob, indent=2)
        f.write(blob_str)
