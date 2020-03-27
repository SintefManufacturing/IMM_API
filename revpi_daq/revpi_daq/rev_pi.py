#--------------------------------------------------------------------
#Module Description
#--------------------------------------------------------------------
"""
Module to communicate with Rev PI
"""
#--------------------------------------------------------------------
#Administration Details
#--------------------------------------------------------------------
__author__ = "Mats Larsen"
__copyright__ = "2020 [NTNU Gjøvik and SINTEF Manufacturing"
__credits__ = ["Mats Larsen","Olga Ogorodnyk","Anders Svenskerud Bækkedal"]
__license__ = "SRM"
__maintainer__ = "Mats Larsen"
__email__ = "Mats.Larsen@sintef.no"
__status__ = "Development"
__date__ = "27032020"
__version__ = "1.0"
#--------------------------------------------------------------------
#IMPORT
#--------------------------------------------------------------------
import revpimodio2
#--------------------------------------------------------------------
#METHODS
#--------------------------------------------------------------------
#--------------------------------------------------------------------
# CLASSES
#--------------------------------------------------------------------
class RevPi():
    '''
    Class for interaction with REV PI
    '''
    def __init__(self,**kwargs):
        #--------------------------------------------------------------------
        # Arbrittues
        #--------------------------------------------------------------------
        # Reference to the pi
        self.__rpi = revpimodio2.RevPiModIO(autorefresh=True)

        # Handle SIGINT / SIGTERM to exit program cleanly
        self.__rpi.handlesignalend(self.cleanup_revpi)

    def cleanup_revpi(self):
        '''
        Cleanup function to leave the RevPi in a defined state.
        '''
        # Switch of LED and outputs before exit program
        self.__rpi.core.a1green.value = False

    def get_analog_input(self,io):
        '''
        Returning value of input.
        Params:
        - io -> string : Name of the imput
        Returns:
        -> Float : Result of input
        '''
        return self.__rpi.io['InputValue_{}'.format(io)].value
