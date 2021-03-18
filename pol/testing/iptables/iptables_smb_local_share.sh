#!/bin/sh

# Borrar reglas de filtrado existentes
iptables -t filter  -F

# Politicas de filtrado por defecto
iptables -t filter --policy FORWARD DROP
iptables -t filter --policy INPUT   DROP
iptables -t filter --policy OUTPUT  ACCEPT

# ----Reglas------

# Aceptar todo paquete de entrada que constituya una respuesta 
# a una solicitud proveniente de la misma máquina
iptables -A INPUT   -m state --state ESTABLISHED,RELATED -j ACCEPT
#iptables -A INPUT -p tcp ! --syn  -j ACCEPT

# Aceptar solicitudes externas de ping
iptables -A INPUT  -p icmp --icmp-type echo-request   -j ACCEPT

# Servicio ssh
iptables -A INPUT -p tcp --dport 22   -j ACCEPT
# Servicio rpc
iptables -A INPUT -p tcp --dport 111  -j ACCEPT
# Servicios de impresion
iptables -A INPUT -p tcp --dport 515  -j ACCEPT
iptables -A INPUT -p tcp --dport 631  -j ACCEPT
# Servicio de asistencia remota
iptables -A INPUT -p tcp --source localhost  --dport 5900 -j ACCEPT
# Para acceso local a maquina virtual
iptables -A INPUT -s 127.0.0.1/32 -p tcp -m tcp --dport 3389 -j ACCEPT
##iptables -A INPUT -s 127.0.0.1/32 -p tcp -m tcp --dport 445 -j ACCEPT

# Para acceso remoto a smb local
iptables -A INPUT -p tcp --dport 445  -j ACCEPT
