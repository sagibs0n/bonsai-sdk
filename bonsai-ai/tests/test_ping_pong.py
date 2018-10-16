import time

def test_train_sim(train_sim, capsys):
    """ 
    Tests that pings are received by our mock server.
    This test is contained in it's own file because it
    captures stdout output and checks that a received
    message was printed
    """
    train_sim.brain.config.ping_interval = 1.0
    counter = 0
    while train_sim.run():
        time.sleep(.1)
        if counter == 20:
            break
        counter += 1
    out, err = capsys.readouterr()
    assert('Received PING: ' in out)
