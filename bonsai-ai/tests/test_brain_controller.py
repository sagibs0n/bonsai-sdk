import pytest
from ws_aiohttp import START_STOP_RESUME, METRICS, BRAIN_STATUS, BRAIN_INFO, \
     SIMS, CREATE_PUSH


def test_create_brain(brain_controller):
    assert brain_controller.create('cartpole', ink_str='ink') == CREATE_PUSH

def test_create_brain_inkling_file(brain_controller, temp_directory):
    with open('foo.ink', 'w') as f:
        f.write('inkling')
    assert brain_controller.create('cartpole', ink_file='foo.ink') == CREATE_PUSH

def test_push_inkling_str(brain_controller):
    assert brain_controller.push_inkling('cartpole', ink_str='ink') == CREATE_PUSH

def test_push_inkling_file(brain_controller, temp_directory):
    with open('foo.ink', 'w') as f:
        f.write('inkling')
    assert brain_controller.push_inkling('cartpole', ink_file='foo.ink') == CREATE_PUSH

def test_delete(brain_controller):
    assert brain_controller.delete('cartpole') == {}

def test_train_start(brain_controller):
    assert brain_controller.train_start('cartpole') == START_STOP_RESUME

def test_train_stop(brain_controller):
    assert brain_controller.train_stop('cartpole') == START_STOP_RESUME

def test_train_resume(brain_controller):
    assert brain_controller.train_resume('cartpole') == START_STOP_RESUME

def test_brain_status(brain_controller):
    assert brain_controller.status('cartpole') == BRAIN_STATUS

def test_brain_info(brain_controller):
    assert brain_controller.info('cartpole') == BRAIN_INFO

def test_sample_rate(brain_controller):
    assert brain_controller.sample_rate('cartpole') == 0

def test_simulator_info(brain_controller):
    assert brain_controller.simulator_info('cartpole') == SIMS

def test_training_episode_metrics(brain_controller):
    assert brain_controller.training_episode_metrics('cartpole') == METRICS

def test_test_episode_metrics(brain_controller):
    assert brain_controller.test_episode_metrics('cartpole') == METRICS

def test_iteration_metrics(brain_controller):
    assert brain_controller.iteration_metrics('cartpole') == METRICS

# Following tests test that errors do not raise exceptions in brain controller
@pytest.mark.parametrize('request_errors', ['connection'], indirect=True)
def test_controller_connection_error(request_errors, brain_controller, capsys):
    brain_controller.delete('cartpole')
    captured = capsys.readouterr()
    assert 'Unable to connect' in captured.err

@pytest.mark.parametrize('request_errors', ['timeout'], indirect=True)
def test_delete_timeout_error(request_errors, brain_controller, capsys):
    brain_controller.delete('cartpole')
    captured = capsys.readouterr()
    assert 'timed out' in captured.err

@pytest.mark.parametrize('request_errors', ['http'], indirect=True)
def test_delete_http_error(request_errors, brain_controller, capsys):
    brain_controller.delete('cartpole')
    captured = capsys.readouterr()
    assert 'Request failed' in captured.err
