schema GameState
    Float32 x_position,
    Float32 x_velocity
end

constant Float32 throttleMin = -1.0
constant Float32 throttleMax = 1.0
schema Action
    Float32{throttleMin:throttleMax} command
end

schema MountainCarConfig
    UInt8 deque_size
end

simulator mountaincar_continuous_simulator(MountainCarConfig)
  action  (Action)
  state  (GameState)
end

concept high_score is estimator
    predicts (Action)
    follows input(GameState)
    feeds output
end

curriculum high_score_curriculum
    train high_score
    with simulator mountaincar_continuous_simulator
    objective open_ai_gym_default_objective

        lesson get_high_score
            configure
                constrain deque_size with UInt8{1}
            until
                maximize open_ai_gym_default_objective
end
