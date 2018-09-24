import time
import pytest
from bonsai_ai.exceptions import RetryTimeoutError


def test_reconnect(flaky_train_sim, monkeypatch):
    def _patched_sleep(backoff):
        return backoff
    monkeypatch.setattr(time, 'sleep', _patched_sleep)

    counter = 0
    while flaky_train_sim.run():
        if counter == 100:
            break
        counter += 1


@pytest.mark.xfail(raises=(RetryTimeoutError))
def test_reconnect_timeout(flaky_train_sim):
    flaky_train_sim._impl._sim_connection._retry_timeout_seconds = 1
    counter = 0
    while flaky_train_sim.run():
        if counter == 100:
            # Avoid infinite simulation loops and fail test
            assert False
        counter += 1


@pytest.mark.xfail(raises=(RetryTimeoutError))
def test_reconnect_user_does_not_want_to_reconnect(flaky_train_sim):
    flaky_train_sim._impl._sim_connection._retry_timeout_seconds = 0
    counter = 0
    while flaky_train_sim.run():
        if counter == 100:
            # Avoid infinite simulation loops and fail test
            assert False
        counter += 1


def test_sim_connection_constructor(train_sim):
    sim_connection = train_sim._impl._sim_connection
    assert(sim_connection._brain == train_sim.brain)
    assert(sim_connection._predict is train_sim.predict)
    assert(sim_connection._connection_attempts == 0)
    assert(sim_connection._retry_timeout_seconds == 3000)
    assert(sim_connection._maximum_backoff_seconds == 60)
    assert(sim_connection._timeout is None)
