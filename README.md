# coPylot
_coPylot_ is a UI software, providing  paramater input and control for the Pisces lightsheet microscope.

The UI is started up by running **copylot/gui/main_window.py**. Its dependencies can be installed using the requiremets.txt file in a Python 3.7 Conda  environment. 


## Installation
This installation guide uses Anaconda to set up a virtual environment with the required dependencies. 

Install Anaconda here: https://www.anaconda.com/distribution/


### Clone coPylot Repository
```
git clone https://github.com/royerlab/coPylot.git
```

### Create Conda Environment and Install Dependencies
```
conda create -n coPylot python=3.7
conda activate coPylot
pip install -r requirements.txt
```
