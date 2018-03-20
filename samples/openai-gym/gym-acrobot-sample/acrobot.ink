schema GameState
    Float32 cos_theta0,
    Float32 sin_theta0,
    Float32 cos_theta1,
    Float32 sin_theta1,
    Float32 theta0_dot,
    Float32 theta1_dot
end

schema Action
    Int8{0, 1, 2} command
end

schema AcrobotConfig
    UInt8 deque_size
end

simulator acrobot_simulator(AcrobotConfig)
    action (Action)
    state (GameState)
end

concept height is classifier
    predicts (Action)
    follows input(GameState)
    feeds output
end

curriculum height_curriculum
    train height
    with simulator acrobot_simulator
    objective open_ai_gym_default_objective

        lesson reaching_height
            configure
                constrain deque_size with UInt8{1}
            until
                maximize open_ai_gym_default_objective
end
