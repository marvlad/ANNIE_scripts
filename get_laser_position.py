# This script gives you the position of the laserball in the detector
# With the --ask option, it can also tell you how to deply the ball to reach the desired location (user input)
# Author: Vincent Fischer

import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from matplotlib import colors, cm
from matplotlib.patches import Rectangle

import numpy as np
import math, time
import optparse

### ------- Initialisation ------- ##
#-----------------------------------------------------------------------------------------------#
start = time.time()

# Some constants [cm]
sleeve_length = 20.
d_top_bot_beam_outer = 323.56 
d_top_bot_PMTface = 273.8
d_topbeam_toptank = 38.23 
d_topPMTface_toptank = 60.7
d_toptank_topports = [24.19, 22.19, 23.39, 24.19, 35.19] 

X_pos_ports = [-75.0, 75.0, 102.0, 0.0, 0.0]
Y_pos_ports = [0.0, 0.0, 0.0, 75.0, 0.0]

### ------- Main function ------- ##
#-----------------------------------------------------------------------------------------------#

if __name__=="__main__":
	parser = optparse.OptionParser(description='Computes the laserball position in the tank, python get_laser_position.py <options>')
	parser.add_option('-n', dest="sleeves", help='Number of sleeves fully passed the calibration port [cm]')
	parser.add_option('-d', dest="housing", help='Distance between the bottom of the first sleeve (above the black RTV glue) and the laserball [cm]')
	parser.add_option('-l', dest="extra_sleeve", help='Distance between top of last sleeve (out of the port) and top of calibration port [cm]')
	parser.add_option('-p', dest="port", help='Port being used (1 to 5)')
	parser.add_option('--ask', action='store_true', help='Gives you the number of sleeves and extra distance needed for a given position')
	(options, args) = parser.parse_args()
	
	if options.ask == True and (options.sleeves != None or options.extra_sleeve != None):
		parser.print_help()
		raise Exception("The --ask option doesn't require -n or -l (since it will give it to you)...")
	
	
	n_port = int(options.port)
	d_housing = float(options.housing)
	if options.ask == True:
		ask_bool = options.ask
	else:
		n_sleeves = int(options.sleeves)
		d_extra_sleeve = float(options.extra_sleeve)
	
	# Sanity tests
	if options.ask != True:
		if d_extra_sleeve > sleeve_length:
			parser.print_help()
			raise Exception("This distance should be shorter or equal to the sleeve's length!")
		if n_sleeves <= 0 or d_housing <= 0. or d_extra_sleeve < 0.:
			parser.print_help()
			raise Exception("Negative values?! Come on...")
		if n_port <= 0 or n_port > 5:
			parser.print_help()
			raise Exception("Port number must be between 1 and 5")
	
	if options.ask == True:
		print("-------------------------------")
		print("What position do you want the source to be located at in Z (vertical, bottom to top)? Remember that (0,0,0) is the center of the PMTs not the inner structure beams!")
		Zpos_text = input("Z position: ")
		Zpos_number = float(Zpos_text)
		
	# Some outputs to confirm the numbers
	print( "-------------------------------")
	print( "Source deployed in port %i (see picture)" % n_port)
	print( "Distance between bottom of housing and first sleeve = %.2f cm" % d_housing)
	if options.ask == True:
		print( "-------------------------------")
		print( "You want the source at (X, Y, Z) = (%.2f, %.2f, %.2f)" % (X_pos_ports[n_port-1], Y_pos_ports[n_port-1], Zpos_number))
	else:	
		print( "-------------------------------")
		print( "Number of sleeves fully in the port = %i  -   Distance from top of last sleeve (out of the port) to top of calibration port = %.2f cm" % (n_sleeves, d_extra_sleeve))
	
	if options.ask == True:
		d_top_pmt_ask = 0.5*d_top_bot_PMTface - Zpos_number - d_housing + (d_topPMTface_toptank + d_toptank_topports[n_port-1])
		n_sleeves_ask = np.floor(d_top_pmt_ask/sleeve_length)
		d_extra_sleeve_ask = sleeve_length - d_top_pmt_ask%sleeve_length
		print( "-------------------------------")
		print( "-------------------------------")
		print( "To have the source located at (%.2f, %.2f, %.2f),you need to have %i sleeves in the calibration port and a distance of %.2f cm between the top of last sleeve (out of the port) and top of calibration port [cm]" % (X_pos_ports[n_port-1], Y_pos_ports[n_port-1], Zpos_number,n_sleeves_ask,d_extra_sleeve_ask))
		
		source_X_beam = X_pos_ports[n_port-1]
		source_Y_beam = Y_pos_ports[n_port-1]
		source_Z_beam = Zpos_number
	else:	
		# Computes the source distances relative to the PMTs/beams
		d_top_beam = d_housing + sleeve_length*n_sleeves + (sleeve_length - d_extra_sleeve) - (d_topbeam_toptank + d_toptank_topports[n_port-1])
		d_bot_beam = d_top_bot_beam_outer - d_top_beam
	
		d_top_pmt = d_housing + sleeve_length*n_sleeves + (sleeve_length - d_extra_sleeve) - (d_topPMTface_toptank + d_toptank_topports[n_port-1])
		d_bot_pmt = d_top_bot_PMTface - d_top_pmt
	
		# Source position in X,Y,Z 
		source_X_beam = X_pos_ports[n_port-1]
		source_Y_beam = Y_pos_ports[n_port-1]
		source_Z_beam = 0.5*d_top_bot_beam_outer - d_top_beam
	
		source_X_PMT = X_pos_ports[n_port-1]
		source_Y_PMT = Y_pos_ports[n_port-1]
		source_Z_PMT = 0.5*d_top_bot_PMTface - d_top_pmt
	
		print ("-------------------------------")
		print ("-------------------------------")
		print ("The AmBe source is located %.2f cm away from the top beams (outer) and %.2f cm away from the botton beams (outer)" % (d_top_beam, d_bot_beam))
		print ("The AmBe source is located %.2f cm away from the top PMTs (face) and %.2f cm away from the botton PMTs (face)" % (d_top_pmt, d_bot_pmt))
		print ("-------------------------------")
		print ("If center of the beams is (0,0,0) cm, the source is at (%.2f,%.2f,%.2f) cm (see plot for axis orientation)" % (source_X_beam, source_Y_beam, source_Z_beam))
		print ("If center of the PMTs volume is (0,0,0) cm, the source is at (%.2f,%.2f,%.2f) cm (see plot for axis orientation)" % (source_X_PMT, source_Y_PMT, source_Z_PMT))
	
	
	### ------- Plotting ------- ##
	# Handle the whole "current port in red not blue" thing
	color_port = ['blue', 'blue', 'blue', 'blue', 'blue']
	fontsize_port = [12,12,12,12,12]
	color_port[n_port-1] = 'red'
	fontsize_port[n_port-1] = 18
	
	# 2 plots, [0] is top view, [1] is side view
	fig, ax = plt.subplots(1, 2, sharey=False, tight_layout=True)
	
	## -- Top view -- ##
	
	ax[0].text(-165, 170, "Top view", fontsize=30)
	
	# Fix the aspect ratio
	ax[0].set_xlim((-190, 190))
	ax[0].set_ylim((-190, 190))
	ax[0].set_aspect('equal')
	
	# Draw the tank top, hatch and ports
	tank_lid = plt.Circle((0, 0), 157.8, color='black', fill=False, clip_on=False, linewidth=3)
	tank_hatch = plt.Circle((0, 0), 56.5, color='black', fill=False, clip_on=False, linewidth=3)
	calib_port_1_in = plt.Circle((Y_pos_ports[0], X_pos_ports[0]), 4.78, color=color_port[0], fill=False, clip_on=False)
	calib_port_1_out = plt.Circle((Y_pos_ports[0], X_pos_ports[0]), 9.0, color=color_port[0], fill=False, clip_on=False)
	calib_port_2_in = plt.Circle((Y_pos_ports[1], X_pos_ports[1]), 4.78, color=color_port[1], fill=False, clip_on=False)
	calib_port_2_out = plt.Circle((Y_pos_ports[1], X_pos_ports[1]), 9.0, color=color_port[1], fill=False, clip_on=False)
	calib_port_3_in = plt.Circle((Y_pos_ports[2], X_pos_ports[2]), 4.78, color=color_port[2], fill=False, clip_on=False)
	calib_port_3_out = plt.Circle((Y_pos_ports[2], X_pos_ports[2]), 9.0, color=color_port[2], fill=False, clip_on=False)
	calib_port_4_in = plt.Circle((-Y_pos_ports[3], X_pos_ports[3]), 4.78, color=color_port[3], fill=False, clip_on=False)
	calib_port_4_out = plt.Circle((-Y_pos_ports[3], X_pos_ports[3]), 9.0, color=color_port[3], fill=False, clip_on=False)
	calib_port_5_in = plt.Circle((Y_pos_ports[4], X_pos_ports[4]), 4.78, color=color_port[4], fill=False, clip_on=False)
	calib_port_5_out = plt.Circle((Y_pos_ports[4], X_pos_ports[4]), 9.0, color=color_port[4], fill=False, clip_on=False)
	
	ax[0].text(12, -75, "Port 1", color=color_port[0], fontsize=fontsize_port[0])
	ax[0].text(12, 75, "Port 2", color=color_port[1], fontsize=fontsize_port[1])
	ax[0].text(12, 100, "Port 3", color=color_port[2], fontsize=fontsize_port[2])
	ax[0].text(-80, 15, "Port 4", color=color_port[3], fontsize=fontsize_port[3])
	ax[0].text(12, 0, "Port 5", color=color_port[4], fontsize=fontsize_port[4])
	
	# LAPPD slots
	ax[0].add_patch(Rectangle((-24.7, 120.0), 49.5, 26.7, color='black', fill=False, angle=0))
	ax[0].add_patch(Rectangle((-105, 70.0), 49.5, 26.7, color='black', fill=False, angle=45))
	ax[0].add_patch(Rectangle((-120, -24.7), 49.5, 26.7, color='black', fill=False, angle=90))
	ax[0].add_patch(Rectangle((-70, -105.0), 49.5, 26.7, color='black', fill=False, angle=135))
	ax[0].add_patch(Rectangle((-24.7, -146.7), 49.5, 26.7, color='black', fill=False, angle=0))
	ax[0].add_patch(Rectangle((105, -70.0), 49.5, 26.7, color='black', fill=False, angle=-135))
	ax[0].add_patch(Rectangle((120, 24.7), 49.5, 26.7, color='black', fill=False, angle=-90))
	ax[0].add_patch(Rectangle((70, 105.0), 49.5, 26.7, color='black', fill=False, angle=-45))
	
	ax[0].add_artist(tank_lid)
	ax[0].add_artist(tank_hatch)
	ax[0].add_artist(calib_port_1_in)
	ax[0].add_artist(calib_port_1_out)
	ax[0].add_artist(calib_port_2_in)
	ax[0].add_artist(calib_port_2_out)
	ax[0].add_artist(calib_port_3_in)
	ax[0].add_artist(calib_port_3_out)
	ax[0].add_artist(calib_port_4_in)
	ax[0].add_artist(calib_port_4_out)
	ax[0].add_artist(calib_port_5_in)
	ax[0].add_artist(calib_port_5_out)
	
	# Axis display (on the side
	x_axis_mark = plt.Circle((160, -160), 5.0, color='black', fill=False, clip_on=False)
	
	ax[0].add_artist(x_axis_mark)
	ax[0].plot(160, -160, 'o', color='black')
	ax[0].text(165, -170, "Z", fontsize=12)
	
	ax[0].arrow(160, -160, 0, 20, head_width=5)
	ax[0].text(165, -140, "X", fontsize=12)
	
	ax[0].arrow(160, -160, -20, 0, head_width=5)
	ax[0].text(135, -150, "Y", fontsize=12)
	
	# Beam direction
	ax[0].arrow(-160, -160, 0, 20, head_width=5)
	ax[0].text(-160, -170, "Beam", fontsize=18)
	
	## -- Side view -- ##
	
	ax[1].text(-160, 220, "Side view", fontsize=30)
	
	# Fix the aspect ratio
	ax[1].set_xlim((-190, 190))
	ax[1].set_ylim((-250, 250))
	ax[1].set_aspect('equal')
	
	# Tank (simplified)
	ax[1].add_patch(Rectangle((-157.8, -191.15), 305, 391.16, color='black', fill=False, angle=0, linewidth=3))
	
	# Inner structure (simplified)
	ax[1].add_patch(Rectangle((-125.1, -162.6), 250.19, 5.08, color='black', fill=False, angle=0))
	ax[1].add_patch(Rectangle((-125.1, 162.6), 250.19, 5.08, color='black', fill=False, angle=0))
	
	ax[1].add_patch(Rectangle((-125.1, -191.2), 5.08, 384.2, color='black', fill=False, angle=0))
	ax[1].add_patch(Rectangle((120, -191.2), 5.08, 384.2, color='black', fill=False, angle=0))
	
	# Axis display (on the side
	x_axis_mark = plt.Circle((0, -220), 5.0, color='black', fill=False, clip_on=False)
	ax[1].add_artist(x_axis_mark)
	ax[1].plot(0, -220, 'x', color='black')
	
	ax[1].text(-10, -230, "Y", fontsize=12)
	
	ax[1].arrow(0, -220, 0, 20, head_width=5)
	ax[1].text(8, -200, "Z", fontsize=12)
	
	ax[1].arrow(0, -220, 20, 0, head_width=5)
	ax[1].text(20, -230, "X", fontsize=12)
	
	# Beam direction
	ax[1].arrow(-160, -220, 20, 0, head_width=5)
	ax[1].text(-160, -240, "Beam", fontsize=18)
	
	# Source and housing (estimates)
	ax[1].add_patch(Rectangle((source_X_beam, source_Z_beam), 2, 2, color='red', fill=True, angle=0))
	ax[1].add_patch(Rectangle((source_X_beam-2, source_Z_beam-2), 6, 10, color='black', linewidth=3, fill=False, angle=0))
	
	source_highlight = plt.Circle((source_X_beam+1, source_Z_beam+1), 20.0, color='red', fill=False, clip_on=False)
	ax[1].add_artist(source_highlight)
	
	plt.show()
