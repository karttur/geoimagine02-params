"""
params
==========================================

Package belonging to Karttur´s GeoImagine Framework.

Author
------
Thomas Gumbricht (thomas.gumbricht@karttur.com)

"""
from .version import __version__, VERSION, metadataD
from params.paramsjson import JsonParams, Struct, Composition
from .timestep import TimeSteps
from .layers import VectorLayer, RasterLayer, RegionLayer, LayerCommon