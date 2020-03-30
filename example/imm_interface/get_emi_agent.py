#--------------------------------------------------------------------
#Module Description
#--------------------------------------------------------------------
"""
Script to communicate with IMM as a service with PYRO4.
This is an example how to get imm proxy.
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
#Import
#--------------------------------------------------------------------
import sys
import imm
from xml.etree import ElementTree as et
#--------------------------------------------------------------------
#CONSTANTS
#--------------------------------------------------------------------
PYRONAME = 'IMM.EXAMPLE'
NS = ['172.16.0.98',9001]
#--------------------------------------------------------------------
#METHODS
#--------------------------------------------------------------------
if __name__ == "__main__":
    # Getting the emi proxy
    print('Trying to get link')
    p = imm.get_proxy(PYRONAME,NS)
    d = p.get_async:sample()
    print(d)
    d.disconnect()
