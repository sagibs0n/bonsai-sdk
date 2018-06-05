schema GameState
    Luminance(9, 9) image
end

schema PlayerMove
    Int8{1, 2, 3, 4, 5, 6, 7, 8, 9} move
end

schema DummyConfig
    Int8 dummy
end

simulator tictactoe_simulator(DummyConfig)
  action  (PlayerMove)
  state  (GameState)
end

concept play_tictactoe is classifier
    predicts (PlayerMove)
    follows input(GameState)
    feeds output
end

algorithm My_DQN_Settings
    is DQN
    hidden_layer_size => "32",
    hidden_layer_activation_descriptor => "'relu'",
    conv_layer_descriptor => "3x3:3:3:2",
    conv_compression_size_descriptor => "32",
    conv_compression_activation_descriptor => "'relu'"
end

curriculum ticatactoe_curriculum
    train play_tictactoe
    using algorithm My_DQN_Settings
    with simulator tictactoe_simulator
    objective get_reward
        lesson highscore
            configure
                constrain dummy with Int8{-1}
            until
                maximize get_reward
end
