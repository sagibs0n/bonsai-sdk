inkling "2.0"
using Number
type GameState {
    position: Number.Float32,
    velocity: Number.Float32,
    angle: Number.Float32,
    rotation: Number.Float32
}

type Action {
    command: Number.Int8<0, 1, >
}

type CartPoleConfig {
    episode_length: Number.Int8,
    deque_size: Number.UInt8
}

simulator cartpole_simulator(action: Action, config: CartPoleConfig): GameState {
}

graph (input: GameState): Action {

    concept balance(input): Action {
        curriculum {
            source cartpole_simulator
            lesson balancing {
                constraint {
                    episode_length: -1,
                    deque_size: 1
                }
            }
        }
    }
    output balance
}
