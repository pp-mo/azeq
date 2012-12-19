'''
Created on Dec 18, 2012

@author: itpp
'''

import numpy as np

import shapely.geometry as sgeom
import matplotlib.pyplot as plt

import iris
import iris.plot as iplt
import iris.quickplot as qplt
import cartopy.crs as ccrs
import iris.tests.stock as istk


# assumed radius of spherical earth in PROJ4 (pinched from code in pj_ellps.c)
EARTH_SPHERE_RADIUS = 6370997.0
EARTH_SPHERE_CIRCUMFERENCE = EARTH_SPHERE_RADIUS * 2.0 * np.pi


class AzEq(ccrs.Projection):
    # Attempt at defining Azimuthal Equidistant projection for Cartopy.
    #  -- mostly pinched from Gnomonic type etc.
    def __init__(self, central_latitude=90.0, central_longitude=0.0):
        proj4_params = {'proj': 'aeqd',
                        'lat_0': central_latitude,
                        'lon_0': central_longitude,
                        # NOTE: spherical assumption should work better for 
                        # this projection.
                        'ellps':'sphere'
        }
        super(AzEq, self).__init__(proj4_params)
        # Map limit is one-half earth circumference.
        # This is why 'ellps:sphere' is a good idea.
        self._max = 0.5*EARTH_SPHERE_CIRCUMFERENCE

    @property
    def boundary(self):
        # Copied -- don't really understand.
        return sgeom.Point(0, 0).buffer(self._max).exterior

    @property
    def threshold(self):
        # Copied -- don't really understand.
        # Seems to control the precision of drawn lines.
        # See in crs.py that this is typically -
        #   * 0.5 for degree-based projections
        #   * ~1e5-1e7 for metre-based projections (=100-10000km?)
        return 1e3

    @property
    def x_limits(self):
        # Copied -- don't really understand.  A square coordinate box?
        return (-self._max, self._max)

    @property
    def y_limits(self):
        # Copied -- don't really understand.  A square coordinate box?
        return (-self._max, self._max)


_proj_cyl = ccrs.PlateCarree()


def apply_dict_defaults(kwargs, defaults_dict):
    for (argname, value) in defaults_dict.iteritems():
        if not argname in kwargs:
            kwargs[argname] = value

# Properties of the PufferSphere
PUFFERSPHERE_FULL_WIDTH = 1400
PUFFERSPHERE_FULL_HEIGHT = 1050
PUFFERSPHERE_TOTAL_PIXELS = (PUFFERSPHERE_FULL_WIDTH, PUFFERSPHERE_FULL_HEIGHT)
PUFFERSPHERE_USED_WIDTH = 1050
PUFFERSPHERE_USED_HEIGHT = 1050

# Set "dpi".
# In principle arbitrary, as results are rescaled from Figure 'inch' sizes.
# In practice controls *default linewidths* (as in pixels).
USE_DPI = 200

# Size of main figure.
_figure_inches = [x*1.0/USE_DPI for x in PUFFERSPHERE_TOTAL_PIXELS]

# Normalised corners of the useful area within the main figure 
# (left,bottom,width,height).
_margin_pixels = (PUFFERSPHERE_FULL_WIDTH - PUFFERSPHERE_USED_WIDTH) / 2
_width_norm_scale = 1.0 / PUFFERSPHERE_FULL_WIDTH
_axes_normalised_rect = [
    _margin_pixels * _width_norm_scale,
    0.0,
    PUFFERSPHERE_USED_WIDTH * _width_norm_scale,
    1.0
]

def make_puffersphere_figure(**kwargs):
    """
    Init a pyplot.Figure for full-globe spherical projection.

    From : http://wiki.openstreetmap.org/wiki/Pufferfish_Display ...
      "A pre-warped image consists of a 1050x1050 pixel square image with a 75 pixal black band on either side. With the north pole at in the centre."
    """
    # Create a figure with useful defaults
    apply_dict_defaults(
        kwargs,
        {
            'figsize': _figure_inches,
            'dpi': USE_DPI,
            'facecolor': 'black',
            'edgecolor': None,
        })
    figure = plt.figure(**kwargs)
    return figure

def make_puffersphere_axes(**kwargs):
    """
    Create a pyplot.Axes for full-globe spherical projection.

    Uses Azimuthal Equidistant projection, and 
    """
    # Create a central global-map axes to plot on.
    apply_dict_defaults(
        kwargs,
        {
#            'figure': figure,
#            'rect': _axes_normalised_rect,
# NOTE: for plt.axes() : 'figure' is implicit, 'rect' is an arg, not kwarg.
            'frameon': False,
            'projection': AzEq(),
            'axisbg': 'black',
        })
    axes = plt.axes(_axes_normalised_rect, **kwargs)
    return axes

def plot_figure_for_puffersphere(figure, filename, **savefig_kwargs):
    """
    Plot the given Figure in a suitable form for the puffersphere.
    """
#    # A list of modified defaults
#    apply_dict_defaults(
#        savefig_kwargs,
#        {
#            'format': 'png',
#        })
    # For correct results, must re-assert dpi and facecolor?
    figure.savefig(
        filename,
        dpi=USE_DPI,
        facecolor='black'
    )

def draw_gridlines(n_meridians=12, n_parallels=8, lon_color='#180000', lat_color='#000018'):
    for longitude in np.linspace(-180.0, +180.0, n_meridians):
        plt.plot([longitude, longitude], [-90.0, 90.0], color=lon_color, transform=_proj_cyl)
    for latitude in np.linspace(-90.0, +90.0, n_parallels):
        plt.plot([-180.0, 180.0], [latitude, latitude], color=lat_color, transform=_proj_cyl)


#axes = plt.axes(projection=AzEq(central_latitude=52.0, central_longitude=0.0))
#axes = plt.axes(projection=AzEq())
    #
    # NOTE: A central *South* pole works ok, other places don't do well, giving
    # confusion over contouring etc -- even crossing contours ??
    #

#axes = plt.axes(projection=ccrs.PlateCarree())
#axes = plt.axes(projection=ccrs.Gnomonic(central_latitude=60.0))
def simpletest(do_savefig=True, do_showfig=True, savefig_file='./puffer.png'):
    figure = make_puffersphere_figure()
    axes = make_puffersphere_axes(frameon=True)
    axes.stock_img()
    data = istk.global_pp()
    axes.coastlines()
    qplt.contour(data)
    draw_gridlines()
    #axes.coastlines()
    if do_savefig:
        plot_figure_for_puffersphere(figure=plt.gcf(), filename=savefig_file)
    if do_showfig:
        plt.show()

def rotating_sequence(do_savefig=True, do_showfig=True, savefig_file='./puffer.png'):
    figure = make_puffersphere_figure()
    axes = make_puffersphere_axes(frameon=True)
    axes.stock_img()
    data = istk.global_pp()
    axes.coastlines()
    qplt.contour(data)
    draw_gridlines()
    if do_savefig:
        plot_figure_for_puffersphere(figure=plt.gcf(), filename=savefig_file)
    if do_showfig:
        plt.show()


if __name__ == '__main__':
    simpletest()
