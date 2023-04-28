import ee
import altair as alt
from ee_jupyter.colab import set_colab_output_cell_height
from ee_jupyter.ipyleaflet import Map
from ee_jupyter.ipyleaflet import Inspector
from ee_jupyter.layout import MapWithInspector
import ipyleaflet
import ipywidgets as widgets
from IPython.display import HTML
import math
import pandas as pd
from pprint import pprint  # for pretty printing

ee.Initialize()

location_lonlat= ( 75.979404,11.798852)
map_init_params = {
    'center': list(reversed(location_lonlat)), # <lat,lon> ordering
    'zoom': 10
}
landsat8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA')
point=ee.Geometry.Point( 75.979404,11.798852)
landsat_rgb_viz={'bands':['B4','B3','B2'],'min':0.0,'max':0.3}
temporalFiltered=landsat8.filterDate('2016-01-01','2016-12-31').filterBounds(point)
spacialFiltered=temporalFiltered.filterBounds(point)
mediana=temporalFiltered.median()
hansenImage=ee.Image("UMD/hansen/global_forest_change_2021_v1_9")
datamask=hansenImage.select("datamask")
mask=datamask.eq(1)
def add_ndvi(image):
    ndvi=image.normalizedDifference(['B5','B4']).rename('NDVI')
    return image.addBands(ndvi)
image_collection=landsat8.filterDate('2016-01-01','2016-12-31').filterBounds(point)
xy=image_collection.map(add_ndvi)

ndvi_vis_arams={'bands':'NDVI','min':-1,'max':1,'palette':['blue','yellow','green']}
import folium
def add_ee_layer(self, ee_image_object,vis_params,name):
    map_id_dict=ee.Image(ee_image_object).getMapId(vis_params)
    folium.raster_layers.TileLayer(
    tiles=map_id_dict['tile_fetcher'].url_format,
        attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
        name=name,
        overlay=True,
        control=True
    ).add_to(self)
folium.Map.add_ee_layer=add_ee_layer
my_map=folium.Map(( 11.798852,75.979404),zoom_start=10)
my_map.add_ee_layer(xy.qualityMosaic('NDVI').updateMask(mask),ndvi_vis_arams,'land cover')
my_map.add_child(folium.LayerControl())
from flask import Flask
app=Flask(__name__)
@app.route("/")
def fol():
    return my_map.get_root().render()



