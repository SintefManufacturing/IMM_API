#--------------------------------------------------------------------
#Module Description
#--------------------------------------------------------------------
"""
Class to API for RevPI DAQ
The API set is:
- get_samples()     -> Returning all samples that have been collected
- event()           -> Set the Revpi to event state, waiting a trigger sample from externally
- event_sample()    -> Trigger a sample when the Revpi is oin event state
- idle()            -> Revpi is in idle
- start_logging()   -> Start intern logging based on the set sampling_rate
- get_async_sample  -> Get asynchrony samnple independent of the control loop
"""
#--------------------------------------------------------------------
#Administration Details
#--------------------------------------------------------------------
__author__ = "Mats Larsen"
__copyright__ = "2020 [NTNU Gjøvik and SINTEF Manufacturing]"
__credits__ = ["Mats Larsen","Olga Ogorodnyk","Anders Svenskerud Bækkedal"]
__license__ = "MIT"
__maintainer__ = "Mats Larsen"
__email__ = "Mats.Larsen@sintef.no"
__status__ = "Development"
__date__ = "27032020"
__version__ = "1.0"
#--------------------------------------------------------------------
#IMPORT
#--------------------------------------------------------------------
from .revpi_daq_controller import RevPi_DAQ_Controller
from .revpi_daq_controller import States
import os
import csv
#--------------------------------------------------------------------
#CONSTANTS
#--------------------------------------------------------------------
#--------------------------------------------------------------------
#METHODS
#--------------------------------------------------------------------
def load_params(path):
    '''
    Loading parameter list
    '''
    print('Loading parameter list at path : {}'.format(path))
    params = {}

    with open('{}'.format(path)) as csvfile:

        line = csv.DictReader(csvfile,delimiter=',', quotechar='"')
        count = 0
        for row in line:

            params[row['name']] = row
    return params
#--------------------------------------------------------------------
# CLASSES
#--------------------------------------------------------------------
class RevPi_DAQ_API(RevPi_DAQ_Controller):
    '''
    Class for API of revpi daq
    '''
    def __init__(self,pins,**kwargs):
        '''
        Constructor for REVPODAQ API
        Params : The same params from RevPi_DAQ_Controller
        '''
        #Inheritance
        RevPi_DAQ_Controller.__init__(self,inputs=pins,**kwargs)

    def get_async_sample(self,io=None):
        '''
        Get asynchrony samnple independent of the control loop
        '''
        return self.get_value(io)

    def get_samples(self):
        '''
        Return a samples from the FIFO quene. This is properly a thread action to
        get data.
        '''
        d = {}
        while self.quene_empty() == False:
            s = self.get_quene_sample()
            for key,val in s.items():
                if key not in d.keys(): d[key] = []
                d[key].append(val)
        return d

    def event(self):
        '''
        Set state to event, an event based state that can be triggered from external.
        Params:
        Return:
        '''
        self.set_state(States.EVENT)

    def event_sample(self):
        '''
        Trigger a event based sampling. The state has to be event.
        '''
        if self.__c_state == States.EVENT:
            self.trigger_event()
        else:
            print('The state is {}, it has to be in EVENT'.format(self.__c_state))

    def idle(self):
        '''
        Set state to idle.
        Params:
        Return:
        '''
        self.set_state(States.IDLE)

    def reset(self):
        '''
        Set state to idle.
        Params:
        Return:
        '''
        self.set_state(States.IDLE)
        self.reset_queue()

    def start_logging(self):
        '''
        Start intern logging. The logging can be stopped by calling the
        method idle.
        Params:
        Return:
        '''
        self.set_state(States.INTERNLOGGING)
