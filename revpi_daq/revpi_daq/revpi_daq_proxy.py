#--------------------------------------------------------------------
#Module Description
#--------------------------------------------------------------------
"""
Module to communicate with a PI as a service by using PYRO4.
"""
#--------------------------------------------------------------------
#Administration Details
#--------------------------------------------------------------------
__author__ = "Mats Larsen"
__copyright__ = "2020 [NTNU Gjøvik and SINTEF Manufacturing]"
__credits__ = ["Mats Larsen", "Olga Ogorodnyk"]
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
import Pyro4
from .revpi_daq_api import RevPi_DAQ_API
#--------------------------------------------------------------------
#CONSTANTS
#--------------------------------------------------------------------
#--------------------------------------------------------------------
#METHODS
#--------------------------------------------------------------------
#--------------------------------------------------------------------
# CLASSES
#--------------------------------------------------------------------
class RevPI_DAQ_Proxy(threading.Thread):
    '''
    Class for revpi daq service
    '''
    def __init__(self,debug=False,**kwargs):
        '''
        Constructor for agent
        Params:
        - params -> dict : Config name of the sensor
        - pyro4_params -> dict : Pyro4 parameters
        '''
        # Arguments
        params = kwargs.get('params')               # sensor parameter
        pyro4_params = kwargs['pyro4_params']       #  Pyro4 parameter

        #local Artributes
        self.__alive = True         # Indicate if sensor is running


        threading.Thread.__init__(self) # Initialize this thread
        self.daemon = True              # End if main loop stops
        self.start()                    # Start agent thread

        # Configure to pickle and pyro4
        Pyro4.config.REQUIRE_EXPOSE = False
        Pyro4.config.SERIALIZER = "pickle"
        Pyro4.config.SERIALIZERS_ACCEPTED=["pickle"]

        class_ = Pyro4.expose(RevPi_DAQ_API)    # Expose class methods

        # Create a instanse
        self.__inst = class_(**params,debug=debug)

        # Get Pyro4 deamon and register daemon
        self.__daemon = Pyro4.core.Daemon(host='172.16.0.100')
        uri = self.__daemon.register(self.__inst)

        # Locate the nameserver
        ns = Pyro4.locateNS(host=pyro4_params['ns'][0],
                            port=pyro4_params['ns'][1])
        # Register instance
        ns.register(pyro4_params['name'], uri)
        print ("Servername(LINK) = {} and serializer = {}, use this servername, if you want to subscribe it".format(pyro4_params['name'],Pyro4.config.SERIALIZER))

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
        Proxy thread
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
                      "6 - Get samples that has been collected \n" +
                      "7 - Reset \n" +
                      "----------------------------------\n"))
            if a == str("0"): # stop the thread by break
                self.__inst.cleanup_revpi()
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
        print('PI Proxy is shutting down')
