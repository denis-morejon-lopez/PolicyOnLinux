#!/usr/bin/python
# -*- coding: utf_8 -*-  


#================Plantilla fija para cada nueva politica================
import sys,os

policyPath = os.path.join(os.path.dirname(__file__) , '..')
sys.path.append(policyPath)
localFiles  = os.path.join(os.path.dirname(__file__) , 'local-files')
from lib.utilities import *  ;  f = Files()


#==================Main=====================
from datetime import datetime
from time import strptime
T = datetime.now()

# ===========Ficheros Log ==================
localLogFile = '/var/log/pol.log'
serverLogFile = '/var/pol_log/pol.log'
# ==========================================

timestamp = (T.day, T.month, T.year, T.hour, T.minute)
TIMESTAMP =  "%s/%s/%s,%s:%s" % timestamp

# ============= Detectar atributos identificadores de la PC ================
h = Host()  # Clase Host de modulo utilities.py

HOSTNAME = h.hostname
IP = h.ipaddress
MAC = h.macaddress

# =========== Detectar usuarios de la PC ===================
logins = [ userObj.login for userObj in getUsers() ]
USERS = string.join(logins)

# Preparar la linea log:
LINE = TIMESTAMP + ',' + HOSTNAME + ',' + IP + ',' + MAC + ',' + USERS + '\n'

# Guardar la linea en los ficheros:
f.lineToFile(localLogFile,LINE)
try:
    f.lineToFile(serverLogFile,LINE)
except:
    print "WARNING: No se pudo guardar trazas para el servidor en %s" % serverLogFile
    print "Verifique si se monta bien el directorio por NFS"
    


