import uproot
import sys
import numpy as np

datafile = "data/annietree.root"

if len(sys.argv) != 2:
    print(f"Usage: python {sys.argv[0]} <event_number>")
    sys.exit(1)

event_num_arg = int(sys.argv[1])

with uproot.open(datafile) as file:
    event_tree = file["Event"]
    mrd_hit_det_id = event_tree["MRDhitDetID"].array()
    mrd_hit_t = event_tree["MRDhitT"].array()
    event_number = event_tree["eventNumber"].array()

    # Find the index of the requested event number
    try:
        idx = list(event_number).index(event_num_arg)
    except ValueError:
        print(f"Event number {event_num_arg} not found.")
        sys.exit(1)

    # Print the arrays in two columns: MRDhitT and MRDhitDetID
    print(f"{'MRDhitT':>15} {'MRDhitDetID':>15}")
    for t, det_id in zip(mrd_hit_t[idx], mrd_hit_det_id[idx]):
        print(f"{t:15} {det_id:15}")
