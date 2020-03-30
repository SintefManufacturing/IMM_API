#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#Module Description
#--------------------------------------------------------------------
'''
This module is the facade class for the EMI interface.
'''
#--------------------------------------------------------------------
#IMPORT
#--------------------------------------------------------------------
from .imm_controller import IMMController, States
import csv
from .process_params import ProcessParam
#--------------------------------------------------------------------
#CONSTANTS
#--------------------------------------------------------------------
# path to CSV
PATH_VALUES = ['path_act_value','path_set_low_value','path_set_high_value','path_set_value']
#--------------------------------------------------------------------
# CLASSES
#--------------------------------------------------------------------
class IMM_API(IMMController):
    '''
    IMM API class, it is the top-level of the EMI package.
    '''
    def __init__(self,params_path,**kwargs):
        '''
        Constructor for REVPODAQ API
        Params : The same params from IMMController
        '''
        # load params from csv on a specific format
        params = self.__load_params(params_path)
        # Define update parameters
        self.__pp = self.__preparePP(params)
        uri = [self.__pp[i].get for i in self.__pp.keys()]
        # Create controller
        IMMController.__init__(self,uri=uri,**kwargs)
        self.init()

    def __load_params(self,path):
        '''
        Loading parameter list
        '''
        print('Loading parameter list at path : {}'.format(path))
        params = {}
        with open('{}'.format(path)) as csvfile:

            line = csv.DictReader(csvfile,delimiter=',', quotechar='"')
            count = 0
            for row in line:

                params[row['name']] = row
        return params

    def __preparePP(self,params):
        '''
        Prepare uri to a list of if process parameters instances.
        Params:
        - params -> List<string> : URI for process parameters
        Return:
        - uris  -> Dict[UpdateParams]
        '''
        print('Prepraring UpdateParms list')
        # List with ParamUpdates instances
        pp = {}
        # Loop the parameter list
        for key,value in params.items():
            # IF the enable is 1, and wanted to be used
            if value['enable'] == '1':
                pp[key] = ProcessParam(name=key,
                                       get=value[PATH_VALUES[0]],
                                       set=value[PATH_VALUES[3]],
                                       threshold=[value[PATH_VALUES[1]],value[PATH_VALUES[2]]],
                                       unit=value['unit']
                                       )
        return pp

    def set_process_param(self,param,value):
        '''
        Setting process param for set value or a threshold boundary
        '''
        p = self.__pp[param]
        if p.set is not None:
            set_val = [p.set]
            value = [value]
        elif p.threshold is not None:
            set_val = p.threshold
        else:
            return None
        r = {}
        for i in range(0,len(set_val)):
            print('set {} to {}'.format(param,value[i]))
            self.set_param_value(set_val[i],value[i])
        return self.get_process_param(param)

    def get_process_param(self,param):
        '''
        Returning process param.
        '''
        p = self.__pp[param]
        if p.set is not None:
            set_val = [p.set]

        elif p.threshold is not None:
            set_val = [p.threshold]
        else: set_val = []
        d = self.get_param_value(set_val)
        r = []
        for i in set_val:
            r.append(d[i])
        return r

    def get_async_act_sample(self,uri=None):
        '''
        Get asynchrony sample independent of the control loop
        '''
        d = self.get_value(uri)
        d = self.__convert(d)
        return d

    def __convert(self,d):
        '''
        '''
        for key in d.keys():

            for name,data in self.__pp.items():
                r = data.find(key)

                if r is not None: break

            if r is not None:
                d[r] = d[key]
                del d[key]

        return d

    def get_samples(self):
        '''
        Return samples from the FIFO quene. This is properly a thread action to
        get data.
        '''
        d = {}
        while self.quene_is_empty() == False:
            s = self.get_sample()

            for key,val in s.items():
                if key not in d.keys(): d[key] = []
                d[key].append(val)
        d = self.__convert(d)
        return d

    def event(self):
        '''
        Set state to event, an event-based state that can be triggered from external.
        Params:
        Return:
        '''
        self.set_state(imm.States.EVENT)

    def event_sample(self):
        '''
        Trigger a event based sampling. The state has to be event.
        '''
        if self.__c_state == imm.States.EVENT:
            self.trigger_event()
        else:
            print('The state is {}, it has to be in EVENT'.format(self.__c_state))

    def idle(self):
        '''
        Set state to idle.
        Params:
        Return:
        '''
        self.set_state(imm.States.IDLE)

    def disconnect(self):
        '''
        Disconnect to the machine
        '''
        self.close()

    def start_logging(self):
        '''
        Start intern logging. The logging can be stopped by calling the
        method idle.
        Params:
        Return:
        '''
        self.set_state(imm.States.INTERNLOGGING)
