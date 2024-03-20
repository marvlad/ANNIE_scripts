# To run use for example `python3.11 plot5.py ./WaveForms_2D.root lappd63_laser_on_test 10`
# python3 plot5.py [path/rootfile_name] [name_of_the_pdf] [number_of_events]

import uproot
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
#from matplotlib import PdfPages
import numpy as np
import sys
from tqdm import tqdm
import time

filepath = sys.argv[1]
output_name = sys.argv[2]
nevent = int(sys.argv[3])
spare_channels = int(sys.argv[4])

# Open the ROOT file and access the TDirectoryFile
file = uproot.open(filepath)
directory = file["off_beam"]

# Create a PDF file to save the plots
with PdfPages(output_name+".pdf") as pdf:
        # Loop over each pair of histograms and plot them side by side
        # Initialize the progress bar
        progress_bar = tqdm(total=nevent, desc="Progress", unit="iteration")

        for i in range(nevent):
                # Get the data from the TH2D histograms
                data_event0 = directory[f"event0_{i}"].values()
                data_event1 = directory[f"event1_{i}"].values()

                # Convert the data to numpy arrays
                data_event0 = np.array(data_event0)
                data_event1 = np.array(data_event1)

                # Set the figure size
                fig, axs = plt.subplots(2, 2, figsize=(15, 9))
                #plt.show(block=False)

                row_t,colum_t=data_event0.shape
                #print(row_t,colum_t)

                # Plot the histograms side by side
                im0 = axs[0,0].imshow(data_event0.T, origin="lower", cmap="viridis", aspect="auto")
                axs[0,0].set_title(f"Side 0 Event {i}")
                axs[0,0].set_xlabel("Time [ns]")
                axs[0,0].set_ylabel("Strip")
                cbar0 = fig.colorbar(im0, ax=axs[0,0])
                cbar0.set_label('Amplitude [mV]')

                # Loop over each bin of the projected 2D histogram and plot the 1D histogram
                for j in range(data_event0.shape[1]):
                    y_projection = data_event0[:, j]

                    # Plot the 1D histogram
                    axs[1,0].plot(y_projection, label=f"Bin {j}")

                axs[1,0].set_xlabel("Time [ns]")
                axs[1,0].set_ylabel("Amplitude [mV]")

                im1 = axs[0,1].imshow(data_event1.T, origin="lower", cmap="viridis", aspect="auto")
                axs[0,1].set_title(f"Side 1 Event {i}")
                axs[0,1].set_xlabel("Time [ns]")
                axs[0,1].set_ylabel("Strip")
                cbar1 = fig.colorbar(im1, ax=axs[0,1])
                cbar1.set_label('Amplitude [mV]')

                # Loop over each bin of the projected 2D histogram and plot the 1D histogram
                for j in range(data_event1.shape[1]):
                    y_projection = data_event1[:, j]

                    # Plot the 1D histogram
                    axs[1,1].plot(y_projection, label=f"Bin {j}")

                axs[1,1].set_xlabel("Time [ns]")
                axs[1,1].set_ylabel("Amplitude [mV]")

                # Add the plot to the PDF file
                pdf.savefig(fig)
                plt.close()
                progress_bar.update(1)

        progress_bar.close()
