#--------------------------------------------------------------------
#Module Description
#--------------------------------------------------------------------
"""
Example to communicate with revpi daq proxy as a normal python script.
This is an example how to use revpi as a daq system
"""
#--------------------------------------------------------------------
#Administration Details
#--------------------------------------------------------------------
__author__ = "Mats Larsen"
__credits__ = ["Mats Larsen"]
__copyright__ = "Sintef Raufoss Manufacturing 2018"
__license__ = "SRM"
__maintainer__ = "Mats Larsen"
__email__ = "Mats.Larsen@sintef.no"
__status__ = "Development"
__date__ = "31102018"
__version__ = "0.1"
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
PYRONAME = 'PI.MEGAMOULD'
NS = ['172.16.0.98',9001]
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
    a = revpi_daq.RevPI_DAQ_Proxy(params=params,pyro4_params=pyro4_params)
