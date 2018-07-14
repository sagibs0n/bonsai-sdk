import gym
import sys
from bonsai_ai import Brain, Config
from bonsai_gym import GymSimulator
from bonsai_ai.logger import Logger
from bonsai_ai import EpisodeStartEvent, SimulateEvent, \
    EpisodeFinishEvent, FinishedEvent, UnknownEvent

from star import state, terminal, action, reward, params

log = Logger()


class CartPole(GymSimulator):
    # Environment name, from openai-gym
    environment_name = 'CartPole-v0'

    # simulator name from Inkling
    # Example Inkling:
    #   curriculum balance_curriculum
    #       train balance
    #       with simulator cartpole_simulator
    #       ....
    simulator_name = 'cartpole_simulator'

    def render(self):
        self._env.render()


class CartPoleTrainer(object):

    def __init__(self, sim):
        self._sim = sim
        self._episode_count = 0
        self._episode_reward = 0

    def run(self):
        event = self._sim.get_next_event()

        if isinstance(event, EpisodeStartEvent):
            log.event("Episode Start")
            observation = self._sim.gym_episode_start(params(event))
            event.initial_state = state(observation)

        elif isinstance(event, SimulateEvent):
            log.event("Simulate")
            obs, rwd, done, _ = self._sim.gym_simulate(action(event))
            event.state = state(obs)
            event.reward = reward(rwd)
            event.terminal = terminal(done)
            self._episode_reward += rwd
            self._sim.render()

        elif isinstance(event, EpisodeFinishEvent):
            log.event("Episode Finish")
            print("Episode {} reward: {}".format(
                self._episode_count, self._episode_reward))
            self._episode_count += 1
            self._episode_reward = 0

        elif isinstance(event, FinishedEvent):
            log.event("Finished")
            return False
        elif event is None:
            return False

        return True


if __name__ == '__main__':
    # create a brain, openai-gym environment, and simulator
    config = Config(sys.argv)
    brain = Brain(config)
    sim = CartPole(brain)
    trainer = CartPoleTrainer(sim)
    while trainer.run():
        pass
