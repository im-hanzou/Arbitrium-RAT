#!/bin/bash


SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTPATH


value="{API_FQDN}"
value_IP="{API_FQDN_IP}"


for arg in "$@"
do
    if [ "$arg" == "--help" ] || [ "$arg" == "-h" ]
    then
        echo "Usage: ./setAPI_FQDN.sh DOMAIN_OF_API_HOST_OR_IP"
        exit 0
    fi
done


if [ -e .API_FQDN.conf ]
then
    value=`cat .API_FQDN.conf`
    value_IP=$(getent hosts $value | awk '{gsub(/\n/,"",$1); print $1; exit}')
fi



if [ "$1" == "" ]
then
    echo "No domain was provided. Usage: ./setAPI_FQDN.sh DOMAIN_OF_API_HOST_OR_IP"
else
    echo "$value" > .API_FQDN.conf
    resolvedDNS=$(getent hosts $1 | awk '{gsub(/\n/,"",$1); print $1; exit}')
    grep -rl "$value" . --exclude=*setAPI_FQDN.sh | xargs sed -i "s/$value/$1/g"
    grep -rl "$value_IP" . --exclude=*setAPI_FQDN.sh | xargs sed -i "s/$value_IP/$resolvedDNS/g"
    echo "[!] Done"
fi


