experimental
    random_seed => "20" : "random seeds"
end

schema GameState
    Int8{0:15} current_pos
end

constant Int8 up = 0
constant Int8 down = 1
constant Int8 left = 2
constant Int8 right = 3
schema Action
    Int8{up, down, left, right} command
end

schema FrozenLakeConfig
    UInt8 deque_size
end

simulator frozenlake_simulator(FrozenLakeConfig) 
    action (Action)
    state (GameState)
end

concept goal_position is classifier
    predicts (Action)
    follows input(GameState)
    feeds output
end

curriculum reach_goal_curriculum
    train goal_position
    with simulator frozenlake_simulator
    objective open_ai_gym_default_objective

        lesson reach_goal
            configure
                constrain deque_size with UInt8{1}
            until
                maximize open_ai_gym_default_objective
end
