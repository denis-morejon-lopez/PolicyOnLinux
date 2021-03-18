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
regexp   = "/etc/cron.daily"
newline = "01 12   * * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )"

if f.existLinesInFile(cronfile,regexp,'#'):
    f.replaceLinesInFile(cronfile,regexp,newline,'#')

os.system("/etc/init.d/cron reload")


