#!/usr/bin/python
# -*- coding: utf_8 -*-  

"""change_root_passwd.py establece una nueva clave para el
usuario root de cada PC, modificando el fichero /etc/shadow
con una clave ya encriptada MD5."""

#================Plantilla fija para cada nueva politica================
import sys,os

policyPath = os.path.join(os.path.dirname(__file__) , '..')
sys.path.append(policyPath)
localFiles  = os.path.join(os.path.dirname(__file__) , 'local-files')
from lib.utilities import *  ;  f = Files()


#==================Main=====================
shadow_file  = '/etc/shadow'
# Linea con la clave de root encriptada
#newline="root:$6$6eU5EJrW$O6rhg7LF5s5rEgSnp5AN8.bfjrGQq2m3tjQJzcjFFDdfkHPOpv1JXHnaNlyY1uedp/ZPhwL0AW9/QrntvL7VD/:16080:0:99999:7:::"
newline="root:$6$7ofpSvof$b.jH0EMiBg.lCpfEzKQQti5NnitL2KfrRHGBIxzn6bBjLW8MevWXs/2UIkk0ngUHWTTU0TYPiajfsmXlRCTk4/:16148:0:99999:7:::"

#=============Confeccion de comandos==============
regexp = '^root' #Linea que comience con: root
f.replaceLinesInFile(shadow_file,regexp,newline)
    
