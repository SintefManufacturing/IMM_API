#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#Module Description
#--------------------------------------------------------------------
'''
This module is for ENGEL Machine database logging system.
'''
#--------------------------------------------------------------------
# #Administration Details
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
import time
import datetime
import os
import threading
import Pyro4
import imm
import json
import csv
#--------------------------------------------------------------------
#CONSTANTS
#--------------------------------------------------------------------
# URI for check for mould opening
OPENINGMOULD_URI = 'cc300://imm/cm#//c.Mold1/p.sv_MeasActClmpForce/v/p.rAct/v'
# Threshold to decide of the mould is open
THRESHOLD_MOULD_OPENING = 300 # kN
#--------------------------------------------------------------------
# CLASSES
#--------------------------------------------------------------------
class IMM_Logging_System(threading.Thread):
    '''
    The class for database logging.
    '''
    def __init__(self,**kwargs):
        '''
        Instantiate database for engel database.
        Params:
        - folder    -> str : The folder to save the samples
        - sampling_mode -> SamplingMode : Mode of the sampling
        - devices -> [Any] : Device we want to log
        Returns:
        '''
        #--------------------------------------------------------------------
        # Arguments
        #--------------------------------------------------------------------
        self.__folder = kwargs.get('folder',None,)
        self.__csv = kwargs.get('csv',False)
        self.__json = kwargs.get('json',False)
        self.__pickle = kwargs.get('pickle',False)
        # Initlaize database interface to machine
        self.__devices = kwargs.get('devices',[])

        # Define folder for sampled data
        date = datetime.datetime.now()
        self.__sampling_folder = r'{}\experiment_{}_{}_{}_{}_{}'.format(self.__folder,date.day,date.month,date.day,date.hour,date.minute)
        del date
        self.__data = []

        #--------------------------------------------------------------------
        # Local Attributes
        #--------------------------------------------------------------------
        self.__last_timestamp = datetime.datetime.now()
        # Define the status for the machine, if the machine is doing injection
        self.__busy = threading.Event()
        self.__busy.clear()

        # Initialize this thread
        threading.Thread.__init__(self)
        self.daemon = True      # End if main loop stops
        self.start()            # Start agent thread

    def __sampleConstant(self):
        '''
        Sample constant without mould closing
        '''
        samples = []
        self.__emi.reset()
        self.__emi.startLogging()
        self.__data = []
        while 10> len(self.__data):
            self.__getSample()
        self.__emi.idle()
        if self.__csv:
            self.__saveCSV(self.__sampling_folder,self.__data,'shot1')
        c_data,timestamps = self.__emi.convertUrisToDataSet(self.__data)

        return c_data,timestamps

    def __getSample(self):
        '''
        Returning the next sample in the queue.
        Params:
        Returns:
        '''
        # Get sample
        d = self.__emi.get_quene_sample()

        # If the sample is valid, insert into queue
        if d != None:
            uri = self.__emi.get_param_uris()
            valid = True
            for i in uri:
                #print(i)
                if i not in d.keys():
                    valid = False
            if valid:
                self.__data.append(d)

    def __sampleClosedMould(self):
        '''
        Start logging only when the mould is closed.
        Params:
        number_of_samples -> int : Number of desired sampling
        sampling_rate -> float : Sampling rate in seconds.
        '''
        # Trigger event sampling
        self.__trigger_event()
        # Wait for mould to open
        return self.__checkMouldOpening() #== True:

    def run(self):
        '''
        '''
        self.__alive = True
        while(self.__alive):
            a = str(input("----------------------------------\n" +
                      "Menu: \n" +
                      "0 - Quit \n" +
                      "----------------------------------\n"))
            if a == str("0"): # stop the thread by break
                #del self.__inst
                self.__alive=False # end active thread

    def __reset_devices(self):
        '''
        '''
        for i in self.__devices: i.reset()

    def __idle(self):
        '''
        '''
        for i in self.__devices: i.idle()

    def __event(self):
        '''
        '''
        for i in self.__devices: i.event()

    def __get_samples(self):
        '''
        '''
        d = {}
        for i in self.__devices:
            s = i.get_samples()
            print('s : {}'.format(s))
            for key,val in s.items():
                d[key] = val
        return d

    def __trigger_event(self):
        '''
        '''
        for i in self.__devices: i.trigger_event()
        self.__last_timestamp = datetime.datetime.now()

    def sample_shots(self,sampling_time):
        '''
        '''
        count = 1
        while(self.__alive):
            print('Loop : nr {}'.format(count))
            self.__reset_devices()
            self.__event()

            # Wait for mould to closing
            self.__waitMouldClosing()
            acc_time = datetime.datetime.now()
            while self.__sampleClosedMould() ==False and self.__alive == True:
                acc_time += datetime.timedelta(seconds=sampling_time)
                t = (acc_time-datetime.datetime.now()).total_seconds()
                if t > 0: time.sleep(t)
            # Stop logging
            time.sleep(1)
            self.__idle()
            # Reset data
            d = self.__get_samples()

            # Save dataset to file
            self.__saveShot(folder=r'{}'.format(self.__sampling_folder), # Folder where to save file
                            file_name='shot_{}.json'.format(count),          # Name of file
                            data=d)                           # Data parameters
                            #timestamps=timestamps)                  # Timestamps
            count += 1

    def startLogging(self,):
        '''
        Starting to log the machine with the given settings.
        Params:
        Return:
        '''
        # Sample if the mode is constant
        count = 1
        while(self.__alive):
            print('Loop : nr {}'.format(count))
            self.__.reset()
            self.__event()

            if self.__sampling_mode == SamplingMode.CONSTANT:
                data,timestamps = self.__sampleConstant()

                self.__saveShot(folder=self.__sampling_folder,
                                file_name='shot1',
                                data=data,
                                timestamps=timestamps)

            count += 1

    def __saveCSV(self,file_name,d):
        '''
        '''
        p = pandas.DataFrame(d)
        p.to_csv(file_name,encoding='utf-8',index=False)

    def __save_json(self,path,d):
        '''
        Save a whole dict to json.
        Params:
        - d -> Dict : Dict we want to save to file
        '''
        with open(path, 'w') as outfile:
            json.dump(d, outfile,sort_keys=True, indent=4, separators=(',', ': '))

    def __saveShot(self,folder,file_name,data):
        '''
        '''
        path = os.path.join(folder,file_name)
        dir_path = os.path.dirname(path)
        try:
            os.stat(dir_path)
        except:
            os.makedirs(dir_path)
        # Save to csv if wanted
        if self.__csv:

            self.__saveCSV(file_name='{}.csv'.format(file_name),d=data)

        if self.__pickle:
            f = file_classes.PickleDict(folder=folder,file_name=file_name)
            f.save(data)
        if self.__json:
            self.__save_json(path,data)

    def getIMMBusy(self):
        '''
        Return the state of the IMM is busy
        Params:
        Return:
        - Event : State of the IMM
        '''
        return self.__busy.isSet()

    def __checkMouldOpening(self):
        '''
        Checking if the mould is opening.
        Params:
        Return: -> Bool : True for opening
        '''
        ret = self.__devices[0].get_param_value(OPENINGMOULD_URI)
        ret = float(ret[OPENINGMOULD_URI]) # To float
        if ret > THRESHOLD_MOULD_OPENING:
            return False
        else:
            self.__busy.clear()
            return True

    def __waitMouldClosing(self):
        '''
        Waiting for the IMM to close by observe the clamping force.
        Params:
        Return:
        '''
        # Uri to clamping force
        ret = 0
        print('Wait for closing mould')
        # Wait for the force is over 300
        while  ret < THRESHOLD_MOULD_OPENING:
            # Sleep
            time.sleep(0.1)
            # Get the current force
            ret = self.__devices[0].get_param_value(OPENINGMOULD_URI)
            ret = float(ret[OPENINGMOULD_URI]) # To float
            print('Value of openning mould : {}'.format(ret))

        # IMM is busy
        self.__busy.set()
        print('Set IMM to busy')

def get_proxy(name,ns):
    '''
    Returning a proxy
    Params:
    - name -> str : Name of the pyro4 object
    - ns   -> list : List of ip and port
    '''
    # Configure to pickle
    Pyro4.config.SERIALIZER = "pickle"
    Pyro4.config.SERIALIZERS_ACCEPTED=["pickle"]

    ns_ = Pyro4.locateNS(host=ns[0],port=ns[1])
    uri = ns_.lookup(name)
    return Pyro4.core.Proxy(uri)
