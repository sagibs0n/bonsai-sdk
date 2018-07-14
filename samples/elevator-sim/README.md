# PySim Elevator

In this example, SimPy, a process-based discrete-event simulation framework based on standard Python, is used to simulate an elevator effectively transporting people to their desired floor. The simulated elevator gets rewarded by having people wait for the least amount of time. This example includes a simple elevator SimPy simulator, a Python simulation, and the simulation’s Inkling file.

For more information on how this and other examples work follow along with [Bonsai's example documentation](https://docs.bons.ai/examples.html#simpy-elevator-simulation).


## WEB GUIDE

If you're using the web interface, please follow the [quick start guide](https://docs.bons.ai/guides/getting-started.html).

## LOCAL (CLI) GUIDE

### CLI INSTALLATION
1. Install the Bonsai CLI by following our [detailed CLI installation guide](https://docs.bons.ai/guides/cli-install-guide.html).

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
3. Connect the simulator for training.
       `python elevator_simulator.py`
4. When training has hit a sufficient accuracy for prediction, after a few minutes, stop training your BRAIN.
       `bonsai train stop`

### GET PREDICTIONS
1. Run the simulator using predictions from your BRAIN. You can now see AI in action!
       `python elevator_simulator.py --predict`

## Questions about Inkling?
See our [Inkling Guide](https://docs.bons.ai/guides/inkling-guide.html) and [Inkling Reference](https://docs.bons.ai/references/inkling-reference.html) for help.