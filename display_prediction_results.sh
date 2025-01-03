#!/bin/bash
export PATH=$PATH:$HOME/.local/bin

PIDS=$(ps -eaf)
PID=$(echo "$PIDS" | grep "display_prediction_results.py" | awk '{print $2}')

if [[ -z "$PID" ]];
 then(
        echo "display_prediction_results.py is not running, Starting a new one";
)else(
        echo "display_prediction_results.py was running with $PID, Restarting a new one";
        kill -9 $PID
)fi
cd  Teams_scrapper/
source env/bin/activate
pip3 install -r requirements.txt
python3 display_prediction_results.py