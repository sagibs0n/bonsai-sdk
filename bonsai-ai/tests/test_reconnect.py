import time
import pytest
from bonsai_ai.exceptions import RetryTimeoutError, BonsaiServerError
from ws import set_unauthorized_mode, set_flaky_mode, set_fail_duration, \
    reset_count


def test_reconnect(train_sim, monkeypatch):
    set_flaky_mode(True)
    reset_count()

    def _patched_sleep(backoff):
        return backoff
    monkeypatch.setattr(time, 'sleep', _patched_sleep)

    counter = 0
    while train_sim.run():
        if counter == 100:
            break
        counter += 1


@pytest.mark.xfail(raises=(RetryTimeoutError), strict=True)
def test_reconnect_timeout(train_sim):
    set_flaky_mode(True)
    set_fail_duration(20)
    reset_count()
    train_sim._impl._sim_connection._retry_timeout_seconds = 1
    counter = 0
    while train_sim.run():
        if counter == 100:
            # Avoid infinite simulation loops and fail test
            assert False
        counter += 1


def test_reconnect_user_does_not_want_to_reconnect(train_sim, capsys):
    set_flaky_mode(True)
    reset_count()
    train_sim._impl._sim_connection._retry_timeout_seconds = 0
    counter = 0
    while train_sim.run():
        if counter == 100:
            # Avoid infinite simulation loops and fail test
            assert False
        counter += 1
    out, err = capsys.readouterr()
    assert err.count('Starting Training') == 1
    assert err.count('Websocket connection closed.') == 1


def test_reconnect_sim_does_not_exist(train_sim):
    train_sim._impl.name = "cartpole_simulatorX"
    enter_loop = False
    while train_sim.run():
        enter_loop = True
        break

    assert not enter_loop


def test_reconnect_http_error_401(train_sim, capsys):
    set_unauthorized_mode(True)
    counter = 0
    while train_sim.run():
        if counter == 100:
            assert False
        counter += 1
    out, err = capsys.readouterr()
    # Assert 401 occurs once and no reconnects attempts happen
    assert err.count('401: Unauthorized.') == 1


def test_reconnect_http_error_404(train_sim, capsys):
    train_sim.brain.config.username = 'bob'
    counter = 0
    while train_sim.run():
        if counter == 100:
            assert False
        counter += 1
    out, err = capsys.readouterr()
    # Assert 404 occurs once and no reconnects attempts happen
    assert err.count('404: Not Found') == 1


def test_sim_connection_constructor(train_sim):
    sim_connection = train_sim._impl._sim_connection
    assert sim_connection._brain == train_sim.brain
    assert sim_connection._predict is train_sim.predict
    assert sim_connection._connection_attempts == 0
    assert sim_connection._retry_timeout_seconds == 300
    assert sim_connection._maximum_backoff_seconds == 60
    assert sim_connection._timeout is None


def test_read_timeout_reconnect(train_sim, capsys):
    train_sim._impl._sim_connection.read_timeout_seconds = 0.000000000000001
    counter = 0
    while train_sim.run():
        if counter == 100:
            break
        if counter == 50:
            train_sim._impl._sim_connection.read_timeout_seconds = 240
        counter += 1
    out, err = capsys.readouterr()
    assert 'WS read took longer than' in err
    assert 'Starting Training' in err
    assert 'episode_start' in out
    assert 'simulate' in out
