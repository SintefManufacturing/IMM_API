#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
# Module Description
#--------------------------------------------------------------------
'''
This module is the IMM controller of the EMI interface.
'''
#--------------------------------------------------------------------
# Administration Details
#--------------------------------------------------------------------
__author__ = "Mats Larsen"
__copyright__ = "2020 [NTNU Gjøvik and SINTEF Manufacturing]"
__credits__ = ["Mats Larsen", "Olga Ogorodnyk"]
__license__ = "MIT"
__maintainer__ = "Mats Larsen"
__email__ = "Mats.Larsen@sintef.no"
__status__ = "Development"
__date__ = "30032020"
__version__ = "1.0"
#--------------------------------------------------------------------
# IMPORT
#--------------------------------------------------------------------
import imm
import threading
import queue
import datetime
import time
import copy
#--------------------------------------------------------------------
# CONSTANTS
#--------------------------------------------------------------------
IDLE_TIME = 10 # Units is  seconds. Time that the connection can be idle
#--------------------------------------------------------------------
# CLASSES
#--------------------------------------------------------------------
class States:
    IDLE = 1
    EVENT = 2
    INTERNLOGGING = 3

class Protocol:
    EMI = 'emi'

class SamplingRateMode:
    '''
    Mode for the sampling. It can be either
    - A fixed sampling rate for all parameter
    - A flexible sampling rate, because not all parameter have the same update cycle
    '''
    FIXED_STEP = 'Fixed sampling step'
    FLEXIBLE_CYCLES = 'Flexible update cycles'

class IMMController(threading.Thread, imm.EMI_Interface):
    '''
    Constructor of the IMMInterface
    '''

    def __init__(self, **kwargs):
        '''
        Instantiate EMI with params.
        Params:
        - sampling_mode     -> SamplingRateMode : The mode for sampling
        - sampling_rate     -> float            : Sampling rate for fixed sampling mode
        - uri       -> list<str>             : A collection of params that the machien can log
        - protocol -> Protocol : Type protocol that will be applied
        '''
        #--------------------------------------------------------------------
        #Arguments
        #--------------------------------------------------------------------
        self.__kwargs = kwargs
        self.__uri = kwargs.get('uri',[]) # Uniform Resource Identifier for parameters
        self.__sampling_mode = kwargs.get('sampling_mode',SamplingRateMode.FIXED_STEP)
        #self.__kwargs['sampling_mode'] = self.__sampling_mode
        self.__sampling_rate = kwargs.get('sampling_rate',0.1)
        self.__debug = kwargs.get('debug',False)

        #Inheritance
        if kwargs.get('protocol','emi'):
            imm.EMI_Interface.__init__(self,**kwargs)
        else:
            print('Not implemented')
            raise

        # Local Artributes
        # Transfrom uri to uptateparms instances

        self.__last_action = datetime.datetime.now() - datetime.timedelta(days=1)    # Datetime for last action
        self.__q = queue.Queue()     # The quene LIFO with samples

        #Threading
        threading.Thread.__init__(self)     # initialize this thread
        self.daemon = True                  # Close if main loop stops

        #--------------------------------------------------------------------
        # State machine
        #--------------------------------------------------------------------

        # Event for sample data
        self.__sync = threading.Event()
        self.__sync.clear()
        self.__event_quene = queue.Queue()
        # Event state transition
        self.__t_trigger = threading.Event()
        self.__t_trigger.clear()

        # Next state
        self.__nx_state = States.IDLE
        self.__c_state = States.IDLE

    def init(self):
        '''
        '''
        if self.__debug: print('Trying to initialize the machine')
        # Connect to machine
        if self.connect() == False:       # Connect to IMM
            print('Did not connect correctly')
            sys.exit()

        self.logout()        # First logout and then login
        self.login()         # Login
        # Start the thread
        self.start()
        print('IMM Controller started')

    def get_sample(self):
        '''
        Return a sample from the quene. This is properly a thread action to
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

    def reset(self):
        '''
        Reset samples and set to idle
        '''
        self.set_state(States.IDLE)
        self.__q = queue.Queue()
        self.__event_quene = queue.Queue()

    def quene_is_empty(self):
        '''
        Check of the queue is full for empty.
        Params:
        Returns:
        err -> Bool : Queue is empty return True otherwise return False
        '''
        if self.__q.empty(): return True
        else: return False

    def __sample_quene(self,d,debug=False):
        '''
        Set a data to queue
        '''
        if self.__q.full() == False:
            self.__q.put(d)

        if debug: print('len of the queue {}'.format(self.__q.qsize()))

    def close(self):
        '''
        '''
        self.__alive = False

    def __idle(self):
        '''
        Set the thread to go to idle state.
        Params:
        Return:
        '''
        # In idle to ensure a connection
        if self.__debug: print('Idle State')

        # Compute sleep time based on idle time, before the connection will be disconencted
        sleep_time = IDLE_TIME - (datetime.datetime.now()-self.__last_action).total_seconds()

        if sleep_time > 0: # Goto sleep
            self.__t_trigger.wait(timeout=sleep_time)
        else:   # If no action has happened, then call for info data for active the connection
            self.info_log()

    def trigger_event(self):
        '''
        Trigger for sampling in event state.
        Params:
        Return:
        '''
        self.__event_quene.put(True)

    def __sample_to_queue(self):
        '''
        '''
        # The sampling mode is fixed
        if self.__sampling_mode == SamplingRateMode.FIXED_STEP:
            d = self.get_value() # Get data
            self.__sample_quene(d,debug=self.__debug)    # Put it in queue

        elif self.__sampling_mode == SamplingRateMode.FLEXIBLE_CYCLES:
            d = self.__getParamsOnCycle(past_time=past,debug=False)   # Get data
            if d !=  None:
                self.__sample_quene(d,debug=self.__debug)    # Put it in queue

    def __event(self):
        '''
        Set the thread to go to event state
        Params:
        Return:
        '''
        # Triger idle mode
        self.__event_quene.get(block=True)
        if self.__t_trigger.isSet() == False:
            self.__sample_to_queue()

    def __intern_logging(self):
        '''
        Start intern logging.
        Params:
        Return:
        '''
        self.__sample_to_queue()    # Put it in queue

        # Get sleep time
        sleep_time = self.__sampling_rate - (datetime.datetime.now()-self.__last_action).total_seconds()
        #print('Sleep time : {}, rate : {}'.format(sleep_time,self.__sampling_rate))
        if sleep_time > 0:
            self.__t_trigger.wait(timeout=sleep_time)

    def run(self):
        '''
        Run thread
        Params:
        Returns:
        '''
        # Runs forever if alive is true
        self.__alive = True
        while(self.__alive):
            if self.__nx_state != self.__c_state:
                self.__t_trigger.clear()
                self.__event_quene = queue.Queue()
                self.__c_state = self.__nx_state

                print('Changed to new state {}'.format(self.__c_state))

            if self.__c_state == States.IDLE:
                self.__idle()
            elif self.__c_state == States.EVENT:
                self.__event()
            elif self.__c_state == States.INTERNLOGGING:
                self.__intern_logging()

            else:
                sys.exit(0)

    def get_value(self,uri=None):
        '''
        Get all the parameter we wanted from the parameter list.
        Params:
        Return:
        - Dict : Dict with all uri and the respectively results
        '''
        self.__last_action = datetime.datetime.now()
        if uri is None:
            return self.get_param_value(param_uri=self.__uri)
        else:
            return self.get_param_value(param_uri=uri)
