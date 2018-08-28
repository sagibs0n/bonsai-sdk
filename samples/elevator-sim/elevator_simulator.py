""" elevator simulator, in sdk2 simulation api """

import sys
import argparse
import simpy
import elevator
from bonsai_ai import Simulator, Brain, Config


BUILDING_SIZE = elevator.BUILDING_SIZE
SIM_TIME = elevator.SIM_TIME


def doit(store, command):
    # print('storing command: {}'.format(command))
    if not store.items:
        yield store.put(command)


class ElevatorSimulator(Simulator):

    def episode_start(self, parameters=None):
        print('called episode_start')
        self.env = env = simpy.Environment()
        floors = [simpy.Resource(env, 1) for _ in range(0, BUILDING_SIZE)]
        store = simpy.Store(env, 1)
        state = elevator.Lstate()
        person_score = []
        reqs = []
        env.process(elevator.claim(floors, reqs))
        env.process(elevator.person_generator(env, floors, person_score))
        env.process(elevator.display_process(env, person_score, state))

        # We use the single step version of elevator (elevator_one)
        # this allows the simulator to run until the elevator uses a command.
        ep = env.process(
            elevator.elevator_one(env, floors, state, store, reqs))

        self.floors = floors
        self.store = store
        self.state = state
        self.person_score = person_score
        self.reqs = reqs
        self.ep = ep

        return self._get_state()

    def simulate(self, action):
        # TODO - sounds like previous state should replace the internal state..
        command = action['command']
        env = self.env
        # print('[advance]', end='')
        # print('command: {}'.format(command))
        self.state.command = command

        # pass our command to a resource by way of this doit() method
        env.process(doit(self.store, command))

        env.run(until=self.ep)
        self.ep = env.process(elevator.elevator_one(
            self.env, self.floors, self.state, self.store, self.reqs))
        # print('stepped to {}'.format(env.now))

        state = self._get_state()
        done = self._get_done()

        # only calculate reward for training mode
        if not self.predict:
            reward = self._elevator_objective()
        else:
            reward = 0

        return state, reward, done

    def _get_state(self):
        """ return the current state of the simulation """

        # print('[get_state]', end='')

        # if a floor is requested, state=1
        values = [min(len(q.queue), 1) for q in self.floors]
        state = {'Floor{}'.format(ix+1): v for ix, v in enumerate(values)}
        state['Position'] = self.state.floor
        # print(state)

        return state

    def _get_done(self):
        self.done = done = self.env.now > SIM_TIME
        return done

    def _elevator_objective(self):
        # print('[objective]', end='')
        waiting = elevator.count_waiting(self.person_score)
        # print("returning score %d for %d people" % (active, len(scores)))

        # return as negative because the simulator maximizes this value.
        return -waiting


def main():
    config = Config(sys.argv)

    brain = Brain(config)

    sim = ElevatorSimulator(brain, 'elevator_simulator')
    while sim.run():
        continue

    print('finished.')


if __name__ == "__main__":
    main()
