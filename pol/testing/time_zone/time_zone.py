#!/usr/bin/python
# -*- coding: utf_8 -*-  


#================Plantilla fija para cada nueva politica================
import sys,os

policyPath = os.path.join(os.path.dirname(__file__) , '..')
sys.path.append(policyPath)
localFiles  = os.path.join(os.path.dirname(__file__) , 'local-files')
from lib.utilities import *  ;  f = Files()
from datetime import datetime
from time import strptime


#====================================Main===================================


# Variables
zone_text_file = localFiles + '/' + "ZonaEtecsa.txt"
zone_bin_file  = "/usr/share/zoneinfo/America/Havana"
localtime_file = "/etc/localtime"
time_server    = "192.168.80.10"

# Variables Agrupadas
data = (zone_text_file, zone_bin_file, localtime_file, time_server)


# Confeccion de comandos
commands = "zic %s ; cp %s %s ; ntpdate %s " % data

# Ejecucion
execFunction(os.system,commands)

