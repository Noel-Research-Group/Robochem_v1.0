### RoboChem
This repository contains the codebase and resources necessary to operate 
RoboChem, a self-optimizing robotic platform dedicated to chemistry
optimization. 

For the paper associated with the code please see here: 
https://chemrxiv.org/engage/chemrxiv/article-details/64809b97e64f843f41767eac

DOI: 10.26434/chemrxiv-2023-r0drq

Robochem is split over a 64-bit (GUI and BO) and 32-bit (Hardware/Platform). 

Please Read below for how to get up and running.

#### Physical Components Control (python 32-bit):
This section consists of individual folders dedicated to managing the physical 
components essential for our system's operation. Each piece  equipment, 
including the photoreactor (eagle reactor), liquid handler, mass flow controller, NMR
(spinsolve NMR), phase sensors, syringe pumps, switch valves, and, has its separate folder. This modular structure allows for 
easy integration and modification of specific components, enabling a flexible 
and scalable build process. The individual components are then combined in 
in further individual programmes
#### Machine Learning & GUI Integration (python 64-bit): 
The second section is subdivided into two essential parts:
###### Machine Learning Process with Bayesian Optimization: 
This part encompasses the machine learning algorithms implementing Bayesian 
optimization using the Dragonfly package. These algorithms work tirelessly 
behind the scenes, optimizing chemical processes for efficiency and accuracy.
###### Graphical User Interface (GUI): 
Alongside the machine learning process, a user-friendly GUI built on Streamlit 
orchestrates the entire system. This intuitive interface harmonizes with the 
optimization algorithms, empowering users to interact effortlessly with the 
platform. Together, these components form an accessible, self-optimizing 
robotic platform that streamlines the chemistry optimization process.


### Setting-up Conda environments
Two conda environments are required to run this code, one for the optimization (robochem_gui) and one for controlling
the platform (robochem_platform_32bit). To create these environments please use the environment yml files:
- `ML_GUI\\gui_environment.yml`
- `Platform_\\platform_environment.yml`
Please don't change the names of the environments as they are currently used in the code.

To do this, run the following commands from the root directory in the terminal:
```commandline
cd ML_GUI
conda env create -f gui_environment.yml
cd ..
cd Platform_
conda env create -f platform_environment.yml
```
For more information on setting up conda see: `https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html`

### Run Optimization from GUI
If the campaign shall be run from the GUI, first the GUI has to be activated.
When all information is filled in (and the Liquid Handler is filled with the stocksolutions according to the by the GUI 
generated excel-file) the platform can be run by pressing the `run button` on the `Run Platform` page.
This will call the `run_optimization_from_gui.py` file which will call the `Dragonfly_BO.py` file which in turn will use
`os.popen` to run the `run_platform.py` file in the `Platform_` folder.

###### How to activate the GUI
Change directory and then active the conda environment `robochem_gui`, and then run the GUI home page:
```
cd ML_GUI -> conda activate robochem_gui -> streamlit run ??_Home.py
```

When streamlit is run, the main page is `🏡_Home.py`. Every additional page is found in the 
folder `Pages`. The pages are order alphabetically. When the platform is run, the result shall be
updated and plotted after each run. The figures are generated in `Visualization.py` and
the png-files `figure_hypervolyme.png` and `figure_objectives.png` are updated and these are the files
the streamlit app is continuously calling. Before the first experiment has been finished the figures are replaced with 
the figure `Campaign has started.png` instead.

### Run Optimization directly from code
If one wants to run the platform directly from the code, one can write
the space directly into the file `run_optimization.py`. An example of how that could look like is found in this file.
The other files such as the excel-file for the Liquid Handler then has to manually be generated and put in the correct 
place. When run it will call the `Dragonfly_BO.py` file which in turn will use `subprocess.run` to run the `run_platform.py` 
file in the `Platform_` folder.
