# -*- coding: utf_8 -*-
"""utilities.py  Funciones y clases comunes para que sean utilizadas
por las distintas politicas.

Modificado: 8/02/2012 
"""

import os,re,shutil,sys,string,socket

######################################
debug_mode  = False   # True  o  False
mount_point = "/var/pol"
######################################

#=========Decorador para trabajar el modo debug=========
def debug(func):
    """Decorador para hacer que las funciones que modifiquen algo en el sistema
    no se ejecuten si debug_mode = True
    Como utilizarlo?
    Solo debe utilizarse en las funciones del modulo utilities, no en las
    politicas que se programen.
    Ubicar la linea: @debug  antes de la funcion"""
    def decorated_func(*args,**kwds):
        if debug_mode:
            try:
                name = func.func_name
            except:
                name = func.__name__	
            print "="*50
            print "Ejecuta la funcion: ", name
            print "Con los parametros: ", args
            print "y los parametros:   ", kwds
            print "="*50
        else:
            func(*args,**kwds)
    return decorated_func
 

   
@debug
def execFunction(func,*args,**kwds):
    """Ejecuta la funcion que se referencia en el primer
    parametro, con los parametros que siguen.
    El que programe politicas debiera utilizar esta funcion
    en lugar de utilizar directamente alguna de python, porque
    esta ya esta preparada con el decorador @debug para no ejecutar
    accion sobre el sistema cuando estemos en modo debug"""
    return func(*args,**kwds)
 

   
#===================Para tratamientos especificos de ficheros================
class Files:
    """Para manipulacion de ficheros de manera general. Contiene una
    seccion de funciones basicas, y otra de funciones de alto nivel
    para manipular ficheros que no estan incluidas en el 
    modulo shutil de python."""
    
    #################Funciones Basicas:#####################
    ###############(Trate de utilizar las complejas)########
    
    def existFile(self,filepath):
        """existFile(CaminoCompleto)
        Si existe el fichero devuelve --> True.
        Sino devuelve --> False"""
        return os.path.exists(filepath)    

    def removeFile(self,filepath):
        """removeFile(CaminoCompleto) --> Borra un fichero si existe"""
        if self.existFile(filepath):
            os.remove(filepath)
          
    def globalFile(self,filename):
        """globalFile(nombre_fichero) --> Camino completo hasta el fichero
        que esta dentro del directorio global-files/"""
        filepath = os.path.join(os.path.dirname(__file__) , '../global-files/' + filename ) 
        if self.existFile(filepath):
            return filepath
        else:
            sys.exit('Fichero inexistente: %s'%filepath)
    
    def linesFromFile(self,filepath):
        """linesFromFile(CaminoCompleto) --> lista de lineas"""
        if self.existFile(filepath):
            f = open(filepath,'r')
            lines = f.readlines()
            f.close()
            return lines
        else:
            sys.exit('Fichero inexistente: %s'%filepath)
    
    @debug
    def linesToFile(self,lines,filepath):
        """linesToFile(ListaDeLineas,CaminoCompleto) --> Escribe en
        el fichero: CaminoCompleto"""
        f = open(filepath,'w')
        f.writelines(lines)
        f.close()
                    
    @debug
    def lineToFile(self,filepath,newline=''): 
        """lineToFile(CaminoCompleto,newline='')
        Anexa una linea al final del fichero"""
        #Validar que exista un cambio de linea en la nueva linea:
        if not ('\n' in newline) and (newline != '') :
            newline += '\n'
        f = open(filepath,'a')
        f.write(newline)
        f.close()
        
    def textToFile(self,content,filepath):
        """textToFile(filepath) --> Sobre escribe todo un fichero
        con la cadena que entra en content"""
        f = open(filepath,'w')
        f.write(content)
        f.close()
        
            
    def replaceLines(self,lines,regexp,newline='',comment='#'):
        """replaceLines(ListaDeLineas,ExpresionRegular,LineaDeReemplazo,CaracterComentario)
        --> Devuelve nueva estructura lines con los reemplazos efectuados
        Si no se proporciona LineaDeReemplazo simplemente se elimina
        la linea donde se encuentra la expresion regular o cadena.
        Si introduce un caracter de comentario (como '#'), se ignoraran
        las lineas que comiencen con dicho caracter""" 
        
        #Validar que exista un cambio de linea en la nueva linea:
        if not ('\n' in newline) and (newline != '') :
            newline += '\n'
        #Compilar la expresion regular o patron:
        pattern = re.compile(regexp)
        #patron cuando una cadena comience con comment:
        if comment:
            CommentPattern = re.compile('^' + comment) 
        #Lista de lineas que sera devuelta:
        UpdatedLines = []
        
        for L in lines:
            #No Coincidencia o existencia de comentario:
            if not pattern.search(L) or ( comment and CommentPattern.search(L) ): 
                UpdatedLines.append(L)
            #Coincidencia sin comentario (si esta activo el comentario):
            else:                     
                UpdatedLines.append(newline)
                
        return UpdatedLines
    
    
    def removeLines(self,lines,regexp,comment='#'):
        """Es un caso particular de replaceLines() sin el parametro:
        newline.
        Si la linea coincidente esta comentariada y se pasa como parametro
        el caracter de comentario (como '#'), no se borra.  """
        return self.replaceLines(lines,regexp)    
    
    def existLines(self,lines,regexp,comment='#'):
        """existLines(lines,regexp,comment='#')
        Devuelve la ultima linea que existe con la expresion regular indicada.
        Devuelve False si no aparece la expresion.
        Si introduce un caracter de comentario (como '#') se ignoraran
        las lineas que comiencen con dicho caracter"""
        match = False
        #Compilar la expresion regular o patron:
        pattern = re.compile(regexp)
        #patron cuando una cadena comience con comment:
        if comment:
            CommentPattern = re.compile('^' + comment) 
            
        for L in lines:
            if comment and CommentPattern.search(L):
                pass
            elif not pattern.search(L): #No Coincidencia
                pass
            else:                     #Coincidencia
                match = L
    
        return match
    
    def readTextFile(self,filepath):
        """readTextFile(CaminoCompleto)
        Lee un fichero texto en modo lectura y devuelve todo el
        contenido en una cadena"""
        f = open(filepath,'r')
        one_str = f.read()
        f.close()
        return one_str  

    def listFolders(self,folderpath):
        """Devuelve una lista de todos los directorios de un camino """
        todos = os.listdir(folderpath)
        directorios = []
        for item in todos:
            if isdir(join(folderpath,item)): 
                directorios.append(join(folderpath,item))
        return directorios 
    
    #################Funciones Complejas (utilizar preferiblemente):##########
    ################(Basadas en las Funciones Basicas)########################
    
    def replaceLinesInFile(self,filepath,regexp,newline='',comment='#'):    
        """replaceLinesInFile(CaminoCompleto,regexp,newline='',comment='#')
        Primero obtiene las lineas de un fichero con el metodo:
        linesFromFile()
        Luego las modifica usando el metodo:
        replaceLines()
        Finalmente escribe las lineas resultantes en el propio fichero con:
        linesToFile()"""
        newlines = self.replaceLines(  self.linesFromFile(filepath),regexp,newline,comment  )
        self.linesToFile(  newlines,filepath  )
      
    
    def removeLinesInFile(self,filepath,regexp,comment='#'):
        """Es un caso particular de replaceLinesInFile() sin el parametro:
        newline."""
        self.replaceLinesInFile(filepath,regexp,comment='#')
    
     
    def existLinesInFile(self,filepath,regexp,comment='#'):
        """existLinesInFile(CaminoCompleto,regexp,comment='')
        Revisa si existe una expresion regular en las lineas
	    de un fichero. Por defecto no busca en las lineas comentadas"""	
        return self.existLines( self.linesFromFile(filepath) , regexp , comment)

    def getValueInConfigFile(self,filepath,regexp,comment='#'):
        line = self.existLinesInFile(filepath,regexp,comment)
        if line: #Si aparecio una linea con el patron
            lineParts = string.split(line)
            if len(lineParts) == 2: #Si la linea tiene 2 palabras, entonces puede ser del tipo "variable valor"
                variable = lineParts[0]
                value    = lineParts[1]
            else:
                value = False
        else:
            value = False
        return value

#============= Fichero de configuracion global =============
f = Files()
configFile = f.globalFile('pol.cfg')
#===========================================================

class Ldap:
    try:
        import ldap
    except:
        os.system("apt-get install python-ldap --force-yes -y")
        import ldap

    def __init__(self):
        h = Host()
        self.server = f.getValueInConfigFile(configFile,'server')
    	self.base   =f.getValueInConfigFile(configFile,'base')
        self.pc_attr_name   =f.getValueInConfigFile(configFile,'pc_attr_name')
        self.ldapuser   =f.getValueInConfigFile(configFile,'ldapuser')
        self.password   =f.getValueInConfigFile(configFile,'password')
           
    def search(self,filter):
        ldap = self.ldap
        l = ldap.initialize('ldap://%s' % self.server)
        if self.ldapuser:
            if self.password:
                l.set_option(ldap.OPT_REFERRALS, 0)
                l.simple_bind_s(self.ldapuser, self.password)
            else:
                print "No se conecta al servidor LDAP"
                print "Necesita ubicar password en pol.cfg"
        try:
            r = l.search_s(self.base,ldap.SCOPE_SUBTREE,(filter),['%s'%self.pc_attr_name])
        except:
            print "No se conecta al servidor LDAP"
            sys.exit()
        if r:
            dn=repr(r[0][0])
            result = dn
        else:
            result = "none"
        return result
    

class Host:
    """La clase Host posee como atributos identificadores de la PC cliente. """
    def __init__(self):
        # Capturar el server:port del fichero policy_server_file
        policy_server_file = '/var/policy_server_file'
        file = open(policy_server_file)
        server_port = file.read()
        file.close()
        server_port_list = server_port.strip().split(':')
        if len(server_port_list) == 2:
            policy_server = server_port_list[0]
            policy_port   = int( server_port_list[1] )
        else:
            print "No se pudo capturar policy_server:policy_port del fichero %s" % policy_server_file
            return False
        self.ipaddress = self.get_local_ip(policy_server,policy_port)
        self.interface = self.get_interface_from_ip(self.ipaddress)[0]
        self.macaddress = self.get_interface_from_ip(self.ipaddress)[2]
        self.hostname = self.get_hostname()
        self.host_id_type=f.getValueInConfigFile(configFile,'host_id_type')

    def get_local_ip(self,policy_server,policy_port):
        # Procesar nombre servidor para que siempre devuelva IP
        ip_server = socket.gethostbyname(policy_server) # Devuelve IP en una cadena
        # Realizar conexion temporal al servidor
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip_server, policy_port))
        # Obtener la IP local
        ip_loc,port_loc = s.getsockname()
        # Cerrar la conexion
        s.close()
        return ip_loc

    def get_interfaces(self):
        """Devuelve diccionario donde las llaves son
        los nombres de las interfaces y los valores
        son tuplas (interface_ip,interface_mac) """
        interfaces = {}
        command = "ifconfig"
        macregex='[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}'
        macpattern=re.compile(macregex)
        ipregex = "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"
        ippattern = re.compile(ipregex)
        intregex = "^[^\s]+\s" # Solo cuando se esta en la 1ra linea
        intpattern=re.compile(intregex)
        iplineregex = 'inet[^6]'
        iplinepattern=re.compile(iplineregex)
    
        p = os.popen(command)
        lines = p.readlines() #Lista con las lineas del ifconfig
        p.close()

        first_line = True
        for line in lines:
            # Obtener la mac de cada interface
	    # trata de obtener la mac buscando en todas las lineas
            try_interface_mac  = macpattern.findall(line)
            if try_interface_mac:
                interface_mac = try_interface_mac[0]

            if first_line == True: # Primera linea
                # Obtener el nombre de cada interface.
                # Que se encuentra en las primeras lineas
                interface_name = intpattern.findall(line)
                if interface_name:
                    interface_name = interface_name[0]
                    interface_name = interface_name.strip()
                # Fin del procesamiento de la 1ra linea
                first_line = False
            
            elif line!='\n': # Si no es una linea vacia
                # Obtener la direccion ip version 4
                ipline = iplinepattern.findall(line)
                if ipline:
                    # Se trata de la linea que contiene la direccion ip
                    ip = ippattern.findall(line)
                    if ip:
                        # La linea contiene direcciones ip (ip,mask,broadcast)
                        # La primera direccion es la que necesitamos
                        interface_ip = ip[0]
                        
            elif line=='\n': # Cuando se trate de una linea vacia es que existe un cambio de interfaz
                if not 'interface_ip' in locals().keys():
                    interface_ip = ''
                if not 'interface_mac' in locals().keys():
                    interface_mac = ''
                # Almacenar las variables interface_ip e interface_mac de esa interfaz
                interfaces[interface_name] = (interface_ip,interface_mac)

                # Vaciar las variables interface_ip e interface_mac
                interface_ip = interface_mac = ""

                # Declarar comienzo de linea nuevamente
                first_line = True
                   
            else:
                pass
        return interfaces

    def get_interface_from_ip(self,ip_loc):
        """Devuelve una tupla de la forma (interface_name,ip,mac)  
        emplea para ello la funcion get_interfaces()"""
        interfaces = self.get_interfaces()
        for interface_name in interfaces.keys():
            interface_ip  = interfaces[interface_name][0]
            interface_mac = interfaces[interface_name][1]
            if interface_ip == ip_loc:
                return interface_name,interface_ip,interface_mac

    def get_hostname(self):
        """Devuelve la cadena hostname"""
        hostname=""
        domain_name=""
        # Extraer hostname con o sin domain name
        p = os.popen("hostname")
        line = p.readline()
        p.close()
        hostname = line
        # Extraer el domain name solo
        p = os.popen("dnsdomainname")
        line = p.readline()
        p.close()
        if line:
            domain_name = string.strip(line)
        if hostname:
            if domain_name in hostname:
                index = hostname.find(domain_name)
                hostname = hostname[:index-1]
        hostname = hostname.strip()
        return hostname
        
    # Fin de la clase Host



class User():
    """La clase User completa los atributos de un usuario activo:
    home, shell, etc. Su constructor requiere el login del usuario"""
    def __init__(self,login):
        self.login = login
        tmpfile = "/var/tmp/pol.user"
        command = "finger %s |grep Directory > %s" % (login,tmpfile)
        codeResult = os.system(command)
        if codeResult == 256:
	    os.system("apt-get install finger -y --force-yes && %s" % command)
        line = f.linesFromFile(tmpfile)[0]
        elements = line.split()
        lastElement = ''
        directory = '' ; shell = ''
        for element in elements:
            element = element.strip()
            if 'Directory' in lastElement:
                directory = element
            elif 'Shell' in lastElement:
                shell = element
            else:
                pass
            lastElement = element
                
        self.home = directory
        self.shell     = shell
            
            
def getUsers():
    users = []
    tmpfile = "/var/tmp/pol.user"
    command = "users > %s" % tmpfile        
    try:
        os.system(command)
    except:
        print "No se pudo ejecutar el comando %s" % command
        sys.exit()
    line = f.linesFromFile(tmpfile)[0]
    line = string.strip(line)
    logins = set( line.split() )
    for login in logins:
        users.append( User(login) )
    return users        
