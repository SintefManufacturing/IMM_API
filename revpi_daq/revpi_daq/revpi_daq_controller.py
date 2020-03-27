#--------------------------------------------------------------------
#Module Description
#--------------------------------------------------------------------
"""
Class to communicate with Rev PI
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
import threading
import queue
import time
import datetime
from .rev_pi import RevPi
#--------------------------------------------------------------------
#METHODS
#--------------------------------------------------------------------
#--------------------------------------------------------------------
# CLASSES
#--------------------------------------------------------------------
class States:
    IDLE = 1
    EVENT = 2
    INTERNLOGGING = 3

class RevPi_DAQ_Controller(threading.Thread, RevPi):
    '''
    Class for interaction with mould over PI
    '''
    def __init__(self,**kwargs):
        '''
        Constructor for PI
        Params:
        - name          -> str : Name of this instance
        - sampling_rate -> float : Defining the sampling freq for the time based sampling
        - inputs        -> Dict <string,string> : Key is the parameter name and value is input name
        '''
        #Inheritance
        RevPi.__init__(self)
        #--------------------------------------------------------------------
        # Argument
        #--------------------------------------------------------------------
        self.__name = kwargs.get('name','revpi')
        # Sampling time period
        self.__sampling_rate = kwargs.get('sampling_rate',0.5)

        # Input
        self.__input = kwargs.get('inputs',{})
        print('Selected inputs are : {}'.format(self.__input))

        #--------------------------------------------------------------------
        # Arbritues
        #--------------------------------------------------------------------
        # Quene
        self.__q = queue.Queue()             # The quene LIFO with samples
        self.__last_timestamp = None

        # Event for sample data
        self.__sample_trigger = threading.Event()
        self.__sample_trigger.clear()

        # Event state transition
        self.__t_trigger = threading.Event()
        self.__t_trigger.clear()

        self.__event_quene = queue.Queue()

        # Next state
        self.__nx_state = States.IDLE
        self.__c_state = States.IDLE

        self.__alive = True
        #Threading
        threading.Thread.__init__(self)     # initialize this thread
        self.daemon = True                  # Close if main loop stops
        self.start()                       # starting the thread

        print('Interface started')

    def get_quene_sample(self):
        '''
        Return a sample from the FIFO quene. This is properly a thread action to
        get data.
        Params:
        Return:
        - d -> Dict : Data from machine
        '''
        try:
            # Get data from quene
            d = self.__q.get(block=True,timeout=0.1)
        except:
            d = None
        return d

    def quene_empty(self):
        '''
        Check of the queue is full for empty.
        Params:
        Returns:
        err -> Bool : Queue is empty return True otherwise return False
        '''
        if self.__q.empty(): return True
        else: return False

    def get_value(self,io=None):
        '''
        Returning value of analog input from daq, that is converted.
        Params:
        - io -> string : Name of the imput
        Returns:
        -> dict : Result of input by and name and value
        '''
        # Get start time for sampling
        s_date = datetime.datetime.now()

        # Container
        data = {}
        if io is None:

            for key,val in self.__input.items():
                data['{}_{}'.format(key,val['unit'])] = self.get_analog_input(val['pin'])/float(val['conversion'])
        else:
            for key,val in io.items():
                data['{}_{}'.format(key,val['unit'])] = self.get_analog_input(val['pin'])/float(val['conversion'])
        # Get end time for sampling
        e_date = datetime.datetime.now()
        timestamp = s_date + (e_date-s_date)/2.0
        data['timestamp_{}'.format(self.__name)] = timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        self.__last_timestamp = timestamp
        return data

    def __intern_logging(self):
        '''
        Start intern logging.
        Params:
        Return:
        '''
        self.__sample_queue(self.get_value())    # Put it in queue

        # Get sleep time
        sleep_time = self.__sampling_rate - (datetime.datetime.now()-self.__last_timestamp).total_seconds()
        #print('Sleep time : {}, rate : {}'.format(sleep_time,self.__sampling_rate))
        if sleep_time > 0:
            self.__t_trigger.wait(timeout=sleep_time)

    def __idle(self):
        '''
        Set the thread to go to idle state.
        Params:
        Return:
        '''
        # Triger idle mode
        self.__t_trigger.wait()

    def trigger_event(self):
        self.__event_quene.put(True)
        #self.__sample_trigger.set()

    def __event(self):
        '''
        Set the thread to go to event state
        Params:
        Return:
        '''
        # Trigger idle mode
        self.__event_quene.get(block=True)

        if self.__t_trigger.isSet() == False:
            self.__sample_queue(self.get_value())    # Put it in queue

    def set_state(self,state):
        '''
        Set the thread to go to a new state.
        Params:
        - state -> States : Enum for state
        Return:
        '''
        self.__nx_state = state
        self.__t_trigger.set()
        self.__event_quene.put(True)

    def reset_queue(self):
        '''
        Reset samples and set to idle
        '''
        self.__q = queue.Queue()
        self.__event_quene = queue.Queue()

    def __sample_queue(self,d,debug=False):
        '''
        Set a data to the FIFO queue
        '''
        if self.__q.full() == False:
            self.__q.put(d)

        if debug: print('len of the queue {}'.format(self.__q.qsize()))

    def run(self):
        '''
        This thread has to two methods.
        1) It can be logging continously and put the data in quene.
        2) Thead method to ensure that the connection is up and running. Runs every
        IDLE_TIME to verify that there is action. If no action is happening,
        this method is asking for info data for action to happining.
        Params:
        Returns:
        '''
        # Runs forever
        print('Thread starting')
        while(self.__alive):
            # Lower section
            if self.__nx_state != self.__c_state:
                 self.__t_trigger.clear()
                 #self.__sample_trigger.clear()
                 self.__event_quene = queue.Queue()
                 self.__c_state = self.__nx_state
                 print('Changed to new state {}'.format(self.__c_state))

            # Upper section
            if self.__c_state == States.IDLE:
                self.__idle()
            elif self.__c_state == States.EVENT:
                self.__event()
            elif self.__c_state == States.INTERNLOGGING:
                self.__intern_logging()

            else:
                sys.exit(0)
