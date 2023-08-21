# Analysis LAPPD ROOTfile
# Thu Aug 17, 2023

import uproot
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

# Merged root files 
#my_data=uproot.concatenate(["/Users/marvinascenciososa/Downloads/Pesestal_f/Analysis.root:ffmytree"],filter_name=["pulseamp_simp","pulsestrip_simp"],library="pd")
#my_data=uproot.concatenate(["/Users/marvinascenciososa/Desktop/LAb6_laser_outputs/Analysis.root:ffmytree"],filter_name=["pulseamp_simp","pulsestrip_simp"],library="pd")
my_data=uproot.concatenate(["/Users/marvinascenciososa/Desktop/LAb6_laser_outputs/3.5/Analysis.root:ffmytree"],filter_name=["pulseamp_simp","pulsestrip_simp"],library="pd")

# Empty arrays
filtered_data_0 = []
filtered_data_1 = []
filtered_data_2 = []

# Loop over the event and cut based on 'lappdid'
for index, row in my_data.iterrows():
    for br in row['pulsestrip_simp']:
        if br == 11:
            filtered_data_0.append(row['pulseamp_simp'][row['pulsestrip_simp'].index(br)])
        if br == 12:
            filtered_data_1.append(row['pulseamp_simp'][row['pulsestrip_simp'].index(br)])
        if br == 13:
            filtered_data_2.append(row['pulseamp_simp'][row['pulsestrip_simp'].index(br)])

# Moving to pandas DataFrame
filtered_data_pd_0 = pd.DataFrame(filtered_data_0, columns=['pulseamp_simp'])
filtered_data_pd_1 = pd.DataFrame(filtered_data_1, columns=['pulseamp_simp'])
filtered_data_pd_2 = pd.DataFrame(filtered_data_2, columns=['pulseamp_simp'])

# Plotting stuff
fig,ax = plt.subplots()

plt.hist(filtered_data_pd_0, bins=100,label='Strip 11', histtype='step')
plt.hist(filtered_data_pd_1, bins=100,label='Strip 12', histtype='step')
plt.hist(filtered_data_pd_2, bins=100,label='Strip 13', histtype='step')
plt.yscale('log')

ax.set_xlabel("Pulse Amplitude [mV]",fontsize=14)
ax.set_ylabel("Entries",fontsize=14)
plt.legend()
plt.show()
