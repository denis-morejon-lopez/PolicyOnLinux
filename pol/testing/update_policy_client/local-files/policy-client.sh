#!/bin/bash

##########################################
# Escrito por denis.morejon@etecsa.cu
# Colaboracion de alexey.seisdedo@etecsa.cu
##########################################

########   Variables    ##########


#init_script='init.py'          #Para politicas en produccion
init_script='init_testing.py'   #Para politicas de prueba
policy_port=2049 #NFS

# Recursos remotos:
policy_server1='pol-zentyal.cfg.etecsa.cu' # Nombre del servidor de politicas
policy_server2='pol-zentyal.cfg.etecsa.cu' # El administrador puede tener un servidor de respaldo

remote_pol_directory='/var/pol'
remote_log_directory='/var/pol_log'

# Recursos locales
local_pol_directory='/var/pol'
policy_server_file='/var/policy_server_file'

# Invocar de esta forma:  /etc/policy-client.sh delay
# para demorar 60s en ejecutar
# Esto es para garantizar que se ejecuten las politicas 
# en el inicio de la PC tambien.

argument=$1
if test "$argument" == "delay"; then
  delay=60
  sleep $delay
fi

########   Definiciones     ########

# Policy Storage Server1
log_server1=$policy_server1:$remote_log_directory
policy_storage1=$policy_server1:$remote_pol_directory

# Policy Storage Server2
log_server2=$policy_server2:$remote_log_directory
policy_storage2=$policy_server2:$remote_pol_directory

# ======Desmontar:==========
umount_policy_server()
{
umount $local_pol_directory
rm -Rf $local_pol_directory
echo ""
echo "Directorio remoto para politicas desmontado!"

}

umount_log_server()
{
umount $remote_log_directory
rm -Rf $remote_log_directory
echo "Directorio remoto para logs desmontado!"
echo ""
}

# =======Montar: =========
mount_policy_server()
{
if mount -t nfs -o nolock,vers=3 $policy_storage1 $local_pol_directory
then 
    echo ""
    echo "Directorio remoto para politicas montado!"
    policy_server=$policy_server1
    log_init
    $local_pol_directory/$init_script
    umount_policy_server
    umount_log_server

elif mount -t nfs -o nolock,vers=3 $policy_storage2 $local_pol_directory
then
    echo ""
    echo "Directorio remoto para politicas montado!"
    policy_server=$policy_server2
    log_init
    $local_pol_directory/$init_script
    umount_policy_server
    umount_log_server

else 
    echo "ERROR. No se pudo montar ningun servidor"
    exit
fi
# Guardar la conexion con el servidor en un fichero
echo "$policy_server:$policy_port" > $policy_server_file
}

mount_log_server()
{
if mount -t nfs -o nolock,vers=3 $log_server1 $remote_log_directory || mount -t nfs -o nolock $log_server2 $remote_log_directory
then 
    echo "Directorio remoto para logs montado!"
else 
    echo "WARNING. No se pudo montar el directorio remoto para logs"
fi
}


policy_init()
{
if [ -d $local_pol_directory ]
then mount_policy_server
else mkdir $local_pol_directory
    mount_policy_server
fi
}

log_init()
{
if [ -d $remote_log_directory ]
then mount_log_server
else mkdir $remote_log_directory
    mount_log_server
fi
}
 

#########    Main     ###########

policy_init
exit 0
