# A minimal Inkling program for a BRAIN that learns how to operate climate
# control using BCVTB and EnergyPlus.
# Simulator source code:
# https://github.com/BonsaiAI/bonsai-sdk/blob/master/samples/energyplus-sample/energyplus_simulator.py

inkling "2.0"

# A type defining the dictionary returned from the Python simulation's
# advance method to the BRAIN
const MinIrradiation = 0
const MaxIrradiation = 10
type SimState {
    SolarIrradiation: number<MinIrradiation .. MaxIrradiation step 1>
}

# This type defines the 'actions', a dictionary of control signals this AI
# can send to the climate control.
type SimAction {
    shade: number<Off = 0, On = 1>
}

# The simulator clause declares that a simulator named "energyplus_simulator"
# will be connecting to the server for training.
# The following statements bind the above types to this simulator
simulator EnergyplusSimulator(action: SimAction): SimState {
}

graph (input: SimState): SimAction {
    # An example concept that predicts a SimAction given a SimState
    # In this simple demo we just ask the Bonsai Platform to generate any model
    # that can learn to control the server using these inputs and outputs
    concept ManageShade(input): SimAction {
        curriculum {
            source EnergyplusSimulator
        }
    }
    output ManageShade
}
