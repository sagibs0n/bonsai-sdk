inkling "2.0"

using Number
experiment {
    num_workers: "3",
    env_runners_per_sampler: "10"
}

type GameState {
    cos_theta0: number,
    sin_theta0: number,
    cos_theta1: number,
    sin_theta1: number,
    theta0_dot: number,
    theta1_dot: number
}

type Action {
    command: Number.Int8<Left = 0, Center = 1, Right = 2>
}

type AcrobotConfig {
    deque_size: 1
}

simulator AcrobotSimulator(action: Action, config: AcrobotConfig): GameState {
}

graph (input: GameState): Action {
    concept Height(input): Action {
        experiment {
            max_step_per_concept: "1000000"
        }
        curriculum {
            source AcrobotSimulator
        }
    }
    output Height
}
