# Simulator Class

>![Simulator state image](../images/simulator_state.svg)

This class is used to interface with the server while training or running predictions against
a **BRAIN**. It is an abstract base class, and to use it a developer must create a subclass.

The `Simulator` class is closely related to the **Inkling** file that is associated with
the **BRAIN**. The name used to construct `Simulator` must match the name of the simulator
in the *Inkling* file.

There are two main methods that you must override, `episode_start` and `simulate`. The diagram
demonstrates how these are called during training.

## Simulator(brain, name)

> Example Inkling:

```inkling
simulator my_simulator(Config)
    action (Action)
    state (State)
end
```

> Example code:

```cpp
class MySimulator : public Simulator {
 public:
    explicit BasicSimulator(std::shared_ptr<Brain> brain, string name )
        : Simulator(move(brain), move(name)) {
            // your simulator init code goes here.
        }

    void episode_start(const bonsai::InklingMessage& params,
        bonsai::InklingMessage& initial_state) override {
            // your simulation episode reset/init code.
        }

    void simulate(const bonsai::InklingMessage& action,
        bonsai::InklingMessage& state,
        float& reward,
        bool& terminal) override {
            // your simulation stepping code.
        }
};

...

auto config = make_shared<bonsai::Config>(argc, argv);
auto brain = make_shared<bonsai::Brain>(config);
MySimulator sim(brain, "my_simulator");

...

```

```python
class MySimulator(bonsai_ai.Simulator):
    def __init__(brain, name):
        super().__init__(brain, name)
        # your sim init code goes here.

    def episode_start(self, parameters=None):
        # your reset/init code goes here.
        return my_state

    def simulate(self, action):
        # your simulation stepping code goes here.
        return (my_state, my_reward, is_terminal)

...

config = bonsai_ai.Config(sys.argv)
brain = bonsai_ai.Brain(config)
sim = MySimulator(brain, "my_simulator")

...
```

Serves as a base class for running simulations. You should create a subclass
of Simulator and implement the `episode_start` and `simulate` callbacks.

| Argument | Description |
| ---      | ---         |
| `brain`  |  A Brain object for the BRAIN you wish to train against. |
| `name`   |  The name of simulator as specified in the Inkling for the BRAIN. |

## Brain brain()
```cpp
std::cout << sim.brain() << endl;
```

```python
print(sim.brain)
```

Returns the BRAIN being used for this simulation.

## string name()
```cpp
std::cout << "Starting " << sim.name() << endl;
```

```python
print("Starting ", sim.name)
```
Returns the simulator name that was passed in when constructed.

## bool predict()
```cpp
void MySimulator::simulate(const bonsai::InklingMessage& action,
                    bonsai::InklingMessage& state, float& reward, bool& terminal) {
    if (predict() == false) {
        // calculate reward...
    }

    ...
}
```

```python
def simulate(self, action):
    if self.predict is False:
        # calculate reward...

    ...
```
Returns a value indicating whether the simulation is set up to run in predict mode or training mode.

## string objective_name()
```cpp
void MySimulator::episode_start(const bonsai::InklingMessage& params,
                                bonsai::InklingMessage& initial_state) {
    cout << objective_name() << endl;
    ...
}
```

```python
def episode_start(self, params):
    print(self.objective_name)
    ...
```
Property accessor that returns the name of the current objective from Inkling.
The objective may be updated before `episode_start` is called. When running
for prediction and during start up, objective will return an empty std::string.

## episode_start(parameters, initial_state)

> Example Inkling:

```inkling
schema Config
    UInt8 start_angle
end

schema State
    Float32 angle,
    Float32 velocity
end
```

> Example code:

```cpp
void MySimulator::episode_start(const bonsai::InklingMessage& params,
                                bonsai::InklingMessage& initial_state) {
    // training params are only passed in during training
    if (predict() == false) {
        cout << objective_name() << endl;
        angle = params.get_float32("start_angle");
    }

    initial_state.set_float32("velocity", velocity);
    initial_state.set_float32("angle",    angle);
}
```

```python
def episode_start(self, params):
    # training params are only passed in during training
    if self.predict == False:
        print(self.objective_name)
        self.angle = params.start_angle

    initial = {
        "angle": self.angle,
        "velocity": self.velocity,
    }
    return initial
```

| Argument        | Description |
| ---             | ---         |
| `parameters`    | InklingMessage of episode initialization parameters as defined in inkling. `parameters` will be populated if a training session is running. |
| `initial_state` | Output InklingMessage. The subclasser should populate this message with the initial state of the simulation. |

This callback passes in a set of initial parameters and expects an initial state in return
for the simulator. Before this callback is called, the property `objective_name` will be
updated to reflect the current objective for this episode.

This call is where a simulation should be reset for the next round.

The default implementation will throw an exception.

## simulate(action, state, reward, terminal)

> Example Inkling:

```inkling
schema Action
    Int8{0, 1} delta
end
```

> Example code:

```cpp
void MySimulator::simulate(const bonsai::InklingMessage& action,
                           bonsai::InklingMessage& state, float& reward, bool& terminal) {
    velocity = velocity - action.get_int8("delta");
    terminal = (velocity <= 0.0);

    // reward is only needed during training.
    if (self.predict() == false) {
        reward = reward_for_objective(objective_name());
    }

    state.set_float32("velocity", velocity);
    state.set_float32("angle",    angle);
}
```

```python
def simulate(self, action):
    velocity = velocity - action.delta;
    terminal = (velocity <= 0.0)

    # reward is only needed during training
    if self.predict == False:
        reward = reward_for_objective(self.objective_name)

    state = {
        "velocity": self.velocity,
        "angle": self.angle,
    }
    return (state, reward, terminal)
```

| Argument   | Description |
| ---        | ---         |
| `action`   | Input InklingMessage of action to be taken as defined in inkling. |
| `state`    | Output InklingMessage. Should be populated with the current simulator state. |
| `reward`   | Output reward value as calculated based upon the objective. |
| `terminal` | Output terminal state. Set to true if the simulator is in a terminal state. |

This callback steps the simulation forward by a single step. It passes in
the `action` to be taken, and expects the resulting `state`, `reward` for the current
`objective`, and a `terminal` flag used to signal the end of an episode. Note that an
episode may be reset prematurely by the backend during training.

For a multi-lesson curriculum, the `objective_name` will change from episode to episode.
In this case ensure that the simulator is returning the correct reward for the
different lessons.

Returning `true` for the `terminal` flag signals the start of a new episode.

The default implementation will throw an exception.

## bool run()

```cpp
MySimulator sim(brain);

if (sim.predict())
    std::cout << "Predicting against " << brain.name() << " version " << brain.version() << endl;
else
    std::cout << "Training " << brain.name() << endl;

while( sim.run() ) {
}
```

```python
sim = MySimulator(brain)

if sim.predict:
    print("Predicting against ", brain.name, " version ", brain.version)
else:
    print("Training ", brain.name)

while sim.run():
    continue
```

Main loop call for driving the simulation. Returns `false` when the
simulation has finished or halted.

The client should call this method in a `while` loop until it returns `false`.
To run for prediction, `brain()->config()->predict()` must return `true`.

## operator<<(ostream, simulator)

Prints out a representation of Simulator that is useful for debugging.

**Note:** Used in C++ only. For python, use `print(simulator)`

| Argument  | Description |
| ---       | ---         |
| `ostream` | A std c++ stream operator. |
| `simulator`  | A bonsai::Simulator to print out. |

