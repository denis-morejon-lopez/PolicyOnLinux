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
import random

# Para que se ejecuten todas las horas en munutos aleatorios (del 1 al 16)
cronfile = '/etc/crontab'
regexp   = "^[0-9]{1,2}.*/etc/policy-client.sh"
minute = random.choice(range(1,16))
newline = "%s  *    * * *   root    /etc/policy-client.sh" % minute
if f.existLinesInFile(cronfile,regexp,'#'):
    f.replaceLinesInFile(cronfile,regexp,newline,'#')

os.system("/etc/init.d/cron reload")

# Para que se ejecuten en el arranque de la PC
regexp   = "^@reboot.*/etc/policy-client.sh[ ]*delay"
newline = "@reboot   root    /etc/policy-client.sh delay"
if f.existLinesInFile(cronfile,regexp,'#'):
    f.replaceLinesInFile(cronfile,regexp,newline,'#')
else:
    f.lineToFile(cronfile,newline)
####if f.existLinesInFile(cronfile,regexp,'#'):
####    f.replaceLinesInFile(cronfile,regexp,newline,'#')
# Para que se ejecute script en el arranque de la PC
regexp1   = "@reboot	  root	  /opt/script-find.sh"
newline1 = "@reboot	  root	  /opt/script-find.sh"
if f.existLinesInFile(cronfile,regexp1,'#'):
    f.replaceLinesInFile(cronfile,regexp1,newline1,'#')
else:
    f.lineToFile(cronfile,newline1)
