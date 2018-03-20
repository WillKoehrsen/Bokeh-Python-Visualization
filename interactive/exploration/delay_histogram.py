import pandas as pd
import numpy as np

from bokeh.io import show, curdoc
from bokeh.plotting import figure

from bokeh.models import CategoricalColorMapper, HoverTool, ColumnDataSource, Panel
from bokeh.models.widgets import CheckboxGroup, Slider, RangeSlider, Tabs

from bokeh.layouts import column, row, WidgetBox
from bokeh.palettes import Category20_16

# Read in data
flights = pd.read_csv('../data/complete_flights.csv', index_col=0)[['arr_delay', 'carrier', 'name']]

# Available carrier list
available_carriers = list(flights['name'].unique())

# Sort the list in-place (alphabetical order)
available_carriers.sort()

# Dataset based on selected carriers, selected start and end of delays,
# and selected width of bin
def make_dataset(carrier_list, range_start, range_end, bin_width):

    by_carrier = pd.DataFrame(columns=['proportion', 'left', 'right', 
                                       'f_proportion', 'f_interval',
                                       'name', 'color'])
    range_extent = range_end - range_start

    # Iterate through all the carriers
    for i, carrier_name in enumerate(carrier_list):

        # Subset to the carrier
        subset = flights[flights['name'] == carrier_name]

        # Create a histogram with 5 minute bins
        arr_hist, edges = np.histogram(subset['arr_delay'], 
                                       bins = int(range_extent / bin_width), 
                                       range = [range_start, range_end])

        # Divide the counts by the total to get a proportion
        arr_df = pd.DataFrame({'proportion': arr_hist / np.sum(arr_hist), 'left': edges[:-1], 'right': edges[1:] })

        # Format the proportion 
        arr_df['f_proportion'] = ['%0.5f' % proportion for proportion in arr_df['proportion']]

        # Format the interval
        arr_df['f_interval'] = ['%d to %d minutes' % (left, right) for left, right in zip(arr_df['left'], arr_df['right'])]

        # Assign the carrier for labels
        arr_df['name'] = carrier_name

        # Color each carrier differently
        arr_df['color'] = Category20_16[i]

        # Add to the overall dataframe
        by_carrier = by_carrier.append(arr_df)

    # Overall dataframe
    by_carrier = by_carrier.sort_values(['name', 'left'])

    return ColumnDataSource(by_carrier)

# Styling for a plot
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

# Function to make the plot
def make_plot(src):
    # Blank plot with correct labels
    p = figure(plot_width = 700, plot_height = 700, 
              title = 'Histogram of Arrival Delays by Carrier',
              x_axis_label = 'Delay (min)', y_axis_label = 'Proportion')

    # Quad glyphs to create a histogram
    p.quad(source = src, bottom = 0, top = 'proportion', left = 'left', right = 'right',
           color = 'color', fill_alpha = 0.7, hover_fill_color = 'color', legend = 'name',
           hover_fill_alpha = 1.0, line_color = 'black')

    # Hover tool with vline mode
    hover = HoverTool(tooltips=[('Carrier', '@name'), 
                                ('Delay', '@f_interval'),
                                ('Proportion', '@f_proportion')],
                      mode='vline')

    p.add_tools(hover)

    p.legend.click_policy = 'hide'

    # Styling
    p = style(p)

    return p

# Update the plot based on selections
def update(attr, old, new):
    carriers_to_plot = [carrier_selection.labels[i] for i in carrier_selection.active]

    new_src = make_dataset(carriers_to_plot,
                           range_start = range_select.value[0],
                           range_end = range_select.value[1],
                           bin_width = binwidth_select.value)

    src.data.update(new_src.data)


# CheckboxGroup to select carrier to display
carrier_selection = CheckboxGroup(labels=available_carriers, active = [0, 1])
carrier_selection.on_change('active', update)

# Slider to select width of bin
binwidth_select = Slider(start = 1, end = 30, 
                     step = 1, value = 5,
                     title = 'Delay Width (min)')
binwidth_select.on_change('value', update)

# RangeSlider control to select start and end of plotted delays
range_select = RangeSlider(start = -60, end = 180, value = (-60, 120),
                           step = 5, title = 'Delay Range (min)')
range_select.on_change('value', update)


# Find the initially selected carrieres
initial_carriers = [carrier_selection.labels[i] for i in carrier_selection.active]

src = make_dataset(initial_carriers,
                  range_start = range_select.value[0],
                  range_end = range_select.value[1],
                  bin_width = binwidth_select.value)

p = make_plot(src)

# Put controls in a single element
controls = WidgetBox(carrier_selection, binwidth_select, range_select)

# Create a row layout
layout = row(controls, p)

# Make a tab with the layout 
tab = Panel(child=layout, title = 'Delay Histogram')
tabs = Tabs(tabs=[tab])

# Add it to the current document (displays plot)
curdoc().add_root(tabs)