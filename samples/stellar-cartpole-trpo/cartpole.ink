# Inkling code for balancing a pole on a cart

schema GameState
   Float32 position,
   Float32 velocity,
   Float32 angle,
   Float32 rotation
end


schema Action
   Int8{-1,1} command
end

schema CartPoleConfig
   Int8 episode_length,
   UInt8 deque_size
end

simulator the_simulator(CartPoleConfig)
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

   with simulator the_simulator
   objective balance_objective

       lesson balancing
           configure
               constrain episode_length with Int8{-1},
               constrain deque_size with UInt8{1}
           until
               maximize balance_objective
end
