# Widgets
_Widgets_ is a UI software, providing  paramater input and control for the Pisces lightsheet microscope.

The UI is started up by running **widgets/gui/main_window.py**. Its dependencies can be installed using the requiremets.txt file in a Python 3.7 Conda  environment. 


## Installation
This installation guide uses Anaconda to set up a virtual environment with the required dependencies. 

Install Anaconda here: https://www.anaconda.com/distribution/


### Clone Widgets Repository
```
git clone https://github.com/royerlab/widgets.git
```

### Create Conda Environment and Install Dependencies
```
conda create -n widgets python=3.7
conda activate widgets
pip install -r requirements.txt
```
