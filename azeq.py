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
        # This is why 'sphere' is a good idea.
        self._max = 0.5*EARTH_SPHERE_CIRCUMFERENCE

    @property
    def boundary(self):
        # Copied -- don't understand.
        return sgeom.Point(0, 0).buffer(self._max).exterior

    @property
    def threshold(self):
        # Copied -- don't understand.
        # See in crs.py that this is typically -
        #   * 0.5 for degree-based projections
        #   * ~1e5-1e7 for metre-based projections (=100-10000km?)
        return 1e3

    @property
    def x_limits(self):
        # Copied -- don't understand.  Presumably a square coordinate box?
        return (-self._max, self._max)

    @property
    def y_limits(self):
        # Copied -- don't understand.  Presumably a square coordinate box?
        return (-self._max, self._max)


_proj_cyl = ccrs.PlateCarree()

def draw_grid(nx=12, ny=8):
    lats = np.linspace(-90.0, +90.0, ny)
    lons = np.linspace(-180.0, +180.0, nx)
    for ix in range(nx):
        plt.plot([lons[ix], lons[ix]], [-90.0, 90.0], color='red', transform=_proj_cyl)
    for iy in range(ny):
        plt.plot([-180.0, 180.0], [lats[iy], lats[iy]], color='blue', transform=_proj_cyl)

#ax = plt.axes(projection=AzEq(central_latitude=52.0, central_longitude=0.0))
ax = plt.axes(projection=AzEq(central_latitude=90.0, central_longitude=0.0))
    #
    # NOTE: A central *South* pole works ok, other places don't do well, giving
    # confusion over contouring etc -- even crossing contours ??
    #

#ax = plt.axes(projection=ccrs.PlateCarree())
#ax = plt.axes(projection=ccrs.Gnomonic(central_latitude=60.0))
ax.stock_img()
data = istk.global_pp()
ax.coastlines()
qplt.contour(data)
draw_grid()
#ax.coastlines()
plt.show()
