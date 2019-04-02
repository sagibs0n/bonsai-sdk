inkling "2.0"
using Number
type GameState {
    test_number: number,
    test_double: Number.Float64,
    test_float: Number.Float32,
    test_int64: Number.Int64,
    test_int32: Number.Int32,
    test_uint64: Number.UInt64,
    test_uint32: Number.UInt32,
    #test_bool: Number.Bool,
}

type Action {
   ignored: number,
}

type Config {
    test_number: number,
    test_double: Number.Float64,
    test_float: Number.Float32,
    test_int64: Number.Int64,
    test_int32: Number.Int32,
    test_uint64: Number.UInt64,
    test_uint32: Number.UInt32,
    #test_bool: Number.Bool,
}

simulator the_simulator(action: Action, config: Config): GameState {
}

graph (input: GameState): Action {

    concept balance(input): Action {
        curriculum {
            source the_simulator
            lesson balancing {
                constraint {
                    test_number: number<1 .. 4>,
                    test_double: Number.Float64<1 .. 4>,
                    test_float:  Number.Float32<1 .. 4>,
                    test_int64:  Number.Int64<1 .. 4>,
                    test_int32:  Number.Int32<1 .. 4>,
                    test_uint64: Number.UInt64<1 .. 4>,
                    test_uint32: Number.UInt32<1 .. 4>,
                    #test_bool:   Number.Bool<0 .. 1>,
                }
            }
        }
    }
    output balance
}
