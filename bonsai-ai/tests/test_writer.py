# Copyright (C) 2018 Bonsai, Inc.

import csv
import json
import os
import io

from bonsai_ai.proto.generator_simulator_api_pb2 import ServerToSimulator


def test_json_writing(record_json_sim):
    while record_json_sim._impl._prev_message_type != \
          ServerToSimulator.RESET:
        record_json_sim.run()

    assert os.path.exists(record_json_sim.brain.config.record_file)
    with open(record_json_sim.brain.config.record_file, 'r') as f:
        content = [l.strip() for l in f.readlines()]

    assert len(content) > 0
    json_content = [json.loads(l) for l in content]
    assert len(json_content) == len(content)

    for l in json_content:
        # print("then the content: {}".format(l))
        assert l['sim_id'] == 270022238
        assert l['bar.foo'] == 23

    os.remove(record_json_sim.brain.config.record_file)


def test_csv_writing(record_csv_sim):
    while record_csv_sim._impl._prev_message_type != \
          ServerToSimulator.RESET:
        record_csv_sim.run()

    assert os.path.exists(record_csv_sim.brain.config.record_file)

    with io.open(record_csv_sim.brain.config.record_file, newline='') as f:
        reader = csv.reader(f)
        try:
            # python 2
            header = reader.next()
        except Exception as e:
            # python 3
            header = next(reader)

        assert 'sim_id' in header
        assert 'bar.foo' in header

        id_idx = header.index('sim_id')
        custom_idx = header.index('bar.foo')

        for row in reader:
            assert '270022238' in row
            assert id_idx == row.index('270022238')
            assert '23' in row
            assert custom_idx == row.index('23')

    os.remove(record_csv_sim.brain.config.record_file)


def test_file_change(record_csv_sim, tmpdir):
    os.mkdir("sub")
    while record_csv_sim._impl._prev_message_type != ServerToSimulator.RESET:
        if record_csv_sim._impl._prev_message_type == \
           ServerToSimulator.PREDICTION:
            record_csv_sim.record_file = "./sub/bazqux.csv"
        record_csv_sim.run()

    assert os.path.exists(record_csv_sim.brain.config.record_file)

    with io.open(record_csv_sim.brain.config.record_file, newline='') as f:
        reader = csv.reader(f)
        try:
            # python 2
            header = reader.next()
        except Exception as e:
            # python 3
            header = next(reader)

        assert 'sim_id' in header
        assert 'bar.foo' in header

        id_idx = header.index('sim_id')
        custom_idx = header.index('bar.foo')

        for row in reader:
            assert '270022238' in row
            assert id_idx == row.index('270022238')
            assert '23' in row
            assert custom_idx == row.index('23')

    os.remove(record_csv_sim.brain.config.record_file)

    assert os.path.exists("./sub/bazqux.csv")
    with io.open("./sub/bazqux.csv", newline='') as f:
        reader = csv.reader(f)
        try:
            # python 2
            header = reader.next()
        except Exception as e:
            # python 3
            header = next(reader)

        assert 'sim_id' in header
        assert 'bar.foo' in header

        id_idx = header.index('sim_id')
        custom_idx = header.index('bar.foo')

        for row in reader:
            print(row)
            assert '270022238' in row
            assert id_idx == row.index('270022238')
            assert '23' in row
            assert custom_idx == row.index('23')

    os.remove("./sub/bazqux.csv")
    os.rmdir("sub")


def test_predict_mode_record(record_csv_predict, tmpdir):
    os.mkdir("sub")
    rcp = record_csv_predict
    while rcp._impl._prev_message_type != ServerToSimulator.FINISHED:
        rcp.run()

    assert os.path.exists(rcp.brain.config.record_file)

    with io.open(rcp.brain.config.record_file, newline='') as f:
        reader = csv.reader(f)
        try:
            # python 2
            header = reader.next()
        except Exception as e:
            # python 3
            header = next(reader)

        assert 'sim_id' in header

    os.remove(rcp.brain.config.record_file)
    os.rmdir("sub")
