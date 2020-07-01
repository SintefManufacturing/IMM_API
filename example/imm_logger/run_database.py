#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#Module Description
#--------------------------------------------------------------------
"""
Example how to use imm logger system.
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
#IMPORT
#--------------------------------------------------------------------
import imm
import imm_cell
#--------------------------------------------------------------------
#CONSTANTS
#--------------------------------------------------------------------
PYRONAME = 'IMM.EXAMPLE'
PYRONAME_PI = 'PI.EXAMPLE'
NS = ['172.16.0.98',9001]
Sampling_Time = 1
#--------------------------------------------------------------------
#METHODS
#--------------------------------------------------------------------
if __name__ == "__main__":

    emi = imm_cell.get_proxy(PYRONAME,NS)
    pi = imm_cell.get_proxy(PYRONAME_PI,NS)
    # Create database
    db = imm_cell.API(folder='imm_database',
                     json=True,
                     pickle=False,
                     csv=False,
                     devices=[emi,pi])
    db.sample_shots(sampling_time=Sampling_Time)
