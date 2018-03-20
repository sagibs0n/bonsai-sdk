schema GameState
    Float32 x_position,
    Float32 y_position,
    Float32 x_velocity,
    Float32 y_velocity,
    Float32 angle,
    Float32 rotation,
    Float32 left_leg,
    Float32 right_leg
end

schema LanderAction
    Float32{-1.0:1.0} engine1,
    Float32{-1.0:1.0} engine2
end

schema LunarLanderConfig
    Int8 episode_length,
    UInt8 deque_size
end

simulator lunarlander_continuous_simulator(LunarLanderConfig)
  action  (LanderAction)
  state  (GameState)
end

concept land is estimator
    predicts (LanderAction)
    follows input(GameState)
    feeds output
end

curriculum landing_curriculum
    train land
    with simulator lunarlander_continuous_simulator
    objective open_ai_gym_default_objective

        lesson landing
            configure
                constrain episode_length with Int8{-1},
                constrain deque_size with UInt8{1}
            until maximize open_ai_gym_default_objective
end

