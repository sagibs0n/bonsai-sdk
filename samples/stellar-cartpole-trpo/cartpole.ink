schema GameState
   Float32 position,
   Float32 velocity,
   Float32 angle,
   Float32 rotation
end

schema Action
   Float32{-1.0:1.0} command
end

schema CartPoleConfig
   Int8 episode_length,
   UInt8 deque_size
end

simulator the_simulator(CartPoleConfig)
   action (Action)
   state (GameState)
end

concept balance is estimator
   predicts (Action)
   follows input(GameState)
   feeds output

end

curriculum balance_curriculum
   train balance
   using algorithm TRPO
      learning_rate => 5,
      hidden_layer_size_descriptor => [48, 48],
      hidden_layer_activation_descriptor => ["relu", "relu"]
   end

   with simulator the_simulator
   objective balance_objective

       lesson balancing
           configure
               constrain episode_length with Int8{-1},
               constrain deque_size with UInt8{1}
           until
               maximize balance_objective
end
