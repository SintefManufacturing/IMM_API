#--------------------------------------------------------------------
#Module Description
#--------------------------------------------------------------------
"""
Example how to communicate with a revpi daq proxy as a normal python script.
"""
#--------------------------------------------------------------------
#Administration Details
#--------------------------------------------------------------------
__author__ = "Mats Larsen"
__credits__ = ["Mats Larsen","Olga Ogorodnyk"]
__copyright__ = "2020 [NTNU Gjøvik and SINTEF Manufacturing]"
__license__ = "MIT"
__maintainer__ = "Mats Larsen"
__email__ = "Mats.Larsen@sintef.no"
__status__ = "Development"
__date__ = "27103020"
__version__ = "1.0"
#--------------------------------------------------------------------
#Import
#--------------------------------------------------------------------
import revpi_daq
import os
from pathlib import Path
#--------------------------------------------------------------------
#CONSTANTS
#--------------------------------------------------------------------
NAME = 'example revpi_daq'
SRATE = 0.1

pin_path = os.path.join(os.getcwd(),'example','pins.csv')
#Parameters settings for config revpi daq
PYRONAME = 'Pyro.name' # Insert the pyro4 name
NS = ['IP','PORT'] # Insert the IP and Port
#--------------------------------------------------------------------
#METHODS
#--------------------------------------------------------------------
if __name__ ==  "__main__":
    pins= revpi_daq.load_params(pin_path)
    params = {
        'name':NAME,
        'sampling_rate':SRATE,
        'pins':pins
    }
    # Information about config for the sensor

    pyro4_params = {
        # Information about writing and reading config files
        'name': PYRONAME,
        'ns': NS
    }
    a = revpi_daq.RevPI_DAQ_Proxy(params=params,
                                  pyro4_params=pyro4_params
                                  )
