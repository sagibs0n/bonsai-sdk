# Stellar Cartpole Sample
A pole is attached by an un-actuated joint to a cart, which moves along a frictionless track. The system is controlled by applying a force of +1 or -1 to the cart. The pendulum starts upright, and the goal is to prevent it from falling over. A reward of +1 is provided for every timestep that the pole remains upright. The episode ends when the pole is more than 15 degrees from vertical, or the cart moves more than 2.4 units from the center.

This version of Cartpole expands on the OpenAI gym sample of cartpole and exposes machine teaching logic and the rendering modeled by the classic cart-pole system implemented by Rich Sutton et al.

Copied from http://incompleteideas.net/sutton/book/code/pole.c
permalink: https://perma.cc/C9ZM-652R

## Files

* `bonsai_brain.bproj` - BRAIN project file (do not modify)
* `bridge.py` - Python bridge code to connect the model with the Bonsai Platform 
* `cartpole.ink` - Inkling code for balancing a pole on a cart
* `cartpole.py` - Python cart-pole simulation code
* `README.md` - This file
* `render.py` - Visual rendering of the cartpole simulation in Python
* `rendering.py` - Core rendering code and draw calls
* `requirements.txt` - pip install these packages before running this sample
* `seeding.py` - Random number generation
* `star.py` - Machine Teaching logic (states, terminals, actions, and reward)

## WEB GUIDE
If you're using the web interface, please follow the [quick start guide](http://docs.bons.ai/guides/getting-started.html).

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
3. Connect the simulator for training. Use the `--render` option to render the cartpole.
       `python bridge.py --render`
4. When training has hit a sufficient accuracy for prediction, about 250 for at least 100 episodes, stop training your BRAIN.
       `bonsai train stop`

### GET PREDICTIONS
1. Run the simulator using predictions from your BRAIN. You can now see AI playing the game!
       `python bridge.py --predict`


## Questions about Inkling?
See our [Inkling Guide](http://docs.bons.ai/guides/inkling-guide.html) and [Inkling Reference](http://docs.bons.ai/references/inkling-reference.html) for help.