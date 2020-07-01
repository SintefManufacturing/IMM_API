#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#Module Description
#--------------------------------------------------------------------
"""
Class to communicate with EMI as a service with PYRO4.
"""
#--------------------------------------------------------------------
#Administration Details
#--------------------------------------------------------------------
__author__ = "Mats Larsen"
__copyright__ = "2020 [NTNU Gjøvik and SINTEF Manufacturing]"
__credits__ = ["Mats Larsen", "Aadne Solhaug Linnerud"]
__license__ = "MIT"
__maintainer__ = "Mats Larsen"
__email__ = "Mats.Larsen@sintef.no"
__status__ = "Development"
__date__ = "30032020"
__version__ = "1.0"
#--------------------------------------------------------------------
#IMPORT
#--------------------------------------------------------------------
import imm
import socket
import threading
import Pyro4
import time
#--------------------------------------------------------------------
#METHODS
#--------------------------------------------------------------------
def get_ip(ns=None):
    '''
    Return a ip that is in range of namespace
    Params:
    - ns -> str : The namespace ip
    Return:
    - ip -> str : A ip-address that fits into the namespace
    '''
    for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
        sub = ns.split('.')
        if ip.find('{}.{}'.format(sub[0],sub[1])) >= 0:
            return ip
    return None

#--------------------------------------------------------------------
# CLASSES
#--------------------------------------------------------------------
class IMMProxy(threading.Thread):
    '''
    Class for emi to handle the agent version of emi.
    '''
    def __init__(self,**kwargs):
        '''
        Constructor for agent
        Params:
        - params -> dict : Config name of the sensor
        - pyro4_params -> dict : Pyro4 parameters
        '''
        # Arguments
        params = kwargs.get('params')
        pyro4_params = kwargs['pyro4_params']      # Pyro4 parameter
        #local variables
        self.__alive = True         # IF sensor is running

        # Initialize this thread
        threading.Thread.__init__(self)
        self.daemon = True      # End if main loop stops
        self.start()            # Start agent thread

        # Configure to pickle and pyro4
        Pyro4.config.REQUIRE_EXPOSE = False
        Pyro4.config.SERIALIZER = "pickle"
        Pyro4.config.SERIALIZERS_ACCEPTED=["pickle"]
        class_ = Pyro4.expose(imm.IMM_API)    # Expose class methods

        # Create an instance
        self.__inst = class_(**params)

        # Get Pyro4 deamon and register daemon
        self.__daemon = Pyro4.core.Daemon(host=get_ip(pyro4_params['ns'][0]))
        uri = self.__daemon.register(self.__inst)

        # Locate the nameserver
        ns = Pyro4.locateNS(host=pyro4_params['ns'][0],
                            port=pyro4_params['ns'][1])
        # Register instance
        ns.register(pyro4_params['name'], uri)

        print ("Servername(LINK) = {} and serializer = {}, use this servername, if you want to subscribe it".format(pyro4_params['name'],Pyro4.config.SERIALIZER))

        # Initialize emi interface
        #if kwargs.get('initialize',True):
        #    self.__initialize()

        # Enter the service loop.
        print('Entering the service loop')
        try:
            self.__daemon.requestLoop()
        except:
            pass
        print('{} Ending'.format(self.__inst))
        del self.__inst

    def run(self):
        '''
        '''
        alive = True
        while(alive):
            a = str(input("----------------------------------\n" +
                      "Menu: \n" +
                      "0 - Quit \n" +
                      "1 - Get Async Value \n" +
                      "2 - IDLE state \n" +
                      "3 - EVENT state \n" +
                      "4 - Sample in EVENT state \n" +
                      "5 - Intern logging state \n" +
                      "6 - Get samples that have been collected \n" +
                      "7 - Reset \n" +
                      "----------------------------------\n"))
            if a == str("0"): # stop the thread by break
                self.__inst.disconnect()
                #del self.__inst
                alive=False # end active thread

            elif a == str("1"): # Get async sample
                print('Async sample -> {}'.format(self.__inst.get_async_sample()))
            elif a == str("2"): # Idle
                self.__inst.idle()
            elif a == str("3"): # Event
                self.__inst.event()
            elif a == str("4"): # Sample in Event state
                self.__inst.trigger_event()
            elif a == str("5"): # Intern logging state
                self.__inst.start_logging()
            elif a == str("6"): # Collected samples
                print('Colected samples -> {}'.format(self.__inst.get_samples()))
            elif a == str("7"): # Reset
                self.__inst.reset()
            else:
                print('Unknown command')

        self.__daemon.shutdown()
        print('IMM proxy is shutting down')
