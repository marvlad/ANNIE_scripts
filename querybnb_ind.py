#####################################################################################################################################
## Simple script to query the IFBeam databse 
## inspored by: https://cdcvs.fnal.gov/redmine/projects/ifbeamdata/wiki/DataAccessSyntax
##
## mailto: ascarpell@bnl.gov
#####################################################################################################################################

# Sliglty modify my M. Ascencio

import urllib.request, sys
from datetime import datetime, tzinfo, timedelta
import time
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import sys

def composeURL( event, device, t0, t1 ):
    baseURL = "https://dbdata1vm.fnal.gov:9443/ifbeam/data/data?v=%s&e=e,%s&t0=%s&t1=%s&f=csv" % (device, event, t0, t1)
    
    #print("This is the base url for the request to the database: you can paste and copy it into your browser for confirmation of the successful request")
    #print(baseURL)

    return baseURL

def queryBeamByDevice( event, device, t0, t1 ):

    url = composeURL( event, device, t0, t1 )
    
    f = urllib.request.urlopen(url)

    timestamp = []
    device = []

    for i,line in enumerate(f):
        
        if i==0: continue
    
        line = ( line.strip() ).decode('utf-8')
        buff = line.split(",")
    
        timestamp.append( buff[3] )
        device.append( float(buff[5]) )
        
    
    return timestamp, device

def gettime(ts):
    dt_object = datetime.fromtimestamp(int(ts)/1000.0)
    return dt_object.strftime('%Y-%m-%d\n%H:%M') 


####################################################################################################

def main(argv):
    time1 = str(sys.argv[1])
    time2 = str(sys.argv[2])

    mv1 = datetime.strptime(time1, "%Y-%m-%d %H:%M:%S.%f")
    mv2 = datetime.strptime(time2, "%Y-%m-%d %H:%M:%S.%f")

    t0 = int(mv1.timestamp())
    t1 = int(mv2.timestamp())

    ts_bnb, pot_bnb = queryBeamByDevice( "1d", "E:TOR875", t0, t1 )
    print( "BNB: Total POT collected in the time interval selected: %.2f" % np.sum(pot_bnb) )

if __name__=='__main__':
    main(sys.argv[2:])
