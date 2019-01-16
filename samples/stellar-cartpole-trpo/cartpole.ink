schema GameState
   Float32 position,
   Float32 velocity,
   Float32 angle,
   Float32 rotation
end

constant Int8 left = -1 
constant Int8 right = 1

schema Action
   Int8{left, right} command
end

schema CartPoleConfig
   Int8 unused
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
               constrain unused with Int8{-1}
           until
               maximize balance_objective
end
