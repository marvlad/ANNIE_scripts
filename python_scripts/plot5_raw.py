import uproot
import matplotlib.pyplot as plt
import numpy as np
import re
from matplotlib.backends.backend_pdf import PdfPages
import sys

zmin=-10
zmax=60
fsize = 18

def plot_histograms(root_file_path, output_name="output", sparechannel=0, event_number=None):
    root_file = uproot.open(root_file_path)
    
    histogram_names = root_file.keys()
    event_data = [event for event in histogram_names if 'Bin' not in event]
    print(f"Total events: {len(event_data)}")
    
    with PdfPages(output_name + ".pdf") as pdf:
        if event_number is not None and event_number != -1:
            # Plot both sides of a single event
            try:
                event_number = int(event_number)
                if event_number < 0 or event_number >= len(event_data):
                    print(f"Error: Event number {event_number} is out of range (0 to {len(event_data)-1})")
                    sys.exit(1)
                if event_number + 1 >= len(event_data):
                    print(f"Error: No right-side histogram for event {event_number} (needs index {event_number+1})")
                    sys.exit(1)
                
                # Get the pair of histograms for the event (left and right sides)
                hist1_name = event_data[event_number*2] # time 2 for some reason
                hist2_name = event_data[event_number*2 + 1]
                
                hist1 = root_file[hist1_name]
                hist2 = root_file[hist2_name]
                
                # Convert histograms to NumPy arrays and adjust strips
                values1, xedges1, yedges1 = hist1.to_numpy()
                values2, xedges2, yedges2 = hist2.to_numpy()
                if sparechannel == 0:
                    values1 = values1[:, 1:-1]
                    values2 = values2[:, 1:-1]
                    yedges1 = yedges1[1:-1]
                    yedges2 = yedges2[1:-1]
                
                # Create figure with 2x2 subplots (left and right sides)
                fig, axs = plt.subplots(2, 2, figsize=(15, 9))
                
                # Left side (hist1)
                im0 = axs[0, 0].imshow(values1.T, origin="lower", cmap="jet", aspect="auto",
                                      extent=[0, 25.6, yedges1[0], yedges1[-1]],vmin=zmin, vmax=zmax)
                #axs[0, 0].set_title(f"2D Histogram: {hist1_name} (Left)", fontsize=fsize)
                axs[0, 0].set_xlabel("Time [ns]", fontsize=fsize)
                axs[0, 0].set_ylabel("Strip #", fontsize=fsize)
                axs[0, 0].tick_params(axis='both', labelsize=fsize)  # Set tick label fontsize 
                cbar0 = fig.colorbar(im0, ax=axs[0, 0])
                cbar0.set_label('Amplitude [mV]', fontsize=fsize)
                cbar0.ax.tick_params(labelsize=fsize) 
                
                for j in range(values1.shape[1]):
                    y_projection = values1[:, j]
                    axs[1, 0].plot(xedges1[:-1] * (25.6 / 256), y_projection, label=f"Bin {j}")
                axs[1, 0].set_xlabel("Time [ns]", fontsize=fsize)
                axs[1, 0].set_ylabel("Amplitude [mV]", fontsize=fsize)
                axs[1, 0].tick_params(axis='both', labelsize=fsize)  # Set tick label fontsize 
                
                # Right side (hist2)
                im1 = axs[0, 1].imshow(values2.T, origin="lower", cmap="jet", aspect="auto",
                                      extent=[0, 25.6, yedges2[0], yedges2[-1]],vmin=zmin, vmax=zmax)
                #axs[0, 1].set_title(f"2D Histogram: {hist2_name} (Right)", fontsize=fsize)
                axs[0, 1].set_xlabel("Time [ns]", fontsize=fsize)
                axs[0, 1].set_ylabel("Strip #", fontsize=fsize)
                axs[0, 1].tick_params(axis='both', labelsize=fsize)  # Set tick label fontsize 
                cbar1 = fig.colorbar(im1, ax=axs[0, 1])
                cbar1.set_label('Amplitude [mV]', fontsize=fsize)
                cbar1.ax.tick_params(labelsize=fsize)  # Set colorbar tick label fontsize 

                
                for j in range(values2.shape[1]):
                    y_projection = values2[:, j]
                    axs[1, 1].plot(xedges2[:-1] * (25.6 / 256), y_projection, label=f"Bin {j}")
                axs[1, 1].set_xlabel("Time [ns]", fontsize=fsize)
                axs[1, 1].set_ylabel("Amplitude [mV]", fontsize=fsize)
                axs[1, 1].tick_params(axis='both', labelsize=fsize)  # Set tick label fontsize 
                
                plt.tight_layout()
                
                pdf.savefig(fig)
                plt.close()
                
            except ValueError:
                print("Error: Event number must be an integer")
                sys.exit(1)
        else:
            # Plot all events in pairs (original behavior)
            for i in range(0, len(event_data), 2):
                if i + 1 < len(event_data):
                    hist1_name = event_data[i]
                    hist2_name = event_data[i + 1]
                    
                    hist1 = root_file[hist1_name]
                    hist2 = root_file[hist2_name]
                    
                    values1, xedges1, yedges1 = hist1.to_numpy()
                    values2, xedges2, yedges2 = hist2.to_numpy()
                    if sparechannel == 0:
                        values1 = values1[:, 1:-1]
                        values2 = values2[:, 1:-1]
                        yedges1 = yedges1[1:-1]
                        yedges2 = yedges2[1:-1]
                    
                    fig, axs = plt.subplots(2, 2, figsize=(15, 9))
                    
                    im0 = axs[0, 0].imshow(values1.T, origin="lower", cmap="viridis", aspect="auto",
                                          extent=[0, 25.6, yedges1[0], yedges1[-1]])
                    axs[0, 0].set_title(f"2D Histogram: {hist1_name} (Left)", fontsize=fsize)
                    axs[0, 0].set_xlabel("Time [ns]", fontsize=fsize)
                    axs[0, 0].set_ylabel("Strip #", fontsize=fsize)
                    cbar0 = fig.colorbar(im0, ax=axs[0, 0])
                    cbar0.set_label('Amplitude [mV]', fontsize=fsize)
                    cbar0.ax.tick_params(labelsize=fsize) 
                    
                    for j in range(values1.shape[1]):
                        y_projection = values1[:, j]
                        axs[1, 0].plot(xedges1[:-1] * (25.6 / 256), y_projection, label=f"Bin {j}")
                    axs[1, 0].set_xlabel("Time [ns]", fontsize=fsize)
                    axs[1, 0].set_ylabel("Amplitude [mV]", fontsize=fsize)
                    axs[1, 0].tick_params(axis='both', labelsize=fsize)  # Set tick label fontsize  
                    
                    im1 = axs[0, 1].imshow(values2.T, origin="lower", cmap="viridis", aspect="auto",
                                          extent=[0, 25.6, yedges2[0], yedges2[-1]])
                    axs[0, 1].set_title(f"2D Histogram: {hist2_name} (Right)", fontsize=fsize)
                    axs[0, 1].set_xlabel("Time [ns]", fontsize=fsize)
                    axs[0, 1].set_ylabel("Strip #", fontsize=fsize)
                    cbar1 = fig.colorbar(im1, ax=axs[0, 1])
                    cbar1.set_label('Amplitude [mV]', fontsize=fsize)
                    cbar1.ax.tick_params(labelsize=fsize) 
                    
                    for j in range(values2.shape[1]):
                        y_projection = values2[:, j]
                        axs[1, 1].plot(xedges2[:-1] * (25.6 / 256), y_projection, label=f"Bin {j}")
                    axs[1, 1].set_xlabel("Time [ns]", fontsize=fsize)
                    axs[1, 1].set_ylabel("Amplitude [mV]", fontsize=fsize)
                    axs[1, 1].tick_params(axis='both', labelsize=fsize)  # Set tick label fontsize  
                    
                    plt.tight_layout()
                    
                    pdf.savefig(fig)
                    plt.close()
                else:
                    print("WARNING: Odd number of events, skipping last event")

# Command-line argument handling
if __name__ == "__main__":
    event_number = None
    sparechannel = 0
    
    if len(sys.argv) > 1:
        try:
            event_number = int(sys.argv[1])
        except ValueError:
            print("Error: Event number must be an integer")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        try:
            sparechannel = int(sys.argv[2])
        except ValueError:
            print("Error: Sparechannel must be an integer")
            sys.exit(1)
    
    plot_histograms("LAPPDPlots.root", sparechannel=sparechannel, event_number=event_number)
