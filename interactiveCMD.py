from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Column
from bokeh.io import curdoc
from bokeh.events import DoubleTap

import pandas as pd

coordList = []

def createInteractive(photfile, mag = 'G', color1 = 'G_BP', color2 = 'G_RP', xrng = [0.5,2], yrng = [20,10]):

	# create the initial figure
	TOOLS = "tap"
	bound = 10
	p = figure(title = 'Double click to leave a dot.',
			   tools = TOOLS, width = 500, height = 700,
			   x_range = xrng, y_range = yrng)

	# read in the phot file and define the input for Bokeh
	df = pd.read_csv(photfile, sep='\s+')
	sourcePhot = ColumnDataSource(data = dict(x = df[color1] - df[color2], y = df[mag]))

	# add the phot points to the plot
	p.scatter('x', 'y', source=sourcePhot, color='gray', alpha=0.5, size=5, marker='circle')

	# to hold the user-added points
	source = ColumnDataSource(data = dict(x = [], y = []))   
	p.circle(source = source, x = 'x', y = 'y', color='firebrick', size=10) 

	#add a dot where the click happened
	def callback(event):
		global coordList

		Coords = (event.x, event.y)
		coordList.append(Coords) 
		source.data = dict(x = [i[0] for i in coordList], y = [i[1] for i in coordList])        
	
	p.on_event(DoubleTap, callback)

	# One single plot for the layout
	layout = Column(p)

	return(layout)

