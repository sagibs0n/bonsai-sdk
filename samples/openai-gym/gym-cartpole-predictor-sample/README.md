# OpenAI Gym Cart Pole Predictor Sample
A pole is attached by an un-actuated joint to a cart, which moves along a frictionless track. The system is controlled by applying a force of +1 or -1 to the cart. The pendulum starts upright, and the goal is to prevent it from falling over. A reward of +1 is provided for every timestep that the pole remains upright. The episode ends when the pole is more than 15 degrees from vertical, or the cart moves more than 2.4 units from the center.

The following example shows how to use the predictor to get actions from a trained BRAIN.

## LOCAL (CLI) GUIDE

### CLI INSTALLATION
1. Install the Bonsai CLI by following our [detailed CLI installation guide](https://docs.bons.ai/guides/cli-install-guide.html)

### CREATE YOUR BRAIN
1. Setup your BRAIN's local project folder.
       `bonsai create <your_brain>`
2. Run this command to install additional requirements for training your BRAIN.
       `pip install -r requirements.txt`

### HOW TO TRAIN YOUR BRAIN
1. Upload Inkling and simulation files to the Bonsai server with one command.
       `bonsai push`
2. Run this command to start training mode for your BRAIN.
       `bonsai train start`
   If you want to run this remotely on the Bonsai server use the `--remote` option.
       `bonsai train start --remote`
3. Connect the OpenAI Gym simulator for training. Use the `--headless` option to hide the graphical output.
       `python cartpole_simulator.py --headless`
4. When training has hit a sufficient accuracy for prediction, about 250 for at least 100 episodes, stop training your BRAIN.
       `bonsai train stop`

### GET PREDICTIONS USING PREDICTOR INTERFACE
1.  Run the following to get predictions from your BRAIN annd use them to control the OpenAI cartpole simulation.
       `python cartpole_predictor --predict`


## Questions about Inkling?
See our [Inkling Guide](http://docs.bons.ai/guides/inkling-guide.html) and [Inkling Reference](http://docs.bons.ai/references/inkling-reference.html) for help.
