from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Button, Div, PointDrawTool, Slider, TextInput
from bokeh.layouts import column, row
from bokeh.io import curdoc
from bokeh.transform import factor_cmap

from shapely.geometry import LineString as shLs
from shapely.geometry import Point as shPt

from astropy.io import ascii
import sys


def createInteractive(photfile, mag = 'G', color1 = 'G_BP', color2 = 'G_RP', xrng = [0.5,2], yrng = [20,10]):
	'''
	To run this in a Jupyter notebook (intended purpose):

	--------------------
	layout = createInteractive('filename.phot')

	def bkapp(doc):
		doc.add_root(layout)

	show(bkapp)
	--------------------

	To run this from command line:
	- Note: I have only built in a hook for the file argument, but others could be added easily.
	- IMPORTANT: first, uncomment the two lines at the bottom of this script.

	$ bokeh serve --show interactiveCMD.py --args filename.phot

	'''

	###########################
	# plot

	# create the initial figure
	TOOLS = "box_zoom, reset"
	p = figure(title = "",
		tools = TOOLS, width = 500, height = 700,
		x_range = xrng, y_range = yrng)

	# read in the phot file and define the input for Bokeh
	tbl = ascii.read(photfile)
	tbl['useDBI'] = [0]*len(tbl)
	sourcePhot = ColumnDataSource(data = dict(x = tbl[color1] - tbl[color2], y = tbl[mag]))
	# empty for now, but will be filled below in updateStatus
	sourcePhotSingles = ColumnDataSource(data = dict(x = [] , y = []))

	# add the phot points to the plot
	# Note: I could handle categorical color mapping with factor_cmap, but this does not seem to update in the callback when I change the status in sourcePhot (I removed status since this doesn't work)
	# colorMapper = factor_cmap('status', palette = ['black', 'dodgerblue'], factors = ['unselected', 'selected'])
	p.scatter(source = sourcePhot, x = 'x', y = 'y', alpha = 0.5, size = 3, marker = 'circle', color = 'black')
	p.scatter(source = sourcePhotSingles, x = 'x', y = 'y', alpha = 0.75, size = 8, marker = 'circle', color = 'dodgerblue')

	# add the PointDrawTool to allow users to draw points interactively
	# to hold the user-added points
	newPoints = ColumnDataSource(data = dict(x = [], y = []))   
	renderer = p.circle(source = newPoints, x = 'x', y = 'y', color = 'limegreen', size = 10) 
	drawTool = PointDrawTool(renderers = [renderer])
	p.add_tools(drawTool)
	p.toolbar.active_tap = drawTool

	# add the line connecting the user-added points
	p.line(source = newPoints, x = 'x', y = 'y', color = 'limegreen', width = 4)

	# add filled polygon to hold the region within the selection zone for the plot

	# callback to update the single-star selection when a point is added or when the slider changes
	# https://stackoverflow.com/questions/47177493/python-point-on-a-line-closest-to-third-point

	def updateStatus(attr, old, new):
		if (len(newPoints.data['x']) > 1):
			# define the user-drawn line using shapely
			lne = shLs([ (x,y) for x,y in zip(newPoints.data['x'], newPoints.data['y']) ])
			# find the distance for each point to the user-drawn line
			# clear the singles data
			data = dict(x = [] , y = [])
			for i, row in enumerate(tbl):
				x = row[color1] - row[color2]
				y = row[mag]
				pte = shPt(x, y)
				dst = pte.distance(lne)
				# if the distance is within the user-defined tolerance, set the status to selected
				tbl[i]['useDBI'] = 0
				if (dst < slider.value):
					tbl[i]['useDBI'] = 1
					data['x'].append(x)
					data['y'].append(y)
			sourcePhotSingles.data = data
	newPoints.on_change('data', updateStatus)

	###########################
	# widgets

	# add a slider to define the width of the selection, next to the line
	slider = Slider(start = 0, end = 0.1, value = 0.01, step = 0.001, title = "Selection Region")
	def sliderCallback(attr, old, new):
		updateStatus(attr, old, new)
	slider.on_change("value", sliderCallback)
	
	# add a reset button
	resetButton = Button(label = "Reset",  button_type = "danger", )

	def resetCallback(event):
		newPoints.data = dict(x = [], y = [])
		slider.value = 0.1  
		sourcePhot['status'] = ['unselected']*len(tbl)

	resetButton.on_click(resetCallback)

	# text box to define the output file
	outfile = TextInput(value = photfile + '.new', title = "Output File Name:")

	# add a button to apply the filter
	writeButton = Button(label = "Write File",  button_type = "success")

	def writeCallback(event):
		# output an updated phot file
		# This will be improved when the code is combined with BASE9_utils
		ascii.write(tbl, outfile.value, overwrite=True) 
		print('File saved : ', outfile.value) 

	writeButton.on_click(writeCallback)




	###########################
	# layout
	# plot on the left, buttons on the right
	buttons = column(
		slider, 
		Div(text='<div style="height: 15px;"></div>'),
		outfile,
		writeButton,
		Div(text='<div style="height: 50px;"></div>'),
		resetButton,
	)
	title = 	Div(text='<div style="font-size:20px; font-weight:bold">Interactive CMD</div>')
	instructions = 	Div(text='<ul style="font-size:14px">\
		<li>Add points that define a line along the single-star sequence.</li>\
		<li>To add points, first enable the "Point Draw Tool".</li>\
		<li>Click to create a marker.  Click+drag any marker to move it.  Click+backspace any marker to delete it.</li>\
		<li>Click the "Reset" button to remove all the points. </li>\
		<li>When finished, click the "Apply Selection" button to select the single members.</li>\
	</ul>')

	layout = column(title, instructions, row(p, buttons))

	return(layout)


# uncomment these last two lines if running in command line (outside of Jupyter notebook)
# layout = createInteractive(sys.argv[1])
# curdoc().add_root(layout)