#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
"""
This module is for interaction with IMM over EMI for C300 machines.
Protocol specification:
This specification describes the CC300 EMI data interface (ENGEL Machine Interface)
and its functional possibilities. The EMI interface is directly integrated
in the control and is basically accessible via Ethernet and TCP/IP-Socket through port 10050.

Session Layer:
The session layer is multi-client compatible. This means that several client-programs
can establish a socket-connection to the CC300 control simultaneously and independently of each other.
After the connection has been established, the control at first provides the list of all available commands in XML.
This list is based on WSDL (Web Services Description Language), but not identical to it.

Presentation Layer:
For the presentation layer XML-byte streams are used. This guarantees the machine readability
of the proto-col. The control is the server and does only reply to so-called requests with a response.
In order to simplify the processing in client and server, every data string has to be ended
with the character “0x19“. Therewith the client or server can identify the end of a message
without having to parse the data string immediately via XML.

Types of request:
- Info Log
- Get parameter value based on uri
- Set parameter value based on uri

Methods for EMI interface
connect()                           -> Connecting the machine based on the params
info_log()                          -> Returning the infolog from the machine
login()                             -> Login into the machine based on the user data
logout()                            -> Login out of the machine
set_param_value(param_uri, value)   -> Setting parameter value based on a uri
get_param_value(param_uri)          -> Returning the value of the parameter based on uri
get_param_details(param_uri)        -> Returning details about a parameter based on uri
get_parameter_text(param_uri)       -> Returning the parameters description
get_process_dataset(min_r,max_r)    -> Returning the dataset of uris
"""
#--------------------------------------------------------------------
#MODULE
#--------------------------------------------------------------------
__author__ = "Mats Larsen"
__copyright__ = "2020 [NTNU Gjøvik and SINTEF Manufacturing]"
__credits__ = ["Mats Larsen", "Aadne Solhaug Linnerud", "Olga Ogorodnyk"]
__license__ = "MIT"
__maintainer__ = "Mats Larsen"
__email__ = "Mats.Larsen@sintef.no"
__status__ = "Development"
__date__ = "30032020"
__version__ = "1.0"
#--------------------------------------------------------------------
#IMPORT
#--------------------------------------------------------------------
import socket
import xml.etree.ElementTree as ET
import time
import threading
import datetime
import copy
#--------------------------------------------------------------------
#CONSTANTS
#--------------------------------------------------------------------
# URI for date and time
URI_DATE = 'cc300://imm/cm#//c.PDP/p.sv_dPDPDate/v'
URI_TIME = 'cc300://imm/cm#//c.PDP/p.sv_dPDPTime/v'
#--------------------------------------------------------------------
# CLASSES
#--------------------------------------------------------------------
class EMI_Interface():
    '''
    Class for interaction with IMM(C300) over Engel Machin Interface (EMI)
    '''
    def __init__(self,**kwargs):
        '''
        Instantiate EMI with params.
        Params:
        - name              -> str              : Name of the instance
        - ip                -> str              : IP of the engel machine
        - port              -> int              : Port to the engel machine
        - username          -> str              : Login for user
        - passw             -> str              : Password to the username
        - debug             -> Boolean          : Debug value
        '''
        #Arguments
        self.__kwargs = kwargs
        self.__name = kwargs.get('name','imm')
        self.__ip = kwargs.get('ip',None)
        self.__port = kwargs.get('port',None)
        self.__username = kwargs.get('username',None)
        self.__passw = kwargs.get('passw',None)
        self.__debug = kwargs.get('debug',False)

        if self.__debug:
            print('{} created with these params: ip: {},port: {}, debug: {}'.format(__class__,self.__ip,self.__port,self.__debug))

        # Attributes
        self.__endtag = bytes.fromhex('19')         # Endtag
        self.__my_client_id = '1'                   # client id
        self.__host_error_odd = 'enHostErrorOff'    # Setting
        self.__isoabs = 'iso_abs'                   # Setting
        # Connection ref
        self.__c = None
        #Event for socket lock. Only one can send data
        self.__socket_event = threading.Lock()

    def close(self):
        '''
        Close the connection to the machine
        '''
        self.__socket_event.acquire()
        self.__c.close()
        self.__c = None
        self.__socket_event.release()

    def connect(self):
        '''
        Establish connection to the machine over socket.
        Params:
        Return:
        - err -> Bool : True for valid connection otherwise false
        '''
        err = True
        if self.__debug: print('Trying to etablish connection to {}:{}'.format(self.__ip,self.__port))
        try:
            self.__c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__c.connect((self.__ip, self.__port))
            if self.__debug: print('Etablish connection to {}:{}'.format(self.__ip,self.__port))
        except:
            print('Etablish connection to {}:{} failed !!'.format(self.__ip,self.__port))
            self.__c = None
            err = False

        return err

    def info_log(self):
        '''
        Request for the infolog and write it to file
        Params:
        Return:
        - r ->
        '''
        if self.__debug: print('Perform info')
        root = ET.Element("getMessagesRequest")
        root.set('language','en')
        root.set('minMessageIndex','0')

        self.__send_string(ET.tostring(root))
        r = self.__recv_string()
        return r

    def login(self):
        '''
        Login to the machine
        Params:
        Return:
        '''
        # Create the login request
        root = ET.Element("loginRequest")
        root.set('username',self.__username)
        root.set('password',self.__passw)

        login = False
        # Continue until login success
        if self.__debug: print('Trying to login')
        while not login:
        # Send the login request
            self.__send_string(ET.tostring(root))
            login =  self.__handle_login()
            time.sleep(1)

        if self.__debug:print('Login Success')

    def __handle_login(self):
        '''
        Handle login, waiting for the machine to response
        Params:
        Return:
        '''
        r = self.__recv_string()
        self.__session_id = r.get('sessionid')
        if self.__session_id is None:
            time.sleep(1)
            self.logout()
            return False
        return True

    def logout(self):
        '''
        Logout  of the machine
        Params:
        Return:
        '''
        if self.__c != None:
            # Create msg
            root = ET.Element("logoutRequest")
            self.__send_string(ET.tostring(root))
            root = self.__recv_string()
            time.sleep(0.1)
            if self.__debug: print('Login Out')
        else:
            print('Connection not establish')


    def set_param_value(self, param_uri, value):
        '''
        Set value to a parameter given in argument
        Params:
        - param_uri -> str :
        - value     -> str :
        Return:
        '''
        # Create the request
        root = ET.Element("setParameterValueRequest")
        root.set('unitSystem',self.__isoabs)
        root.set('uri',param_uri)
        root.set('parameterValue', str(value))

        # Send the request
        self.__send_string(ET.tostring(root))

        # Get the response
        r = self.__recv_string()

    def get_param_value(self,param_uri):
        '''
        Get value to a parameter given in argument
        Params:
        - param_uri
        Return:
        -> Dict : With results
        '''
        if self.__debug:print('Performing get_param_value with these parameters: {}'.format(param_uri))
        # Create request
        root = ET.Element("getParameterValuesRequest")
        root.set('id',self.__my_client_id)
        parameters = ET.SubElement(root, 'parameters')
        param = copy.copy(param_uri)
        if not isinstance(param,list):
            param = [param]

        for i in param:
            parameter = ET.SubElement(parameters, 'parameter')
            parameter.set('uri',i)

        # Send reqeust
        s = datetime.datetime.now()
        self.__send_string(ET.tostring(root))
        # recv response
        p = self.__handle_get_param_value(s)
        if p is None:
            e = {}
            e['timestamp_{}'.format(self.__name)] = None
            for i in param:
                e[i] = None
            return e
        return p


    def get_param_details(self,param_uri):
        '''
        Request of detailed parameter properties.
        Params:
        - param_uri -> [str] or str :
        Return:
        '''
        # Create request
        root = ET.Element("getParameterDetailsRequest")
        root.set('uri', param_uri)
        # Send reqeust
        self.__send_string(ET.tostring(root))
        return self.__handle_get_param_details()

    def get_parameter_text(self,param_uri):
        '''
        Get description of the parameter
        '''
        root = ET.Element("getParameterPhraseRequest")
        root.set('unitSystem', self.__isoabs)
        root.set('uri', param_uri)
        root.set('language', 'en')
        # Send reqeust
        self.__send_string(ET.tostring(root))
        return self.__handle_get_param_text()

    def get_process_dataset(self,min_r,max_r):
        '''
        Get the process dataset on the machine
        '''
        root = ET.Element("getRecordDataRequest")
        root.set('minRecordNumber', min_r)
        root.set('maxRecordNumber', max_r)
        # Create request
        self.__send_string(ET.tostring(root))
        return self.__handle_process_dataset()

    def __handle_process_dataset(self):
        '''
        Handle the request for process dataset
        '''
        r = self.__recv_string()
        return r

    def __handle_get_param_text(self):
        '''
        '''
        r = self.__recv_string()
        return ET.tostring(r)

    def __handle_get_param_details(self):
        '''
        Handler of the method get_param_details
        '''
        r = self.__recv_string()
        return r.attrib

    def __handle_get_param_value(self,s):
        '''
        Handle the get parameter response
        '''
        # Get recv msg
        r = self.__recv_string()
        e = datetime.datetime.now()
        timestamp = s + (e-s)/2.0
        t= timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        if r is None: return None
        values = {}

        try:
            # find parameters
            param = r.findall('./parameters/parameter')
            for i in param:
                values[i.get('uri')] = i.get('parameterValue')
            values['timestamp_{}'.format(self.__name)] = t

            #del values[URI_DATE]
            #del values[URI_TIME]
        except:
            print('No known parameters returned')
            return ""
        return values

    def __send_string(self,string):
        '''
        Send a request to machine in format str.
        Params:
        - string -> str : The request we want to send
        Return:
        '''
        #Wait till the socket is free
        self.__socket_event.acquire()
        # Add the endtag to the request
        msg = string + self.__endtag

        if self.__debug: print('Msg send to the machine : {}'.format(msg))
        # Send the request
        self.__c.send(msg)

    def __recv_string(self):
        '''
        Return the response from the machine.
        Params:
        Return:
        '''
        r = b""
        # Wait the endtag is present
        while not r.endswith(self.__endtag):
            r += self.__c.recv(1024)

        # Decode reponse to tree.xml
        r = r[:-1].decode("UTF-8")
        r = "<" + r.split("<", 1)[-1]
        if self.__debug: print('Recv msg from the machine : {}'.format(r))

        # Ensure a new thread can take the socket
        self.__socket_event.release()

        if r is None: return None
        try:
            root = ET.fromstring(r)
            return root
        except:
            print('error',r )

    def __get_datetime(self,d,t):
        '''
        Transfrom values to datetime
        '''
        date = d.split('T')[0] + ' ' + t.split('T')[1]
        return date
