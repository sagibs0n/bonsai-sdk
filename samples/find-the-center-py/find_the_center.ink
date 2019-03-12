inkling "2.0"
using Number

type GameState {
    value: Number.Int8
}

type PlayerMove {
    delta: Number.Int8<Dec = -1, Stay = 0, Inc = 1>
}

simulator find_the_center_sim(action: PlayerMove): GameState {
}

graph (input: GameState): PlayerMove {
    concept find_the_center(input): PlayerMove {
        curriculum {
            source find_the_center_sim
        }
    }
    output find_the_center
}
