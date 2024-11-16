#! /bin/bash
# If on Linux or MacOS - check tmux
if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
    python3 linklogger.py &
    cd app || return
    yarn dev
fi

# If on Windows
if [[ "$OSTYPE" == "msys" ]]; then
    python3 linklogger.py &
    cd app || return
    yarn dev
    # echo -e "This script is not supported on Windows. Please run the API and UI manually."
    # echo -e "\t1. Install node.js, yarn, python3, and pip"
    # echo -e "\t2. Run 'pip install -r requirements.txt' in the root directory"
    # echo -e "\t3. Run 'python3 linklogger.py' in the root directory"
    # echo -e "\t4. Run 'cd app' and then 'yarn dev'"
    # exit 1
fi