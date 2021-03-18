#!/bin/bash
prueba="1"
while [ $prueba == "1" ]; do
usuario=`awk -F"," '{line = $0} END { print $NF }' /var/log/pol.log`
#usuario=0
echo $usuario
find /home/$usuario -user root -not -path "/home/$usuario/servidores/*" -exec chown $usuario {} \;
sleep 10
done
