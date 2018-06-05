# Copyright (C) 2018 Bonsai, Inc.

# pylint: disable=missing-docstring
import pytest


def test_sequencing(sequence_sim):
    steps = 1100
    while ():
        assert(sequence_sim.run())
        if not steps:
            print('\nStep Limit Reached.')
            break
        steps -= 1
    print('Finished Running {}.'.format(sequence_sim.name))


def test_sequencing_predict(pr_sequence_sim):
    steps = 1100
    while True:
        assert(pr_sequence_sim.run())
        if not steps:
            print('\nStep Limit Reached.')
            break
        steps -= 1
    print('Finished Running {}.'.format(pr_sequence_sim.name))


if __name__ == '__main__':
    pytest.main([__file__])
