from bonsai_ai.proto.generator_simulator_api_pb2 import ServerToSimulator
# from bonsai_ai.exceptions import SimulateError, EpisodeStartError, \
#     SimStateError
from bonsai_ai.exceptions import SimStateError


def test_simulate_error(train_sim, bonsai_ws, monkeypatch):
    def _simulate(action):
        raise RuntimeError("Boo")
    monkeypatch.setattr(train_sim, 'simulate', _simulate)
    try:
        while train_sim._impl._prev_message_type != ServerToSimulator.RESET:
            train_sim.run()
    except RuntimeError as e:
        assert str(e).find("Boo") >= 0
    else:
        assert False
    finally:
        train_sim.close()


def test_episode_start_error(train_sim, bonsai_ws, monkeypatch):
    def _episode_start(params):
        raise RuntimeError("Hiss")
    monkeypatch.setattr(train_sim, 'episode_start', _episode_start)
    try:
        while train_sim._impl._prev_message_type != ServerToSimulator.RESET:
            train_sim.run()
    except RuntimeError as e:
        assert str(e).find("Hiss") >= 0
    else:
        assert False
    finally:
        train_sim.close()


def test_simulate_bad_state(train_sim, bonsai_ws, monkeypatch):
    def _simulate(action):
        state = {
            "velocity": 0.0,
            "angle": 0.0,
            "rotation": 0.0
        }
        return (state, 1.0, True)
    monkeypatch.setattr(train_sim, 'simulate', _simulate)
    try:
        while train_sim._impl._prev_message_type != ServerToSimulator.RESET:
            train_sim.run()
    except SimStateError as e:
        assert str(e).find("position") >= 0
    else:
        assert False
    finally:
        train_sim.close()


def test_episode_start_bad_state(train_sim, bonsai_ws, monkeypatch):
    def _episode_start(parames):
        return {
            "position": 0.0,
            "velocity": "should be a float",
            "angle": 0.0,
            "rotation": 0.0
        }
    monkeypatch.setattr(train_sim, 'episode_start', _episode_start)
    try:
        while train_sim._impl._prev_message_type != ServerToSimulator.RESET:
            train_sim.run()
    except SimStateError as e:
        assert str(e).find("should be a float") >= 0
    else:
        assert False
    finally:
        train_sim.close()


def test_error_logging(train_sim, bonsai_ws, monkeypatch, capsys):
    def _simulate(action):
        raise RuntimeError("Boo")
    monkeypatch.setattr(train_sim, 'simulate', _simulate)
    try:
        while train_sim._impl._prev_message_type != ServerToSimulator.RESET:
            train_sim.run()
    except RuntimeError as e:
        out, err = capsys.readouterr()
        assert err.find("RuntimeError") >= 0
    else:
        assert False
    finally:
        train_sim.close()
