#!/bin/sh


USER=$(who | tail -1 | gawk '{ print $1 }');

rm /home/$USER/Escritorio/Compartidas
rm /home/$USER/Desktop/Compartidas

find /home/ -type f -name logins.json -exec rm {} \;

