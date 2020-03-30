#--------------------------------------------------------------------
#Module Description
#--------------------------------------------------------------------
"""
Example to communicate with EMI as a normal python script.
This is an example how to use EMI
"""
#--------------------------------------------------------------------
# Administration Details
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
import imm
#--------------------------------------------------------------------
#CONSTANTS
#--------------------------------------------------------------------
#Parameters settings for config EMI
NAME = 'EMI'
IP = '172.16.10.39'
PORT = 10050
USERNAME = 'name'
PASSW = 'code'
uri_shotcounter = 'cc300://imm/cm#//c.ShotCounter/p.sv_iShotCounter/v'
#--------------------------------------------------------------------
#METHODS
#--------------------------------------------------------------------
if __name__ ==  "__main__":
    '''
    Testing this module by connecting to the machine and perform several methods
    '''
    #Create EMI_INTERFACE
    e = imm.EMI_Interface(name=NAME,
                          ip=IP,
                          port=PORT,
                          username=USERNAME,
                          passw=PASSW,
                          debug=True
                          )
    # Connect to machine
    if e.connect() == False:       # Connect to IMM
        print('Did not connect correctly')
        sys.exit()
    e.logout()        # First logout and then login
    e.login()         # Login

    # Get parameter
    param = e.get_param_value(uri_shotcounter)
    print('Get Shot Counter : %s' %param)

    # Logout
    e.logout()

    # Close emi
    e.close()
    del e
