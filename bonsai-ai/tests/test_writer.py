# Copyright (C) 2018 Bonsai, Inc.

import csv
import json
import os
import io
import sys
from bonsai_ai.proto.generator_simulator_api_pb2 import ServerToSimulator


def test_json_writing(record_json_sim, temp_directory):
    while record_json_sim._impl._prev_message_type != \
          ServerToSimulator.RESET:
        record_json_sim.record_append({'foo': 23}, 'bar')
        record_json_sim.run()

    assert os.path.exists(record_json_sim.brain.config.record_file)
    with open(record_json_sim.brain.config.record_file, 'r') as f:
        content = [l.strip() for l in f.readlines()]

    assert len(content) > 0
    json_content = [json.loads(l) for l in content]
    assert len(json_content) == len(content)

    for l in json_content:
        if l['sim_id'] is not None:
            assert l['sim_id'] == 270022238
        assert l['bar.foo'] == 23

    record_json_sim.writer.close()
    record_json_sim.close()
    os.remove(record_json_sim.brain.config.record_file)


def test_csv_writing(record_csv_sim, temp_directory):
    while record_csv_sim._impl._prev_message_type != \
          ServerToSimulator.RESET:
        record_csv_sim.record_append({'foo': 23}, 'bar')
        record_csv_sim.run()

    assert os.path.exists(record_csv_sim.brain.config.record_file)

    with io.open(record_csv_sim.brain.config.record_file, newline='') as f:
        reader = csv.reader(f)
        if sys.version_info < (3, ):
            # python 2
            header = reader.next()
        else:
            # python 3
            header = next(reader)

        assert 'sim_id' in header
        assert 'bar.foo' in header

        id_idx = header.index('sim_id')
        custom_idx = header.index('bar.foo')
        # for row in reader:
        #     print(row)

        # assert False

        for row in reader:
            if '270022238' in row:
                assert id_idx == row.index('270022238')
            assert '23' in row
            assert custom_idx == row.index('23')

    record_csv_sim.writer.close()
    record_csv_sim.close()
    os.remove(record_csv_sim.brain.config.record_file)


def test_file_change(record_csv_sim, temp_directory):
    os.mkdir("sub")
    while record_csv_sim._impl._prev_message_type != ServerToSimulator.RESET:
        if record_csv_sim._impl._prev_message_type == \
           ServerToSimulator.PREDICTION:
            record_csv_sim.record_file = "./sub/bazqux.csv"
        record_csv_sim.record_append({'foo': 23}, 'bar')
        record_csv_sim.run()

    assert os.path.exists(record_csv_sim.brain.config.record_file)

    with io.open(record_csv_sim.brain.config.record_file, newline='') as f:
        reader = csv.reader(f)
        if sys.version_info < (3, ):
            # python 2
            header = reader.next()
        else:
            # python 3
            header = next(reader)

        assert 'sim_id' in header
        assert 'bar.foo' in header

        id_idx = header.index('sim_id')
        custom_idx = header.index('bar.foo')

        for row in reader:
            if '270022238' in row:
                assert id_idx == row.index('270022238')
            assert '23' in row
            assert custom_idx == row.index('23')

    os.remove(record_csv_sim.brain.config.record_file)

    assert os.path.exists("./sub/bazqux.csv")
    with io.open("./sub/bazqux.csv", newline='') as f:
        reader = csv.reader(f)
        if sys.version_info < (3, ):
            # python 2
            header = reader.next()
        else:
            # python 3
            header = next(reader)

        assert 'sim_id' in header
        assert 'bar.foo' in header

        id_idx = header.index('sim_id')
        custom_idx = header.index('bar.foo')

        for row in reader:
            if '270022238' in row:
                assert id_idx == row.index('270022238')
            assert '23' in row
            assert custom_idx == row.index('23')

    record_csv_sim.writer.close()
    record_csv_sim.close()
    os.remove("./sub/bazqux.csv")
    os.rmdir("sub")


def test_predict_mode_record(record_csv_predict, temp_directory):
    os.mkdir("sub")
    rcp = record_csv_predict
    sim_steps = 100
    while sim_steps:
        rcp.run()
        sim_steps -= 1

    assert os.path.exists(rcp.brain.config.record_file)

    with io.open(rcp.brain.config.record_file, newline='') as f:
        reader = csv.reader(f)
        if sys.version_info < (3, ):
            # python 2
            header = reader.next()
        else:
            # python 3
            header = next(reader)

        assert 'sim_id' in header

    record_csv_predict.writer.close()
    record_csv_predict.close()
    os.remove(rcp.brain.config.record_file)
    os.rmdir("sub")
