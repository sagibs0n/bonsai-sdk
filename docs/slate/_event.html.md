# Event

## Event Class (Python)

Base class.

###### EpisodeStartEvent

```python
event = sim.get_next_event()
if isinstance(event, EpisodeStartEvent):
    state = sim.episode_start(event.initial_properties)
    event.initial_state = state
```

This event is generated at the start of a training episode.
It is triggered either by a terminal condition in the simulator
or by the platform itself.

| Attribute | Description |
| ---      | ---         |
| `initial_properties`  |  Configuration properties for the simulator. |
| `initial_state`   |  Assign the state resulting from a model reset. |

###### SimulateEvent

```python
event = sim.get_next_event()
if isinstance(event, SimulateEvent):
    state, reward, terminal = sim.simulate(event.action)
    event.state = state
    event.reward = float(reward)
    event.terminal = bool(terminal)
```

This event is generated when an action (prediction) is ready
to be fed into the simulator.

| Attribute | Description |
| ---      | ---         |
| `action`  |  Next action (prediction) in the queue. |
| `state`   |  Assign the resulting state after updating the model. |
| `reward`   |  The reward calculated from the updated. |
| `terminal`   |  Whether the updated state is terminal. |

###### FinishedEvent

```python
event = get_next_event()
if isinstance(event, FinishedEvent):
    self.close()
```

Indicates that the Bonsai Platform has terminated training.

###### UnknownEvent

Catch-all event for other internal states. This event can be safely ignored,
but it is provided for completeness and is handy for explicitly tracking state
transitions from client code.



## Event Class (C++)

Abstract base class for encapsulating Simulator state. Event types correspond to different
procedures in client code (see `enum class Type`).

### enum class Type

```cpp
auto event = get_next_event();
if (event->type() == Type::Episode_Start) {
    auto es_E = dynamic_pointer_cast<EpisodeStartEvent>(event);
    auto initial_properties = es_E->initial_properties;
    auto initial_state = es_E->initial_state;
    // process initial properties/state
} else if (event->type() == Type::Simulate) {
    auto sim_E = dynamic_pointer_cast<SimulatorEvent>(event);
    auto prediction = sim_E->prediction;
    auto state = sim_E->state;
    auto reward = sim_E->reward;
    auto terminal = sim_E->terminal;
    // process simulator step 
} else if (event->type() == Type::Finished) {
    close();
}
```

| Value          | Description |
| ----           | ----        |
| `Episode_Start`|  Reset the simulator and set initial state. |
| `Simulate`     |  Advance the simulation with the next prediction and record resulting state. |
| `Finished`     |  Simulation complete. BRAIN does not expect further state data. |
| `Unknown`      |  No event corresponding to last message exchange. |

### Type type()
Returns the Type of the Event. Implemented for each specialization of Event.

###### EpisodeStartEvent Class
Signals a boundary between training episodes. Requires resetting the simulation environment
and returning its initial state to the **BRAIN**.

### std::shared_ptr<const InklingMessage> initial_properties
Settings used when resetting the simulation environment.

### std::shared_ptr<InklingMessage> initial_state
Directly manipulate to reflect the state resulting from sim environment reset.

See `InklingMessage` API for detail.

###### SimulateEvent Class
Signals that the **BRAIN** is ready to receive the simulator state resulting from
the next prediction in the queue.

### std::shared_ptr<const InklingMessage> prediction
The prediction (action) intended for the next simulation step.

### std::shared_ptr<InklingMessage> state
Directly manipulate to reflect the state resulting from applying `prediction`
to the simulation environment.

See `InklingMessage` API for detail.

### std::shared_ptr<float> reward
Directly manipulate to reflect the reward corresponding to `state`.

### std::shared_ptr<bool> terminal
Directly manipulate to reflect whether the current `state` is terminal.

###### FinishedEvent Class
Signals that the **BRAIN** is done training. No more simulation steps are expected.

###### UnknownEvent Class
Signals that no action is required.

