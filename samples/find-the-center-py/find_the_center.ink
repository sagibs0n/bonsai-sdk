schema GameState
    Int8 value
end

schema PlayerMove
    Int8{-1, 0, 1} delta
end

schema SimConfig
    Int8 dummy
end

concept find_the_center
    is classifier
    predicts (PlayerMove)
    follows input(GameState)
    feeds output
end

simulator find_the_center_sim(SimConfig)
    action (PlayerMove)
    state (GameState)
end

curriculum find_the_center_curriculum
    train find_the_center
    with simulator find_the_center_sim
    objective time_at_goal
        lesson seek_center
            configure
                constrain dummy with Int8{-1}
            until
                maximize time_at_goal
end