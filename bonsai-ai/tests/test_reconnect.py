import time
from bonsai_ai.exceptions import RetryTimeoutError
from bonsai_ai.proto.generator_simulator_api_pb2 import ServerToSimulator


def test_reconnect(flaky_train_sim, monkeypatch):
    def _patched_sleep(backoff):
        return backoff
    monkeypatch.setattr(time, 'sleep', _patched_sleep)

    counter = 0
    while flaky_train_sim.run():
        if counter == 100:
            break
        counter += 1

    flaky_train_sim.close()


def test_reconnect_timeout(flaky_train_sim):
    try:
        flaky_train_sim._impl._sim_connection._retry_timeout_seconds = .4
        counter = 0
        while flaky_train_sim.run():
            if counter == 100:
                # Avoid infinite simulation loops and fail
                assert False
            counter += 1
    except RetryTimeoutError as e:
        return
    finally:
        flaky_train_sim.close()

    assert False, "Reconnect didn't time out"


def test_reconnect_user_does_not_want_to_reconnect(flaky_train_sim, capsys):
    flaky_train_sim._impl._sim_connection._retry_timeout_seconds = 0
    counter = 0
    while flaky_train_sim.run():
        if counter == 100:
            # Avoid infinite simulation loops and fail test
            assert False
        counter += 1
    out, err = capsys.readouterr()
    print(err)
    assert err.count('Starting Training') == 1
    assert err.count('Websocket connection closed.') == 1
    flaky_train_sim.close()


def test_reconnect_sim_does_not_exist(train_sim):
    train_sim._impl.name = "cartpole_simulatorX"
    enter_loop = False
    while train_sim.run():
        enter_loop = True
        break

    assert not enter_loop
    train_sim.close()


def test_reconnect_http_error_401(auth_sim, capsys):
    counter = 0
    while auth_sim.run():
        if counter == 100:
            assert False
        counter += 1
    out, err = capsys.readouterr()
    # Assert 401 occurs once and no reconnects attempts happen
    assert err.count('401 - Unauthorized') == 1
    auth_sim.close()


def test_reconnect_http_error_404(train_sim, capsys):
    train_sim.brain.config.username = 'bob'
    counter = 0
    while train_sim.run():
        if counter == 100:
            assert False
        counter += 1

    train_sim.close()
    out, err = capsys.readouterr()
    # Assert 404 occurs once and no reconnects attempts happen
    assert err.count('404 - Not Found') == 1


def test_sim_connection_constructor(train_sim):
    sim_connection = train_sim._impl._sim_connection
    assert sim_connection._brain == train_sim.brain
    assert sim_connection._predict is train_sim.predict
    assert sim_connection._connection_attempts == 0
    assert sim_connection._retry_timeout_seconds == 300
    assert sim_connection._maximum_backoff_seconds == 60
    assert sim_connection._timeout is None


def test_reconnect_reset_rate_counter(flaky_train_sim, monkeypatch):
    def _patched_sleep(backoff):
        return backoff
    monkeypatch.setattr(time, 'sleep', _patched_sleep)

    while flaky_train_sim.run():
        if flaky_train_sim._impl._prev_message_type == \
           ServerToSimulator.ACKNOWLEDGE_REGISTER:
            break
    assert flaky_train_sim._reset_rate_counter is True

    while flaky_train_sim.run():
        if flaky_train_sim._impl._prev_message_type == ServerToSimulator.START:
            break
    assert flaky_train_sim._reset_rate_counter is False
    assert flaky_train_sim.iteration_rate == 0
    assert flaky_train_sim.episode_rate == 0
    flaky_train_sim.close()


def test_eofstream_reconnect(eofstream_sim, monkeypatch):
    def _patched_sleep(backoff):
        return backoff
    monkeypatch.setattr(time, 'sleep', _patched_sleep)

    counter = 0
    while eofstream_sim.run():
        if counter == 100:
            break
        counter += 1

    eofstream_sim.close()


def test_ws_error_msg_reconnect(error_msg_sim, monkeypatch):
    def _patched_sleep(backoff):
        return backoff
    monkeypatch.setattr(time, 'sleep', _patched_sleep)

    counter = 0
    while error_msg_sim.run():
        if counter == 100:
            break
        counter += 1

    error_msg_sim.close()
