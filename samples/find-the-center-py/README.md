# Find the Center Example Project
This project demonstrates a basic implementation of a Python simulator with custom Inkling code. For more information see this example walkthrough on [Bonsai docs](http://docs.bons.ai/examples.html#basic-python-c-simulation).


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
1. Upload Inkling and simulation files to the Bonsai server with one command if you have changed any files.
       `bonsai push`
2. Run this command to start training mode for your BRAIN.
       `bonsai train start`
3. Connect the simulator for training.
       `python find_the_center_sim.py`
4. When training has hit a sufficient accuracy for prediction, after a few minutes, stop training your BRAIN.
       `bonsai train stop`

### GET PREDICTIONS
1. Run the simulator using predictions from your BRAIN. You can now see AI in action!
       `python find_the_center_sim.py --predict`


## Questions about Inkling?
See our [Inkling Guide](http://docs.bons.ai/guides/inkling-guide.html) and [Inkling Reference](http://docs.bons.ai/references/inkling-reference.html) for help.
