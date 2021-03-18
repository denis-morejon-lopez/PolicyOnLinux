#!/bin/bash
GATEWAY="$(route -n | awk '/^0.0.0.0/ {print $2}')"
MAC="70:7b:e8:c5:bb:fe"

case  "$GATEWAY" in
  192.168.104.113)
  echo Router de Lajas
  ;;
  192.168.104.129)
  echo Router de Rodas
  ;;
  192.168.104.145)
  echo Router de Abreus
  ;;
  *)
  # Set static arp entry
  arp -s $GATEWAY $MAC
  #echo arp -s $GATEWAY $MAC
esac
