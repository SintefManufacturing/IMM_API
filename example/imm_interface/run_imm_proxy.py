#--------------------------------------------------------------------
#Module Description
#--------------------------------------------------------------------
"""
Example how to use imm proxy
"""
#--------------------------------------------------------------------
#Administration Details
#--------------------------------------------------------------------
__author__ = "Mats Larsen"
__copyright__ = "2020 [NTNU Gjøvik and SINTEF Manufacturing]"
__credits__ = ["Mats Larsen"]
__license__ = "MIT"
__maintainer__ = "Mats Larsen"
__email__ = "Mats.Larsen@sintef.no"
__status__ = "Development"
__date__ = "30032020"
__version__ = "1.0"
#--------------------------------------------------------------------
# Import
#--------------------------------------------------------------------
import imm
#--------------------------------------------------------------------
# CONSTANTS
#--------------------------------------------------------------------
#Parameters settings for config
NAME = 'imm_machine'                        # Name of the instance
IP = '172.16.10.39'                         # IMM's IP
PORT = 10050                                # IMM's port
USERNAME = 'name'       # IMM's username
PASSW = 'code'                         # IMM's password for the username
#sampling_mode = imm.SamplingRateMode.FIXED_STEP
sampling_rate = 0.2                         # Sampling time for only for intern logging state
PROTOCOL = imm.Protocol.EMI                 # IMM's protocol
PATH = 'parameter_list.csv'                 # Path to csv of wanted parameters
DEBUG = False                               # Debug mode

#--------------------------------------------------------------------
# METHODS
#--------------------------------------------------------------------
if __name__ == "__main__":

    #Parameters settings for config
    params = {
        'name':NAME,
        'ip':IP,
          'port':PORT,
          'username':USERNAME,
          'passw':PASSW,
          'sampling_rate' : sampling_rate,
          'protocol':PROTOCOL,
          'params_path':PATH,
          'debug':DEBUG
    }

    # Information for distributed system
    pyro4_params = {
        'name': 'IMM.EXAMPLE',
        'ns': ['172.16.0.98',9001]
    }

    # Starting the IMM proxy instance
    p = imm.IMMProxy(params=params,
                     pyro4_params=pyro4_params
                     )
