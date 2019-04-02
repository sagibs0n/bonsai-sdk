import bonsai_ai
from random import randint
from time import clock
import sys


class BasicSimulator(bonsai_ai.Simulator):

    def episode_start(self, parameters):
        print("episode_start")
        # pull the config parameters
        test_number = parameters["test_number"]
        test_double = parameters["test_double"]
        test_float  = parameters["test_float"]
        test_int64  = parameters["test_int64"]
        test_int32  = parameters["test_int32"]
        test_uint64 = parameters["test_uint64"]
        test_uint32 = parameters["test_uint32"]
        #test_bool   = parameters["test_bool"]
        #test_string = parameters["test_string"]

        return {
            "test_number": test_number,
            "test_double": test_double,
            "test_float": test_float,
            "test_int64": test_int64,
            "test_int32": test_int32,
            "test_uint64": test_uint64,
            "test_uint32": test_uint32,
            #"test_bool": test_bool,
            #"test_string": 0,
            }

    def simulate(self, action):
        print("simulate")
        state = {
            "test_number": 0,
            "test_double": 1,
            "test_float": 2,
            "test_int64": 3,
            "test_int32": 4,
            "test_uint32": 5,
            "test_uint32": 6,
            #"test_bool": True,
            #"test_string": 0,
            }

        terminal = self.iteration_count > 5
        reward = 1.0
        return (state, reward, terminal)

    def episode_finish(self):
        print("episode_finish")
        sys.exit()


if __name__ == "__main__":
    config = bonsai_ai.Config()    
    brain = bonsai_ai.Brain(config)

    sim = BasicSimulator(brain, "the_simulator")
    while sim.run():
        continue
