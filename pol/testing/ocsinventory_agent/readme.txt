### Ejemplo ###
## En la PC muestra
# apt-get install debconf-utils (Si no esta instalado aun)
# apt-get install paquete
# debconf-get-selections |grep paquete > paquete.answers

## Se trae el fichero resultante para el sistema pol,
# y se ubica en la politica que instalara el paquete
# Luego se copia para la PC cliente el fichero en 
# cuestion (paquete.answers) y se ejecuta:

#debconf-set-selections paquete.answers
#apt-get install paquete

