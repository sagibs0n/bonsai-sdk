# OpenAI Gym Lunar Lander Continuous Sample

## WEB GUIDE

If you're using the web interface, please follow the [quick start guide](http://docs.bons.ai/guides/getting-started.html).



## LOCAL (CLI) GUIDE

### SWIG INSTALLATION
* **OSX**
  * brew install swig
* **Ubuntu**
  * apt-get install -y swig
* **Windows**
  * Download swigwin zip package from the [SWIG website](http://www.swig.org/) and unzip. Add the unzipped folder to your system $PATH variable. (Microsoft Visual C++14 is required)
  * Anaconda users can run `conda install -c anaconda swig`

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
3. Connect the OpenAI Gym simulator for training. Use the `--headless` option to hide the graphical output.
       `python lunarlander_continuous_simulator.py --headless`
4. When training has hit a sufficient accuracy for prediction, you'll see the graph plateau, stop training your BRAIN.
       `bonsai train stop`

### GET PREDICTIONS
1. Run the simulator using predictions from your BRAIN. You can now see AI playing the game!
       `python lunarlander_continuous_simulator.py --predict`


## Questions about Inkling?
See our [Inkling Guide](http://docs.bons.ai/guides/inkling-guide.html) and [Inkling Reference](http://docs.bons.ai/references/inkling-reference.html) for help.
