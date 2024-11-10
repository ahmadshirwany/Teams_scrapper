#!/bin/bash
export PATH=$PATH:$HOME/.local/bin

PIDS=$(ps -eaf)
PID=$(echo "$PIDS" | grep "oddsshark_prediction.py" | awk '{print $2}')

if [[ -z "$PID" ]];
 then(
        echo "process_predition_data.py is not running, Starting a new one";
)else(
        echo "process_predition_data.py was running with $PID, Restarting a new one";
        kill -9 $PID
)fi
cd  Teams_scrapper/
source env/bin/activate
pip3 install -r requirements.txt
python3 process_predition_data.py