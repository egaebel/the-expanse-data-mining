#!/bin/bash

cd /home/egaebel/workspace/Programs/the-expanse-tensorflow/src
source ../bin/activate
python expanse_aylien.py | tee -a output.txt
deactivate
