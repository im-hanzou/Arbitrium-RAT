SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTPATH
screen -S main -d -m bash -c "python main.py"
screen -S initproxy -d -m bash -c "python initProxy.py"
echo "[+] the Arbitrium-Server is running ..."
