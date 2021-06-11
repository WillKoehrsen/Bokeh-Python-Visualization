# pandas and numpy for data manipulation
import pandas as pd
import numpy as np

from bokeh.plotting import figure
from bokeh.models import (CategoricalColorMapper, HoverTool, 
						  ColumnDataSource, Panel, 
						  FuncTickFormatter, SingleIntervalTicker, LinearAxis)
from bokeh.models.widgets import (CheckboxGroup, Slider, RangeSlider, 
								  Tabs, CheckboxButtonGroup, 
								  TableColumn, DataTable, Select)
from bokeh.layouts import column, row, WidgetBox
from bokeh.palettes import Category20_16

def map_tab(map_data, states):

	# Function to make a dataset for the map based on a list of carriers
	def make_dataset(carrier_list):
		
		# Subset to the carriers in the specified list
		subset = map_data[map_data['carrier']['Unnamed: 3_level_1'].isin(
														   carrier_list)]

		
		# Dictionary mapping carriers to colors
		color_dict = {carrier: color for carrier, color in zip(
			available_carriers, airline_colors)}
		
		# Lists of data for plotting
		flight_x = []
		flight_y = []
		colors = []
		carriers = []
		counts = []
		mean_delays = []
		min_delays = []
		max_delays = []
		dest_loc = []
		origin_x_loc = []
		origin_y_loc = []
		dest_x_loc = []
		dest_y_loc = []
		origins = []
		dests = []
		distances = []

		# Iterate through each carrier
		for carrier in carrier_list:

			# Subset to the carrier
			sub_carrier = subset[subset['carrier']['Unnamed: 3_level_1'] == carrier]

			# Iterate through each route (origin to destination) for the carrier
			for _, row in sub_carrier.iterrows():

				colors.append(color_dict[carrier])
				carriers.append(carrier)
				origins.append(row['origin']['Unnamed: 1_level_1'])
				dests.append(row['dest']['Unnamed: 2_level_1'])

				# Origin x (longitude) and y (latitude) location
				origin_x_loc.append(row['start_long']['Unnamed: 20_level_1'])
				origin_y_loc.append(row['start_lati']['Unnamed: 21_level_1'])

				# Destination x (longitude) and y latitude (location)
				dest_x_loc.append(row['end_long']['Unnamed: 22_level_1'])
				dest_y_loc.append(row['end_lati']['Unnamed: 23_level_1'])

				# Flight x (longitude) locations
				flight_x.append([row['start_long']['Unnamed: 20_level_1'], 
								 row['end_long']['Unnamed: 22_level_1']])

				# Flight y (latitude) locations
				flight_y.append([row['start_lati']['Unnamed: 21_level_1'], 
								 row['end_lati']['Unnamed: 23_level_1']])


				# Stats about the particular route
				counts.append(row['arr_delay']['count'])
				mean_delays.append(row['arr_delay']['mean'])
				min_delays.append(row['arr_delay']['min'])
				max_delays.append(row['arr_delay']['max'])
				distances.append(row['distance']['mean'])


		# Create a column data source from the lists of lists
		new_src = ColumnDataSource(data = {'carrier': carriers, 'flight_x': flight_x, 'flight_y': flight_y, 
											   'origin_x_loc': origin_x_loc, 'origin_y_loc': origin_y_loc,
											   'dest_x_loc': dest_x_loc, 'dest_y_loc': dest_y_loc,
											   'color': colors, 'count': counts, 'mean_delay': mean_delays,
											   'origin': origins, 'dest': dests, 'distance': distances,
											   'min_delay': min_delays, 'max_delay': max_delays})

		return new_src

	def make_plot(src, xs, ys):
		
		# Create the plot with no axes or grid
		p = figure(plot_width = 1100, plot_height = 700, title = 'Map of 2013 Flight Delays Departing NYC')
		p.xaxis.visible = False
		p.yaxis.visible = False
		p.grid.visible = False

		# States are drawn as patches
		patches_glyph = p.patches(xs, ys, fill_alpha=0.2, fill_color = 'lightgray', 
								  line_color="#884444", line_width=2, line_alpha=0.8)

		# Airline flights are drawn as lines
		lines_glyph = p.multi_line('flight_x', 'flight_y', color = 'color', line_width = 2, 
								   line_alpha = 0.8, hover_line_alpha = 1.0, hover_line_color = 'color',
								   legend = 'carrier', source = src)

		# Origins are drawn as squares (all in NYC)
		squares_glyph = p.square('origin_x_loc', 'origin_y_loc', color = 'color', size = 10, source = src, 
								 legend = 'carrier')

		# Destinations are drawn as circles
		circles_glyph = p.circle('dest_x_loc', 'dest_y_loc', color = 'color', size = 10, source = src, 
								 legend = 'carrier')

		# Add the glyphs to the plot using the renderers attribute
		p.renderers.append(patches_glyph)
		p.renderers.append(lines_glyph)
		p.renderers.append(squares_glyph)
		p.renderers.append(circles_glyph)

		# Hover tooltip for flight lines, assign only the line renderer
		hover_line = HoverTool(tooltips=[('Airline', '@carrier'),
									('Number of Flights', '@count'),
									('Average Delay', '@mean_delay{0.0}'),
									('Max Delay', '@max_delay{0.0}'),
									('Min Delay', '@min_delay{0.0}')],
							  line_policy = 'next',
							  renderers = [lines_glyph])
		
		# Hover tooltip for origin and destination, assign only the line renderer
		hover_circle = HoverTool(tooltips=[('Origin', '@origin'),
										   ('Dest', '@dest'),
										   ('Distance (miles)', '@distance')],
								renderers = [circles_glyph])

		# Position the location so it does not overlap plot
		p.legend.location = (10, 50)

		# Add the hovertools to the figure
		p.add_tools(hover_line)
		p.add_tools(hover_circle)

		p = style(p) 
		
		return p
	
	# Styling 
	def style(p):
			
		# Title 
		p.title.align = 'center'
		p.title.text_font_size = '20pt'
		p.title.text_font = 'serif'

		# Axis titles
		p.xaxis.axis_label_text_font_size = '14pt'
		p.xaxis.axis_label_text_font_style = 'bold'
		p.yaxis.axis_label_text_font_size = '14pt'
		p.yaxis.axis_label_text_font_style = 'bold'

		# Tick labels
		p.xaxis.major_label_text_font_size = '12pt'
		p.yaxis.major_label_text_font_size = '12pt'

		return p
		
	# Show selected carriers on map
	def update(attr, old, new):
		# Find list of carriers and make a new data set
		carrier_list = [carrier_selection.labels[i] for i in carrier_selection.active]
		new_src = make_dataset(carrier_list)

		src.data.update(new_src.data)
			
			
	available_carriers = list(set(map_data['carrier']['Unnamed: 3_level_1']))
	available_carriers.sort()

	airline_colors = Category20_16
	airline_colors = sorted(airline_colors)

	# Remove Alaska and Hawaii from states
	if 'HI' in states: del states['HI']
	if 'AK' in states: del states['AK']

	# Put longitudes and latitudes in lists
	xs = [states[state]['lons'] for state in states]
	ys = [states[state]['lats'] for state in states]

	# CheckboxGroup to select carriers for plotting    
	carrier_selection = CheckboxGroup(labels=available_carriers, active = [0, 1])
	carrier_selection.on_change('active', update)

	# Initial carriers to plot
	initial_carriers = [carrier_selection.labels[i] for i in carrier_selection.active]

	# Initial source and plot
	src = make_dataset(initial_carriers)

	p = make_plot(src, xs, ys)

	# Layout setup
	layout = row(carrier_selection, p)
	tab = Panel(child = layout, title = 'Flight Map')

	return tab