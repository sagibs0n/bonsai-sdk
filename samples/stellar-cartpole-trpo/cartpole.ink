# Inkling code for balancing a pole on a cart

inkling "2.0"

type GameState {
    position: number,
    velocity: number,
    angle: number,
    rotation: number
}

type Action {
    command: number<Left = -1, Right = 1>
}

type CartPoleConfig {
    episode_length: -1,
    deque_size: 1
}

# Simulator source code:
# https://github.com/BonsaiAI/bonsai-sdk/blob/master/samples/stellar-cartpole-trpo/cartpole_simulator.py
simulator CartpoleSimulator(action: Action, config: CartPoleConfig): GameState {
}

graph (input: GameState): Action {
    concept Balance(input): Action {
        curriculum {
            source CartpoleSimulator
        }
    }
    output Balance
}
