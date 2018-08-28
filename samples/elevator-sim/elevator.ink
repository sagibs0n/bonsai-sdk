# Position is current location of elevator
# State of each floor: 1 if the floor is requested, 0 if not
schema FloorState
    Int8{0, 1, 2} Position,
    Int8{0, 1} Floor1,
    Int8{0, 1} Floor2,
    Int8{0, 1} Floor3
end

# command options: up, open, down
constant Int8 up = 0
constant Int8 open = 1
constant Int8 down = 2
schema Action
    Int8{up, open, down} command
end

# Possible option for configuration
schema ElevatorConfig
    Int8 episode_length
end

# Connect to SimPy simulator for training
simulator elevator_simulator(ElevatorConfig)
    action (Action)
    state (FloorState)
end

# Predicts an Action and follows input from the FloorState schema
concept elevator_plan is classifier
    predicts (Action)
    follows input(FloorState)
    feeds output
end

# This trains the concept using a single lesson
# Maximize the elevator_objective defined in elevator_simulator.py
curriculum high_score_curriculum
    train elevator_plan
    with simulator elevator_simulator
    objective elevator_objective
        lesson get_high_score
            configure
                constrain episode_length with Int8{-1}
            until
                maximize elevator_objective
end
