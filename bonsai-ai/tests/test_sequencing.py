# Copyright (C) 2018 Bonsai, Inc.

# pylint: disable=missing-docstring
import pytest


def test_sequencing(sequence_sim):
    print(sequence_sim.brain.config)
    print(sequence_sim.brain)
    steps = 1100
    while (sequence_sim.run()):
        if not steps:
            print('\nStep Limit Reached.')
            break
        steps -= 1
    print('Finished Running {}.'.format(sequence_sim.name))

if __name__ == '__main__':
    pytest.main([__file__])
