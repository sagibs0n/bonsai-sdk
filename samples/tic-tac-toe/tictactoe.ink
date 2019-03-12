inkling "2.0"
using Image

type GameState {
    image: Image.Gray<9, 9>
}

type PlayerMove {
    move: number<1, 2, 3, 4, 5, 6, 7, 8, 9>
}

simulator TicTacToeSimulator(action: PlayerMove): GameState {
}

graph (input: GameState): PlayerMove {
    concept PlayTicTacToe(input): PlayerMove {
        curriculum {
            algorithm {
                Algorithm: "DQN",
                ConvolutionLayers: [{
                    XSize: 3,
                    YSize: 3,
                    XStride: 3,
                    YStride: 3,
                    FilterCount: 2
                }]
            }
            source TicTacToeSimulator
        }
    }

    output PlayTicTacToe
}
