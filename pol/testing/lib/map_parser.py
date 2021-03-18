import string,re,os,sys,copy
from datetime import datetime,timedelta
from time import strptime,strftime
from messages import *
from utilities import *
file = Files()


#==================Funciones accesorias==============
        
def validLine(line=''):
    """Quitar lineas invalidas
    #validLine(str) --> 
    #True si se trata de una linea valida de configuracion
    #False si no lo es: como los comentarios"""
    line = string.strip(line)
    invalid = ('#' in line) or (line == '\n') or (line == '')
    return not invalid

def joinElements( parts = [] ):
    """joinElements recibe una lista y se encarga de devolver otra lista
    donde une los elementos aislados que se encierran por comillas dobles. 
    Ej:
    ['MiNombre','"De','nis"','Morejon']  -->  ['MiNombre','Denis','Morejon']"""
    newParts = []
    frase = ''
    flag = False
    NoDeComillas = 0
    for part in parts:
        NoDeComillas = string.count(part,'"')
        if  NoDeComillas == 0:
            if flag:  # Palabras intermedias y aisladas de la frase entre comillas
                frase = frase + ' ' + part
            else:     # Palabras aisladas fuera de las comillas   
                newParts.append(part)
        elif NoDeComillas == 1: # Cierre o apertura de una frase entre comillas
            if not flag:  # Apertura de frase
                flag = True
                frase = string.replace(part,'"','')
            else:  # Cierre de frase
                part = string.replace(part,'"','')
                frase = frase + ' ' + part
                newParts.append(frase) # Guardar la frase
                frase = ''
                flag = False
                NoDeComillas = 0
        elif NoDeComillas == 2:
            part = string.replace(part,'"','')
            newParts.append(part)
        else:
            print "Demasiadas comillas en la linea que contiene la frase: ",part
            sys.exit()
    if flag:
        print "Existe una comilla sin cerrar en el fichero map.cfg" 
        sys.exit()
    return newParts

class Template():
    """T = Template(templateFile,templateContent,HOME='')
    T.parsed  -->  Contenido de la plantilla ya parseado"""
    def __init__(self,templateFile,templateContent,HOME=''):
        variables = self.getVariables(templateFile)
        if '%(HOME)s' in templateContent:
            variables.update( {'HOME':HOME} )
        self.parsed    = self.parseTemplate(templateContent,variables)
        
    def getVariables(self,templateFile):
        parser = templateFile + ".parser"
        parserOutFile = "/tmp/parser.out"
        dicVariables = {}
        command1 = "%s > %s" % (parser,parserOutFile)
        try:
            os.system(command1)
        except:
            print "No se pudo ejecutar el parser: %s " % parser
            return False
        lines = file.linesFromFile(parserOutFile)
        file.removeFile(parserOutFile)
        for line in lines:
            line = string.strip(line)
            if not "===" in line:
                print "El parser %s esta imprimiendo resultados sin separador '===' "
                return False
            else:
                parts = line.split('===')
                variable = parts[0]
                value = parts[1]
                dicVariables.update( {variable:value} )
        return dicVariables
    
    def parseTemplate(self,templateString,dicVariables):
        """parseTemplate(templateString,dicVariables) Recibe una cadena plantilla
        que debe ser interpretada y un diccionario de variables, para devolver 
        la cadena ya interpretada. Los simbolos a interpretar en el fichero son %(VARIABLE)s
        Se sustituye cada VARIABLE en la plantilla por sus valores correspondientes
        en dicVariables"""
        stringParsed = templateString % dicVariables
        return stringParsed

#==================Fin de funciones accesorias===================

#============Definicion y jerarquia de objetos===============

# Los objetos son:
# Policy, Targetdn, Version, Operation.

class GenericObject:
    """GenericObject representa objetos genericos en el fichero map.cfg"""       
    namePattern = ''
    values = []
    fatherClass = ''
    fatherObj = ''
        
class Policy(GenericObject):
    namePattern = "^\[.*\]$"
    fatherClass = ''
    minFrequency = ['0', 'm']
    def compareFrequency(self):
        policyStampFile = "/var/log/policy-timestamp"
        regexp = policyName = self.values[0]
        MD = ManageDate()
        newTimeStamp = MD.setTimeStamp()
        newLine = "%s %s" % (policyName,newTimeStamp)
        minFrequencyNumber = string.atoi(self.minFrequency[0])
        minFrequencyUnit  = self.minFrequency[1]
        result = True
        if file.existFile(policyStampFile):
            lines = file.linesFromFile(policyStampFile)
            lastTimeStamp = ''
            for line in lines:
                parts = line.split()
                if parts[0] == policyName:
                    lastTimeStamp = parts[1]
            if lastTimeStamp:
                # Sumarle al lastTimeStamp la minFrequency y comparar resultado con la hora actual
                if minFrequencyUnit == 'd':   #day
                    result = MD.isTimeOver(lastTimeStamp,days=minFrequencyNumber,hours=0,minutes=0)
                elif minFrequencyUnit == 'h': #hour
                    result = MD.isTimeOver(lastTimeStamp,days=0,hours=minFrequencyNumber,minutes=0)
                elif minFrequencyUnit == 'm': #minute
                    result = MD.isTimeOver(lastTimeStamp,days=0,hours=0,minutes=minFrequencyNumber)
                else:
                    print "Existe un valor de minfrequency en el fichero map.cfg que no es: 'd', 'h', 'm'"
                    sys.exit()
                if result:
                    file.replaceLinesInFile(filepath=policyStampFile,regexp=policyName,newline=newLine)
            else:
                print "No aparece %s en el fichero %s" % (policyName,policyStampFile)
                # Agregar la politica a este fichero
                file.lineToFile(policyStampFile,newline=newLine)
        else:
            # Crear el fichero, agregando la politica en curso
            print "Creando el fichero %s ..." % policyStampFile
            file.lineToFile(policyStampFile,newline=newLine)
        return result
    
class Targetdn(GenericObject):
    namePattern = "targetdn"
    fatherClass = Policy
    activationDate = []
    def isActivated(self):
        return ManageDate().isActivated(self)
        
    
class Version(GenericObject):
    namePattern = "version"
    fatherClass = Targetdn
    def find(self):
        """find() se utiliza para saber si las expresiones regulares contenidas en 
        el atributo 'values' de esta clase, presentan coincidencias en la linea
        del fichero /etc/issue. La linea de este fichero en cada PC describe
        la distribucion y version de GNU/Linux que se utiliza.
        Esta funcion devuelve la cadena (o coincidencia) mas larga encontrada
        Pero devuelve una cadena vacia si no aparecen coincidencias."""
        
        versionFile = '/etc/issue'
        try:
            content = file.readTextFile(versionFile)
        except IOError,e:
                print e
                sys.exit()
        longestSubString = ''
        for regExp in self.values:
            compiledExp = re.compile(regExp)
            foundList = compiledExp.findall(content)
            if foundList:
                for subString in foundList:
                    if len(subString) > len(longestSubString):
                        longestSubString = subString
        verSubString = longestSubString
        return verSubString
        
    def others(self):
        result = False
        if len(self.values) == 1 and self.values[0] == 'others':
            result = True
        return result
            
class Operation(GenericObject):
    namePattern = "operation"
    fatherClass = Version
    srcFiles = []
    dstFiles = []
    copyType = []
    scripts  = []
    def play(self,localFiles):
        if 'copy' in self.values:
            self.__copy(localFiles)
        if 'execute' in self.values:
            self.__execute(localFiles)
        if 'none' in self.values:
            self.__none()
            
    def __copy(self,localFiles):
        print "Ejecutando operacion 'copy' de:%s   a:%s" %(self.srcFiles,self.dstFiles)
        if len(self.srcFiles) == len(self.dstFiles):
            for srcF,dstF in zip(self.srcFiles,self.dstFiles):
                srcF = os.path.join(localFiles,srcF)
                # Leer:    
                try:
                    content = file.readTextFile(srcF)  
                except IOError,e:
                    print e
                    sys.exit()
                # Si se trata de una plantilla
                if [ copyType for copyType in self.copyType if copyType == 'template' ] :
                    isTemplate = True
                else:
                    isTemplate = False
                
                # Escribir:
                if '%(HOME)s' in dstF:
                    homeDirectories = [ userObj.home for userObj in getUsers() ]
                    logins = [ userObj.login for userObj in getUsers() ]
                    for home,login in zip(homeDirectories,logins):
                        # Procesar el contenido si se trata de una plantilla
                        if isTemplate:
                            T = Template(templateFile=srcF,templateContent=content,HOME=home)
                            content = T.parsed
                        dstPath = dstF.replace('%(HOME)s',home)
                        
                        if file.existFile(dstF):
                            needChangeOwner = False
                        else:
                            needChangeOwner = True
                            
                        try:
                            file.textToFile(content,dstPath)
                            if needChangeOwner:
                                command = "chown %s %s" % (login,dstPath)
                                os.system(command)
                            if [ copyType for copyType in self.copyType if copyType == 'executable' ] :
                                command = "chmod a+x %s" % dstPath
                                os.system(command)
                        except IOError,e:
                            print e
                            if [ copyType for copyType in self.copyType if copyType == 'optional' ] :
                                pass
                            else:
                                sys.exit()
                else:
                    if isTemplate:
                        T = Template(templateFile=srcF,templateContent=content)
                        content = T.parsed 
                    try:
                        file.textToFile(content,dstF)
                        if [ copyType for copyType in self.copyType if copyType == 'executable' ] :
                            #command = "chmod a+x %s" % dstPath
                            command = "chmod a+x %s" % dstF
                            os.system(command)

                    except IOError,e:
                        print e
                        if [ copyType for copyType in self.copyType if copyType == 'optional' ] :
                            pass
                        else:
                            sys.exit()
        else:
            print 'No existe la misma cantidad de ficheros origenes que de ficheros destinos en map.cfg:'
            print 'srcfiles: ',self.srcFiles
            print 'dstfiles: ',self.dstFiles
            sys.exit()
            
    def __execute(self,localFiles=''):
        print "Ejecutando operacion 'execute' de: %s" % self.scripts
        for script in self.scripts:
            scriptDir  = os.path.join(localFiles,'../')
            scriptFile = os.path.join(scriptDir,script)
            os.system(scriptFile)
            
    def __none(self):
        pass

class Map:
    """La clase Map tiene metodos para manipular la informacion
    de configuracion almacenada en un fichero tipo map.cfg"""
    def __init__(self, localFiles='', mapFile='map.cfg' ):
        mapFile=file.globalFile(mapFile)  
        self.objects  = self.__buildObjects(mapFile)
        self.localFiles = localFiles 
    
    def executePolicy(self,policyName,pcdn):
        """executePolicy(policyName,pcdn) --> Ejecuta la politica indicada
	    segun el tipo de operacion de cada entrada"""
        #=============Tratamiento de objetos tipo Policy============
        longestValue = ''
        targetdnMatched = ''
        policyMatched = ''
        isPolicyInFrequency = False
        for policy in self.objects[Policy]:
            if policy.values[0] == policyName:
                policyMatched = policy
                isPolicyInFrequency = policy.compareFrequency()
                if isPolicyInFrequency:
                    
                    #==========Tratamiento de objetos tipo Targetdn===========
                    for targetdn in self.objects[Targetdn]:
                        if (targetdn.fatherObj is policyMatched)  and (targetdn.isActivated() ) :
                            for value in targetdn.values:
                                if (value.lower() in pcdn.lower()) and (len(value) > len(longestValue)):
                                    longestValue = value
                                    targetdnMatched = targetdn
                    if targetdnMatched:
                        #==========Tratamiento de objetos tipo Version=========
                        longestVersionStringMatched = ''
                        versionMatched = ''
                        versionOther = ''
                        for version in self.objects[Version]:
                            if version.fatherObj is targetdnMatched:
                                if version.others():
                                    versionOther = version
                                else:
                                    versionStringMatched = version.find()
                                    if len(versionStringMatched) > len(longestVersionStringMatched):
                                        longestVersionStringMatched = versionStringMatched
                                        versionMatched = version
                        if versionMatched:
                            #===========Tratamiento de objetos tipo Operation=========
                            for operation in self.objects[Operation]:
                                if operation.fatherObj is versionMatched:
                                    operation.play(self.localFiles)
                        elif versionOther:
                            for operation in self.objects[Operation]:
                                if operation.fatherObj is versionOther:
                                    operation.play(self.localFiles)
                        else:
                            print "Falta un objeto 'version' abajo de '%s' en el fichero 'map.cfg' " % longestValue
                            print "o no estan bien escritas las expresiones regulares asociadas a 'version' "
                            sys.exit()
                    else:
                        print 'La politica %s no tiene entradas para la PC o expiraron' % policyName
        if not policyMatched:
            print "La politica '%s' no se encuentra configurada en el fichero map.cfg" % policyName
        if not isPolicyInFrequency:
            print "No ha transcurrido el tiempo necesario para ejecutar nuevamente la politica '%s' " % policyName
       
    def __buildObjects(self, mapFile):
        """Construye objetos que se almacenaran por listas de las distintas clases definidas,
        organizadas mediante un diccionario cuyas llaves son el patron que identifica al objeto
        dentro del texto del fichero map.cfg.
        Estructura:
        objects = {Policy:[] , Targetdn:[] , Version:[] , Operation:[]}"""

        objects = {Policy:[] , Targetdn:[] , Version:[] , Operation:[]}

        # ====  Sacar lineas del fichero map.cfg====
        lines = file.linesFromFile(mapFile)
        #===========Dejar las lineas validas=============
        lines = [string.strip(line) for line in lines if validLine(line) ]

        #=====Armar la estructura como instancias de los objetos definidos=====
        for line in lines:
            parts = line.split()
            # Funcion para unir las partes de una linea que se encierran con comillas dobles y quitar dichas comillas
            parts = joinElements( parts )
            lineName = parts[0]
            if len(parts) > 1: 
                lineValues = parts[1:]
            else:
                lineValues = 'None'
            isObject = False    
            for cla in objects.keys():
                namePatternCompiled = re.compile(cla.namePattern)
                if namePatternCompiled.search(line):
                    currentClass = cla
                    currentObj = currentClass()
                    isObject = True
                
            if isObject: # Si la linea es el comienzo de un objeto definido
        
                if currentObj.namePattern == Policy.namePattern:  #Cuando la linea es un objeto tipo Policy
                    # Para el caso de las politicas el valor 'nameValues' del objeto se refiere
                    # al texto que esta entre corchetes.
                    currentObj.values = [lineName.lstrip('[').rstrip(']')]  
              
                else: # Cuando se trata de algun objeto definido distinto de policy
                    if lineValues: 
                        # Para los otros objetos el valor 'nameValues' son los elementos
                        # separados por espacios que siguen al nombre del objeto, que es el 
                        # 1er elemento de la linea 
                        currentObj.values = lineValues
                        # Identificar y atribuirle su objeto padre
                        currentObj.fatherObj = objects[currentClass.fatherClass][len(objects[currentClass.fatherClass]) - 1]
                    else:
                        print "Una linea del fichero map.cfg necesita al menos un valor como parametro"
                        sys.exit()
                # Almacenado del objeto en cuestion
                objects[currentClass].append(currentObj)     
        
            else: # Si no es un objeto definido, son atributos y valores del ultimo objeto visto  'currentObj'
                if lineName == 'minfrequency':
                    if not (  currentObj.namePattern == "^\[.*\]$" ):
                        print "Existe una linea en el fichero 'map.cfg' con atributo 'minfrequency' a la que no le precede un objeto [policy] "
                        sys.exit()
                    else:
                        currentObj.minFrequency = lineValues    
                
                if lineName == 'srcfiles':
                    if not ( [ value for value in currentObj.values if value == "copy" ] ):
                        print "Existe una linea en el fichero 'map.cfg' con atributo 'srcfiles' a la que no le precede una operacion 'copy' "
                        sys.exit()
                    else:
                        currentObj.srcFiles = lineValues
                if lineName == 'dstfiles':
                    if not ( [ value for value in currentObj.values if value == "copy" ] ):
                        print "Existe una linea en el fichero 'map.cfg' con atributo 'dstfiles' a la que no le precede una operacion 'copy' "
                        sys.exit()
                    else:
                        currentObj.dstFiles = lineValues
                        
                if lineName == 'copytype':
                    if not ( [ value for value in currentObj.values if value == "copy" ] ):
                        print "Existe una linea en el fichero 'map.cfg' con atributo 'copytype' a la que no le precede una operacion 'copy' "
                        sys.exit()
                    else:
                        currentObj.copyType = lineValues    
                
                if lineName == 'scripts':
                    if not ( [ value for value in currentObj.values if value == "execute" ] ):
                        print "Existe una linea en el fichero 'map.cfg' con atributo 'scripts' a la que no le precede una operacion 'execute' "
                        sys.exit()
                    else:
                        currentObj.scripts = lineValues
                           
                if lineName == 'activation-date':
            
                    if not (  currentObj.namePattern == "targetdn" ):
                        print "Existe una linea en el fichero 'map.cfg' con atributo 'activation-date' a la que no le precede un objeto 'targetdn' "
                        sys.exit()
                    else:
                        currentObj.activationDate = lineValues
                                
                # Actualizacion del ultimo objeto visto
                objects[currentClass].pop()
                objects[currentClass].append(currentObj)  
        #============================Fin del recorrido de las lineas===============================
        return objects


#===================Para tratamiento de fechas=====================   
class ManageDate:
    """Clase para manipular fechas"""
    def __init__(self):
        self.TODAY = datetime.today()
        
    def isActivated(self,object):
        """Verifica que el dia actual este en el rango de activacion definido en map.cfg"""
        activated = False
        if not object.activationDate:
            return True
        else:
            for timeStampRange in object.activationDate:
                if self.isInRange(timeStampRange):
                    return True
        return activated
	
    def isInRange(self,timeStampRange):
        """isInRange('2009-04-03-00-00_2009-12-12-00-00') --> True or False"""
        result = False
        if '_' in timeStampRange:
            timeRange = timeStampRange.split('_')
            FROM,TO = [ self.getTimeStamp(timeStamp) for timeStamp in timeRange]
            if FROM < self.TODAY and self.TODAY < TO:
                result = True
        else:
            # Para cuando la marca de tiempo no es un rango sino una fecha y hora
            # se devuelve True si la fecha y hora actual es mayor o igual.
            timeStamp = timeStampRange
            DAY = self.getTimeStamp(timeStamp)
            if DAY <= self.TODAY:
                result = True    
        return result                
    
    def isTimeOver(self,timeStamp,days=0,hours=0,minutes=0):
        delta = timedelta(days=days,hours=hours,minutes=minutes)
        timeObj = self.getTimeStamp(timeStamp)
        newTime = timeObj + delta
        if self.TODAY > newTime: # Si paso el periodo de restriccion
            return True
        else:
            return False
        
    def setTimeStamp(self):
        "setTimeStamp() Devuelve una cadena con la fecha y hora actual con formato: Year-Month-Day-Hour-Minute"
        return strftime("%Y-%m-%d-%H-%M")    
    def getTimeStamp(self,timeStamp):
        "getTimeStamp() Recibe una cadena con una fecha y hora con formato: Year-Month-Day-Hour-Minute"
        "Devuelve un objeto tipo datetime.datetime que se puede comparar con otros de su tipo como: "
        "datetime.datetime.today()"
        DAY = datetime(*strptime(timeStamp, "%Y-%m-%d-%H-%M")[:5])
        return DAY
        
