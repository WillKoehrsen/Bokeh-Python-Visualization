import pandas as pd
import numpy as np

from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, HoverTool, Panel, Tabs, CheckboxGroup
from bokeh.layouts import row, widgetbox

by_carrier = pd.read_csv('../data/by_carrier.csv', index_col=0)

available_carriers = list(by_carrier['name'].unique())

def make_plot(src):
    # Create the figure
    p = figure(plot_height = 600, plot_width = 800, 
               title = 'Histogram of Airline Delays by Carrier',
               x_axis_label = 'Arrival Delay (min)', y_axis_label = 'Proportion')

    # Add the quad glpyh with the source by carrier
    p.quad(bottom = 0, left = 'left', right = 'right', top = 'proportion',
           fill_color = 'color',  legend = 'name', source = src,
          fill_alpha = 0.8, hover_fill_alpha = 1.0, hover_fill_color = 'color')
    
    # Create the hover tool
    # Create the hover tool
    hover = HoverTool(tooltips = [('Carrier', '@name'),
                              ('Proportion', '@f_proportion'),
                              ('Delay', '@f_interval')],
                         mode = 'vline')

    p.add_tools(hover)
    
    p.title.align = 'center'
    p.title.text_font_size = '18pt'
    p.xaxis.axis_label_text_font_size = '12pt'
    p.xaxis.major_label_text_font_size = '12pt'
    p.yaxis.axis_label_text_font_size = '12pt'
    p.yaxis.major_label_text_font_size = '12pt'
    
    return p

def get_dataset(carrier_list):
    subset = by_carrier[by_carrier['name'].isin(carrier_list)]
    new_src = ColumnDataSource(subset)
    
    return new_src

def update(attr, old, new):
    carrier_list = [available_carriers[i] for i in carrier_select.active]
    new_src = get_dataset(carrier_list)
    
    src.data.update(new_src.data)
    
carrier_select = CheckboxGroup(labels=available_carriers,
                               active=[0])
carrier_select.on_change('active', update)

src = get_dataset([available_carriers[i] for i in carrier_select.active])
p = make_plot(src)

layout = row(carrier_select, p)

tab = Panel(child=layout, title='Histogram')
tabs = Tabs(tabs=[tab])

curdoc().add_root(tabs)