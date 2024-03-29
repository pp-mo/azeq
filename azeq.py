'''
Created on Dec 18, 2012

@author: itpp
'''

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import shapely.geometry as sgeom

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
USE_DPI = 150

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

def make_puffersphere_axes(projection_kwargs={}, **kwargs):
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
            'projection': AzEq(**projection_kwargs),
            'axisbg': 'black',
        })
    axes = plt.axes(_axes_normalised_rect, **kwargs)
    return axes

def save_figure_for_puffersphere(figure, filename, **savefig_kwargs):
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
    line_artists = []
    for longitude in np.linspace(-180.0, +180.0, n_meridians, endpoint=False):
        line_artists += [
            plt.plot([longitude, longitude], [-90.0, 90.0],
                     color=lon_color, transform=_proj_cyl)]
    for latitude in np.linspace(-90.0, +90.0, n_parallels, endpoint=False):
        line_artists += [
            plt.plot([-180.0, 180.0], [latitude, latitude],
                     color=lat_color, transform=_proj_cyl)]
    return line_artists

def simpletest(do_savefig=True, do_showfig=True, savefig_file='./puffer.png'):
    figure = make_puffersphere_figure()
    axes = make_puffersphere_axes()
    axes.stock_img()
    data = istk.global_pp()
    axes.coastlines()
    qplt.contour(data)
    draw_gridlines()
    #axes.coastlines()
    if do_savefig:
        save_figure_for_puffersphere(figure=plt.gcf(), filename=savefig_file)
    if do_showfig:
        plt.show()

def rotating_sequence(show_frames=True, save_frames=True, 
                      save_ani=False, show_ani=False,
                      ani_path='./puffer.mp4',
                      frames_basename='./puffer_frame_',
                      airtemp_cubes=None,
                      precip_cubes=None,
                      n_steps_round=20,
                      tilt_angle=21.7
                      ):
    plt.interactive(show_frames)
    figure = make_puffersphere_figure()
#    per_image_artists = []
    for (i_plt, lon_rotate) in enumerate(np.linspace(0.0, 360.0, n_steps_round, endpoint=False)):
        print 'rotate=', lon_rotate,' ...'
        axes = make_puffersphere_axes(
            projection_kwargs={'central_longitude': lon_rotate, 'central_latitude': tilt_angle})
        image = axes.stock_img()
        coast = axes.coastlines()
#        data = istk.global_pp()
        data = airtemp_cubes[i_plt]
        transparent_blue = (0.0, 0.0, 1.0, 0.25)
        transparent_red = (1.0, 0.0, 0.0, 0.25)
        cold_thresh = -10.0
        cold_fill = iplt.contourf(
              data,
              levels=[cold_thresh, cold_thresh],
              colors=[transparent_blue],
              extend='min')
        cold_contour = iplt.contour(
            data,
            levels=[cold_thresh], colors=['blue'],
            linestyles=['solid'])
        data = precip_cubes[i_plt]
        precip_thresh = 0.0001
        precip_fill = iplt.contourf(
            data,
            levels=[precip_thresh, precip_thresh],
            colors=[transparent_red],
            extend='max')
        precip_contour = iplt.contour(
            data,
            levels=[precip_thresh], colors=['red'],
            linestyles=['solid'])
        gridlines = draw_gridlines(n_meridians=6)
#        artists = []
#        artists += [coast]
#        artists += [image]
#        artists += cold_fill.collections
#        artists += precip_fill.collections
#        for gridline in gridlines:
#            artists += gridline
        if show_frames:
            plt.draw()
        if save_frames:
            save_path = frames_basename+str(i_plt)+'.png'
            save_figure_for_puffersphere(figure, save_path)
#        per_image_artists.append(artists)
        print '  ..done.'

#    if save_ani:
#        print 'Saving to {}...'.format(ani_path)
#        ani = animation.ArtistAnimation(
#            figure, per_image_artists,
#            interval=150, repeat=True, repeat_delay=500
#        )
#        ani.save(ani_path, writer='ffmpeg')
#
#    if show_ani:
#        print 'Showing...'
#        ani = animation.ArtistAnimation(
#            figure, per_image_artists,
#            interval=250, repeat=True, repeat_delay=5000,
##            blit=True
#        )
#        plt.show(block=True)


if __name__ == '__main__':
#    simpletest()
    # get some basic data
    airtemp_data, precip_data = iris.load_cubes('/data/local/dataZoo/PP/decadal/*.pp', ['air_temperature', 'precipitation_flux'])
    # create a rolling map from these
    n_frames = 12
#    i_images = [int(x) for x in np.linspace(0, airtemp_raw.shape[0], n_frames, endpoint=False)]
#    airtemp_data = airtemp_raw[i_images]
    airtemp_data = airtemp_data[0:n_frames+1]
    precip_data = precip_data[0:n_frames+1]
    units_degC = iris.unit.Unit('degC')
    airtemp_data.data = airtemp_data.units.convert(airtemp_data.data, units_degC)
    airtemp_data.units = units_degC
    rotating_sequence(airtemp_cubes=airtemp_data, precip_cubes=precip_data, n_steps_round=airtemp_data.shape[0])


#>>> for x in pf:
#...   plt.clf()
#...   plt.axes(projection=ccrs.PlateCarree());plt.gca().stock_img()
#...   iplt.contourf(x, levels=[0.0002,0.0002], extend='max', colors=[(1.0,0,0,0.2)])
#...   print raw_input()
