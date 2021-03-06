#!/usr/bin/python
# -*- coding: utf_8 -*-  


#================Plantilla fija para cada nueva politica================
import sys,os

policyPath = os.path.join(os.path.dirname(__file__) , '..')
sys.path.append(policyPath)
localFiles  = os.path.join(os.path.dirname(__file__) , 'local-files')
from lib.utilities import *  ;  f = Files()


#====================================Main===================================
from datetime import datetime
from time import strptime

cronfile = '/etc/crontab'
regexp   = "apt-get.*update"
newline  =  "#1    9,12,15  *  *   1   root     apt-get update ; apt-get -y upgrade"

if f.existLinesInFile(cronfile,regexp,'#'):
    f.replaceLinesInFile(cronfile,regexp,newline,'#')
else:
    f.lineToFile(cronfile,newline)

#os.system("/etc/init.d/cron reload")
os.system("service cron reload")
