#!/bin/bash

python3 MRDgetIDandTime.py $1 > ./event.txt; python3 mrd_map.py
