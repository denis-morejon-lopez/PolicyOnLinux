
"""__init__.py es el mismo script dentro de cada politica pero se comporta diferente
dependiendo del nombre del directorio que lo contiene, que es en definitiva el
nombre de la politica"""

import sys,os
# La politica se llama como el directorio padre de este script:
policyName = os.path.basename(os.path.abspath(os.path.dirname(__file__))) 
cacheFile = '/tmp/.ldap_pc_id'
policyPath = os.path.join(os.path.dirname(__file__) , '..')
sys.path.append(policyPath)
localFiles  = os.path.join(os.path.dirname(__file__) , 'local-files')
from lib.utilities import *   ;  f = Files()
from lib.map_parser import *  ;  map = Map(localFiles)
from time import strptime

#==Buscar el identificador de la pc en la cache ======

pcdn = False
if f.existFile(cacheFile):
    pcdn = f.readTextFile(cacheFile)

if pcdn:
    # Si encuentra el identificador de la pc en la cache:
    map.executePolicy(policyName,pcdn)   # *****
    # Cada politica debe estar representada en el fichero 'global-files/map.cfg'

else:
    # Accion a realizar si la pc no esta en el ldap
    pass

