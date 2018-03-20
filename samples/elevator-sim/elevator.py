import itertools
import random

import simpy


RANDOM_SEED = 42
BUILDING_SIZE = 3  # number of floors
ELEVATOR_SPEED = 1  # seconds per floor
ELEVATOR_WAIT = 10  # time to board

T_INTER = [20, 100]        # Create a person every [min, max] seconds
SIM_TIME = 180             # Simulation time in seconds

OPEN = 0
UP = 1
DOWN = 2


def person(name, env, floors, score):
    """A person who wants to go to a floor
    It accesses an entry door, followed by an exit door.
    """
    source = random.randrange(0, BUILDING_SIZE)
    offset = random.randrange(1, BUILDING_SIZE-1)
    dest = ((source + offset) % BUILDING_SIZE)

    start = env.now
    person = {'name': name, 'start': start, 'from': source, 'to': dest}
    score.append(person)
    # print('%s (%d to %d) at %d' % (name, source, dest, start))
    with floors[source].request() as req:
        yield req

        # print('%s boarded in %d seconds.' % (name, env.now - start))
        person['boarded'] = True

    with floors[dest].request() as req:
        yield req

        end = env.now
        # print('%s arrived in %d seconds.' % (name, end - start))
        person['end'] = end


def claim(floors, reqs):
    """ claim all floors """
    reqs.extend([f.request() for f in floors])
    for r in reqs:
        yield r


def elevator(env, floors, state, store):
    """
    elevator logic - claims all the floors, then cycle through them
    releasing one at a time
    """
    reqs = []
    yield from claim(floors, reqs)

    while True:
        yield from elevator_one(env, floors, state, store, reqs)


def elevator_one(env, floors, state, store, reqs):
    m = yield store.get()
    # print('elevator saw command: {}'.format(m))
    if m == OPEN:
        i = state.floor
        # print('elevator on floor %d at %d' % (i, env.now))
        floors[i].release(reqs[i])
        yield env.timeout(10)
        reqs[i] = floors[i].request()
        yield reqs[i]
    elif m == UP:
        state.up()
        yield env.timeout(1)
    elif m == DOWN:
        state.down()
        yield env.timeout(1)


class Lstate():
    def __init__(self):
        self.floor = 0
        self.command = None

    def down(self):
        self.floor = self.floor - 1
        if self.floor < 0:
            self.floor = 0

    def up(self):
        self.floor = self.floor + 1
        if self.floor >= BUILDING_SIZE:
            self.floor = BUILDING_SIZE-1


def elevator_store(store):
    for move in elevator_gen():
        yield store.put(move)


def elevator_gen():
    """ A default algorithm """
    while True:
        yield OPEN
        for i in range(0, BUILDING_SIZE-1):
            yield UP
            yield OPEN
        for i in range(0, BUILDING_SIZE-1):
            yield DOWN


def person_generator(env, floors, score):
    """Generate new people for the floors."""
    for i in itertools.count():
        yield env.timeout(random.randint(*T_INTER))
        env.process(person('Mr %d' % i, env, floors, score))


def _format_person(person, time):
    """ a string to describe a person (name + wait time) """
    name = person['name']
    start = person['start']
    end = person.get('end', time)
    return '{}({})'.format(name.replace('Dr ', ''), end-start)


def display(time, people, state):
    # header (time, last 10 people)
    complete = [p for p in people if p.get('end', None)]
    # formatted = [_format_person(p, time) for p in complete[-5:]]
    times = [p['end']-p['start'] for p in complete[-5:]]
    print('{:>4}s '.format(time), end='')

    # display each floor
    on_elevator = [p for p in people
                   if (p.get('boarded', None) and not p.get('end', None))]
    waiting = [p for p in people if not p.get('boarded', None)]
    for floor in range(0, BUILDING_SIZE):
        wait_floor = [p for p in waiting if p['from'] == floor]
        print('{}: {:>2}|'.format(floor, len(wait_floor)), end='')
        # render the elevator or a blank space
        if floor == state.floor:
            print('[_{}_] '.format(len(on_elevator)), end='')
        else:
            print('      ', end='')
    # give recent complete times
    print(' recent: {}'.format(times))


def display_process(env, people, state):
    while True:
        yield env.timeout(100)
        display(env.now, people, state)


def count_waiting(people):
    waiting = [p for p in people if 'end' not in p]
    return len(waiting)

if __name__ == "__main__":
    # Setup and start the simulation
    print('Elevator simulator')
    random.seed(RANDOM_SEED)

    # Create environment and start processes
    env = simpy.Environment()
    floors = [simpy.Resource(env, 1) for _ in range(0, BUILDING_SIZE)]
    state = Lstate()
    store = simpy.Store(env, 1)
    people = []
    reqs = []
    env.process(claim(floors, reqs))
    env.process(elevator_store(store))
    # ep = env.process(elevator(env, floors, state, store))
    ep = env.process(elevator_one(env, floors, state, store, reqs))
    env.process(person_generator(env, floors, people))
    # env.process(display_process(env, people, state))

    # Execute!
    while(env.now < SIM_TIME):
        env.run(until=ep)
        ep = env.process(elevator_one(env, floors, state, store, reqs))
        display(env.now, people, state)
