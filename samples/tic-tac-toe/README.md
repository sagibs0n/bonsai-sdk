# Tic-Tac-Toe
A simple implementation of the classic game Tic-Tac-Toe, with a "computer" agent and a "player" agent. The computer agent makes deterministically optimal moves on each turn, whereas the player's moves are delivered by the Bonsai Platform.

At first, the player should lose every game. As the BRAIN trains, more an more games (approaching all games) should end in a draw.


## WEB GUIDE

If you're using the web interface, please follow the [quick start guide](http://docs.bons.ai/guides/getting-started.html).

## LOCAL (CLI) GUIDE

### CLI INSTALLATION
1. Install the Bonsai CLI by following our [detailed CLI installation guide](http://docs.bons.ai/guides/cli-guide.html).

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
       `python tictactoe_simulator.py --train-brain=<your_brain> --headless`
4. When training has hit a sufficient accuracy for prediction, about 250 for at least 100 episodes, stop training your BRAIN.
       `bonsai train stop`

### GET PREDICTIONS
1. Run the simulator using predictions from your BRAIN. You can now see AI playing the game!
       `python tictactoe_simulator.py --predict-brain=<your_brain> --predict-version=latest`
