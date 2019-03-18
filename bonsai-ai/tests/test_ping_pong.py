import time
import os
import json

def test_pong_sim(pong_sim):
    """
    Tests that pongs are received by our mock server.
    This test is contained in it's own file because it
    captures stdout output and checks that a received
    message was printed
    """
    pong_sim.brain.config._pong_interval = 1.0
    counter = 0
    while pong_sim.run():
        time.sleep(.1)
        if counter == 20:
            break
        counter += 1

    if os.path.exists('pong.json'):
        with open('pong.json', 'r') as infile:
            pong = json.load(infile)
        assert pong['PONG'] == 1
        os.remove('pong.json')
    else:
        assert False
