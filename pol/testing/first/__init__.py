"""Script que captura los identificadores de la PC para aplicar
politicas en dependencia de la ubicacion de dicha PC en un servidor ldap.
Modificado: 7/02/2012"""

import sys,os

cacheFile = '/tmp/.ldap_pc_id'
policyPath = os.path.join(os.path.dirname(__file__) , '..')
sys.path.append(policyPath)
localFiles  = os.path.join(os.path.dirname(__file__) , 'local-files')
from lib.utilities import *   ;  f = Files()
from lib.map_parser import *  ;  map = Map(localFiles)
from time import strptime

# ==========================
configFile = f.globalFile('pol.cfg') # Fichero de configuracion global
connectToLdap = f.getValueInConfigFile(configFile,'connect_to_ldap')
pcdnIfNotConnected = f.getValueInConfigFile(configFile,'base')
unknown_host_action = f.getValueInConfigFile(configFile,'unknown_host_action')

# ============= Detectar atributos identificadores de la PC ================
h = Host()  # Clase Host de modulo utilities.py
print ""
print "HOSTNAME:", h.hostname
print "IP:", h.ipaddress
print "INTERFACE:", h.interface
print "MAC:",h.macaddress
print ""

if h.host_id_type == "ipaddress":
    hostId = h.ipaddress
elif h.host_id_type == "hostname":
    hostId = h.hostname
else:
    print "Valor de 'host_id_type' incorrecto en fichero pol.cfg"
    sys.exit()

# ============= Buscar el identificador de la pc en el ldap ================
if connectToLdap == 'yes' or connectToLdap == 'Yes':
    ld = Ldap() # Clase Ldap de modulo utilities.py
    filter = '%s=%s' % (ld.pc_attr_name , hostId)
    pcdn = ld.search(filter)
else:
    pcdn=pcdnIfNotConnected # base de busqueda

# Accion cuando la PC no esta en el directorio ldap 
# Variable 'unknown_host_action' del fichero: pol.cfg
if pcdn=="none":
    print ""
    print "Esta PC no parece estar registrada en el servidor LDAP."
    if unknown_host_action == 'disconnect': 
        print "Se procede a bloquear la interfaz de red."
        os.system("ifdown %s" % h.interface)
    sys.exit()

#====================================Main===================================
f.removeFile(cacheFile) # Borra el fichero temporal si estaba creado

if pcdn:
    # Si encuentra el identificador de la pc en el servidor ldap:
    # - Crear un fichero temporal para marcar dicha existencia 
    # - Copiar dentro dicho identificador para hacer un mecanismo de cache
    f.lineToFile(cacheFile,pcdn)

else:
    print "La pc no se encuentra en el directorio ldap"

