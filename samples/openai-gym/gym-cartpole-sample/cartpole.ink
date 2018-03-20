schema GameState
    Float32 position,
    Float32 velocity,
    Float32 angle,
    Float32 rotation
end

schema Action
    Int8{0, 1} command
end

schema CartPoleConfig
    Int8 episode_length,
    UInt8 deque_size
end

simulator cartpole_simulator(CartPoleConfig) 
    action (Action)
    state (GameState)
end

concept balance is classifier
    predicts (Action)
    follows input(GameState)
    feeds output
end

curriculum balance_curriculum
    train balance
    with simulator cartpole_simulator
    objective open_ai_gym_default_objective

        lesson balancing
            configure
                constrain episode_length with Int8{-1},
                constrain deque_size with UInt8{1}
            until
                maximize open_ai_gym_default_objective
end
