#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#Module Description
#--------------------------------------------------------------------
"""
Class to handle process parameters.
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
__date__ = "30032020"
__version__ = "1.0"
#--------------------------------------------------------------------
#IMPORT
#--------------------------------------------------------------------
#--------------------------------------------------------------------
# CLASSES
#--------------------------------------------------------------------
class ProcessParam():
    '''
    Class for update params data with different cycle.
    '''
    def __init__(self,name,get,set,threshold,unit):
        '''
        Instantiate updateParams.
        Params:
        - name -> str : Name of the process parameter
        - get  -> str : uri for getting the actual value
        - set  -> str : URI for set the control value
        - threshold [str,str] : for setting the threshold
        - unit -> float : The update cycle for a parameter in unit[ms]
        '''
        # Argument
        self.__name = name
        self.__get = get
        self.__set = set
        self.__threshold = threshold
        self.__unit = unit

    def __check_params(self):
        '''
        '''
        if self.__get == '0' or type(self.__get ) != str:
            self.__get = None
        if self.__set == '0' or type(self.__set ) != str:
            self.__set = None
        if self.__name == '0' or type(self.__name ) != str:
            self.__name = None
        if self.__threshold == '0' or type(self.__threshold ) != list:
            self.__threshold = None

    def find(self, key):
        '''
        '''
        if self.get == key or self.set == key:
            return self.name
        elif self.__threshold is not None:
            if self.__threshold[0] == key or self.__threshold[1] == key:
                return self.name
        else: return None

    @property
    def get(self):
        '''
        '''
        return self.__get

    @property
    def set(self):
        '''
        '''
        return self.__set

    @property
    def name(self):
        '''
        '''
        return self.__name

    @property
    def threshold(self):
        '''
        '''
        return self.__threshold
