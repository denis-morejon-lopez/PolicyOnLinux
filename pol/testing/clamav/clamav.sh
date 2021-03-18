#!/bin/bash

# Instalar el clamav
apt-get install -y clamtk clamav

# configurarle el repositorio
sed -i -e 's/DatabaseMirror.*/DatabaseMirror 192.168.91.59/'  /etc/clamav/freshclam.conf

# Programar la actualizacion para el arranque de la PC
sed -i -e 's/.*exit 0/freshclam -d -c 2 ; exit 0/'   /etc/rc.local


