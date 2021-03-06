#!/usr/bin/env python
"""
@package ion_functions.data.adcp_functions
@file ion_functions/data/adcp_functions.py
@author Christopher Wingard
@brief Module containing ADCP related data-calculations.
"""
import numpy as np
from ion_functions.data.generic_functions import magnetic_declination


# Wrapper functions to create the VELPROF L1 data products for instruments
# programmed in beam coordinates by RSN (ADCPS-I,K and ADCPT-B,D,E)
def adcp_beam_eastward(b1, b2, b3, b4, h, p, r, vf, lat, lon, z, dt):
    """
    Description:

        Wrapper function to compute the Eastward Velocity Profile (VELPROF-VLE)
        from beam coordinate transformed velocity profiles as defined in the
        Data Product Specification for Velocity Profile and Echo Intensity -
        DCN 1341-00750.

    Implemented by:

        2013-04-10: Christopher Wingard. Initial code.
        2014-02-03: Christopher Wingard. Formatting and adjusting to use
                    magnetic declination values calculated use the WMM 2010.
        2014-04-04: Russell Desiderio. Optimized code performance by replacing
                    the for loops previously used to calculate 2D and 3D
                    vectorized coordinate transformations with calls to
                    np.einsum (numpy Einstein summation function).
        2014-06-25: Christopher Wingard. Edited to account for units of
                    heading, pitch, roll and depth

    Usage:

        uu_cor = adcp_beam_eastward(b1, b2, b3, b4, h, p, r, vf, lat, lon, z, dt)

            where

        uu_corr = east velocity profiles in Earth coordinates corrected for the
                  magnetic declination (VELPROF-VLE_L1) [m s-1]

        b1 = "beam 1" velocity profiles in beam coordinates (VELPROF-B1_L0) [mm s-1]
        b2 = "beam 2" velocity profiles in beam coordinates (VELPROF-B2_L0) [mm s-1]
        b3 = "beam 3" velocity profiles in beam coordinates (VELPROF-B3_L0) [mm s-1]
        b4 = "beam 4" velocity profiles in beam coordinates (VELPROF-B4_L0) [mm s-1]
        h = instrument's uncorrected magnetic heading [cdegrees]
        p = instrument pitch [cdegrees]
        r = instrument roll [cdegrees]
        vf = instrument's vertical orientation (0 = downward looking and
            1 = upward looking)
        lat = instrument's deployment latitude [decimal degrees]
        lon = instrument's deployment longitude [decimal degrees]
        z = instrument's pressure sensor reading (depth) [daPa]
        dt = sample date and time value [seconds since 1900-01-01]
    """
    # force shapes of inputs to arrays of the correct dimensions
    b1 = np.atleast_2d(b1)
    b2 = np.atleast_2d(b2)
    b3 = np.atleast_2d(b3)
    b4 = np.atleast_2d(b4)
    h = np.atleast_1d(h) / 100.  # scale cdegrees input to degrees
    p = np.atleast_1d(p) / 100.  # scale cdegrees input to degrees
    r = np.atleast_1d(r) / 100.  # scale cdegrees input to degrees
    vf = np.atleast_1d(vf)
    z = np.atleast_1d(z) / 1000.  # scale daPa depth input to dbar
    z = z * 1.019716  # use a simple approximation to calculate depth in m
    lat = np.atleast_1d(lat)
    lon = np.atleast_1d(lon)
    dt = np.atleast_1d(dt)

    # compute the beam to instrument transform
    u, v, w, _ = adcp_beam2ins(b1, b2, b3, b4)

    # compute the instrument to earth beam transform
    uu, vv, _ = adcp_ins2earth(u, v, w, h, p, r, vf)

    # compute the magnetic variation, and ...
    theta = magnetic_declination(lat, lon, dt, z)

    # ... correct for it
    uu_cor, _ = magnetic_correction(theta, uu, vv)

    # scale velocity to m/s
    uu_cor = uu_cor / 1000.  # mm/s -> m/s

    # return the Eastward Velocity Profile
    return uu_cor


def adcp_beam_northward(b1, b2, b3, b4, h, p, r, vf, lat, lon, z, dt):
    """
    Description:

        Wrapper function to compute the Northward Velocity Profile (VELPROF-VLN)
        from beam coordinate transformed velocity profiles as defined in the
        Data Product Specification for Velocity Profile and Echo Intensity -
        DCN 1341-00750.

    Implemented by:

        2013-04-10: Christopher Wingard. Initial code.
        2014-02-03: Christopher Wingard. Formatting and adjusting to use
                    magnetic declination values calculated use the WMM 2010.
        2014-03-28: Russell Desiderio. Corrected documentation only.
        2014-04-04: Russell Desiderio. Optimized code performance by replacing
                    the for loops previously used to calculate 2D and 3D
                    vectorized coordinate transformations with calls to
                    np.einsum (numpy Einstein summation function).
        2014-06-25: Christopher Wingard. Edited to account for units of
                    heading, pitch, roll and depth

    Usage:

        vv_cor = adcp_beam_northward(b1, b2, b3, b4, h, p, r, vf, lat, lon, z, dt)

            where

        vv_corr = north velocity profiles in Earth coordinates corrected for the
                  magnetic declination (VELPROF-VLN_L1) [m s-1]

        b1 = "beam 1" velocity profiles in beam coordinates (VELPROF-B1_L0) [mm s-1]
        b2 = "beam 2" velocity profiles in beam coordinates (VELPROF-B2_L0) [mm s-1]
        b3 = "beam 3" velocity profiles in beam coordinates (VELPROF-B3_L0) [mm s-1]
        b4 = "beam 4" velocity profiles in beam coordinates (VELPROF-B4_L0) [mm s-1]
        h = instrument's uncorrected magnetic heading [cdegrees]
        p = instrument pitch [cdegrees]
        r = instrument roll [cdegrees]
        vf = instrument's vertical orientation (0 = downward looking and
            1 = upward looking)
        lat = instrument's deployment latitude [decimal degrees]
        lon = instrument's deployment longitude [decimal degrees]
        z = instrument's pressure sensor reading (depth) [daPa]
        dt = sample date and time value [seconds since 1900-01-01]
    """
    # force shapes of inputs to arrays of the correct dimensions
    b1 = np.atleast_2d(b1)
    b2 = np.atleast_2d(b2)
    b3 = np.atleast_2d(b3)
    b4 = np.atleast_2d(b4)
    h = np.atleast_1d(h) / 100.  # scale cdegrees input to degrees
    p = np.atleast_1d(p) / 100.  # scale cdegrees input to degrees
    r = np.atleast_1d(r) / 100.  # scale cdegrees input to degrees
    vf = np.atleast_1d(vf)
    z = np.atleast_1d(z) / 1000.  # scale daPa depth input to dbar
    z = z * 1.019716  # use a simple approximation to calculate depth in m
    lat = np.atleast_1d(lat)
    lon = np.atleast_1d(lon)
    dt = np.atleast_1d(dt)

    # compute the beam to instrument transform
    u, v, w, _ = adcp_beam2ins(b1, b2, b3, b4)

    # compute the instrument to earth beam transform
    uu, vv, _ = adcp_ins2earth(u, v, w, h, p, r, vf)

    # compute the magnetic variation, and ...
    theta = magnetic_declination(lat, lon, dt, z)

    # ... correct for it
    _, vv_cor = magnetic_correction(theta, uu, vv)

    # scale velocity to m/s
    vv_cor = vv_cor / 1000.  # mm/s -> m/s

    # return the Northward Velocity Profile
    return vv_cor


def adcp_beam_vertical(b1, b2, b3, b4, h, p, r, vf):
    """
    Description:

        Wrapper function to compute the Upward Velocity Profile (VELPROF-VLU)
        from beam coordinate transformed velocity profiles as defined in the
        Data Product Specification for Velocity Profile and Echo Intensity -
        DCN 1341-00750.

    Implemented by:

        2013-04-10: Christopher Wingard. Initial code.
        2014-02-03: Christopher Wingard. Formatting and adjusting to use
                    magnetic declination values calculated using the WMM 2010.
        2014-04-04: Russell Desiderio. Optimized code performance by replacing
                    the for loops previously used to calculate 2D and 3D
                    vectorized coordinate transformations with calls to
                    np.einsum (numpy Einstein summation function).
        2014-06-25: Christopher Wingard. Edited to account for units of
                    heading, pitch, roll and depth

    Usage:

        ww_cor = adcp_beam_vertical(b1, b2, b3, b4, h, p, r, vf)

            where

        ww_cor = vertical velocity profiles (VELPROF-VLU_L1) [m s-1]

        b1 = "beam 1" velocity profiles in beam coordinates (VELPROF-B1_L0) [mm s-1]
        b2 = "beam 2" velocity profiles in beam coordinates (VELPROF-B2_L0) [mm s-1]
        b3 = "beam 3" velocity profiles in beam coordinates (VELPROF-B3_L0) [mm s-1]
        b4 = "beam 4" velocity profiles in beam coordinates (VELPROF-B4_L0) [mm s-1]
        h = instrument's uncorrected magnetic heading [cdegrees]
        p = instrument pitch [cdegrees]
        r = instrument roll [cdegrees]
        vf = instrument's vertical orientation (0 = downward looking and
            1 = upward looking)
    """
    # force shapes of inputs to arrays of the correct dimensions
    b1 = np.atleast_2d(b1)
    b2 = np.atleast_2d(b2)
    b3 = np.atleast_2d(b3)
    b4 = np.atleast_2d(b4)
    h = np.atleast_1d(h) / 100.  # scale cdegrees input to degrees
    p = np.atleast_1d(p) / 100.  # scale cdegrees input to degrees
    r = np.atleast_1d(r) / 100.  # scale cdegrees input to degrees
    vf = np.atleast_1d(vf)

    # compute the beam to instrument transform
    u, v, w, _ = adcp_beam2ins(b1, b2, b3, b4)

    # compute the instrument to earth beam transform
    _, _, ww = adcp_ins2earth(u, v, w, h, p, r, vf)

    # scale upward velocity to m/s
    ww = ww / 1000.  # mm/s -> m/s

    # return the Upward Velocity Profile
    return ww


def adcp_beam_error(b1, b2, b3, b4):
    """
    Description:

        Wrapper function to compute the Error Velocity Profile (VELPROF-ERR)
        from beam coordinate transformed velocity profiles as defined in the
        Data Product Specification for Velocity Profile and Echo Intensity -
        DCN 1341-00750.

    Implemented by:

        2013-04-10: Christopher Wingard. Initial code.

    Usage:

        ww_cor = adcp_beam_error(b1, b2, b3, b4)

            where

        e = Error velocity profiles (VELPROF-ERR_L1) [m s-1]

        b1 = "beam 1" velocity profiles in beam coordinates (VELPROF-B1_L0) [mm s-1]
        b2 = "beam 2" velocity profiles in beam coordinates (VELPROF-B2_L0) [mm s-1]
        b3 = "beam 3" velocity profiles in beam coordinates (VELPROF-B3_L0) [mm s-1]
        b4 = "beam 4" velocity profiles in beam coordinates (VELPROF-B4_L0) [mm s-1]
    """
    # force input arrays to 2d shape
    b1 = np.atleast_2d(b1)
    b2 = np.atleast_2d(b2)
    b3 = np.atleast_2d(b3)
    b4 = np.atleast_2d(b4)

    # compute the beam to instrument transform
    _, _, _, e = adcp_beam2ins(b1, b2, b3, b4)

    # scale error velocity to m/s
    e = e / 1000.   # mm/s

    # return the Error Velocity Profile
    return e


# Wrapper functions to create the VELPROF L1 data products for instruments
# programmed in Earth coordinates by CGSN (Pioneer and Endurance) (ADCPA,
# ADCPS-J,L,N and ADCPT-C,F,G,M)
def adcp_earth_eastward(u, v, z, lat, lon, dt):
    """
    Description:

        Wrapper function to compute the Eastward Velocity Profile (VELPROF-VLE)
        from Earth coordinate transformed velocity profiles as defined in the
        Data Product Specification for Velocity Profile and Echo Intensity -
        DCN 1341-00750.

    Implemented by:

        2013-04-10: Christopher Wingard. Initial code.
        2014-02-03: Christopher Wingard. Formatting and adjusting to use
                    magnetic declination values calculated use the WMM 2010.
        2014-04-04: Russell Desiderio. Optimized code performance by replacing
                    the for loops previously used to calculate 2D and 3D
                    vectorized coordinate transformations with calls to
                    np.einsum (numpy Einstein summation function).
        2014-06-25: Christopher Wingard. Edited to account for units of
                    heading, pitch, roll and depth

    Usage:

        uu_cor = adcp_earth_eastward(u, v, z, lat, lon, dt)

            where

        uu_cor = eastward velocity profiles in Earth coordinates corrected for
                 the magnetic declination (VELPROF-VLE_L1) [m s-1]

        u = Eastward velocity profiles (VELPROF-VLE_L0) [mm s-1]
        v = Northward velocity profiles (VELPROF-VLN_L0) [mm s-1]
        z = instrument's pressure sensor reading (depth) [daPa]
        lat = instrument's deployment latitude [decimal degrees]
        lon = instrument's deployment longitude [decimal degrees]
        dt = sample date and time value [seconds since 1900-01-01]
    """
    # force shapes of inputs to arrays
    u = np.atleast_2d(u)
    v = np.atleast_2d(v)
    z = np.atleast_1d(z) / 1000.  # scale daPa depth input to dbar
    z = z * 1.019716  # use a simple approximation to calculate depth in m
    lat = np.atleast_1d(lat)
    lon = np.atleast_1d(lon)
    dt = np.atleast_1d(dt)

    # compute the magnetic variation, and ...
    theta = magnetic_declination(lat, lon, dt, z)

    # ... correct for it
    uu_cor, _ = magnetic_correction(theta, u, v)

    # scale velocity to m/s
    uu_cor = uu_cor / 1000.  # mm/s -> m/s

    # return the Eastward Velocity Profile
    return uu_cor


def adcp_earth_northward(u, v, z, lat, lon, dt):
    """
    Description:

        Wrapper function to compute the Northward Velocity Profile (VELPROF-VLN)
        from Earth coordinate transformed velocity profiles as defined in the
        Data Product Specification for Velocity Profile and Echo Intensity -
        DCN 1341-00750.

    Implemented by:

        2013-04-10: Christopher Wingard. Initial code.
        2014-02-03: Christopher Wingard. Formatting and adjusting to use
                    magnetic declination values calculated use the WMM 2010.
        2014-04-04: Russell Desiderio. Optimized code performance by replacing
                    the for loops previously used to calculate 2D and 3D
                    vectorized coordinate transformations with calls to
                    np.einsum (numpy Einstein summation function).
        2014-06-25: Christopher Wingard. Edited to account for units of
                    heading, pitch, roll and depth

    Usage:

        vv_cor = adcp_earth_northward(u, v, z, lat, lon, dt)

            where

        vv_cor = northward velocity profiles in Earth coordinates corrected for
                 the magnetic declination (VELPROF-VLN_L1) [m s-1]

        u = Eastward velocity profiles (VELPROF-VLE_L0) [mm s-1]
        v = Northward velocity profiles (VELPROF-VLN_L0) [mm s-1]
        z = instrument's pressure sensor reading (depth) [daPa]
        lat = instrument's deployment latitude [decimal degrees]
        lon = instrument's deployment longitude [decimal degrees]
        dt = sample date and time value [seconds since 1900-01-01]
    """
    # force shapes of inputs to arrays
    u = np.atleast_2d(u)
    v = np.atleast_2d(v)
    z = np.atleast_1d(z) / 1000.  # scale daPa depth input to dbar
    z = z * 1.019716  # use a simple approximation to calculate depth in m
    lat = np.atleast_1d(lat)
    lon = np.atleast_1d(lon)
    dt = np.atleast_1d(dt)

    # compute the magnetic variation, and ...
    theta = magnetic_declination(lat, lon, dt, z)

    # ... correct for it
    _, vv_cor = magnetic_correction(theta, u, v)

    # scale velocity to m/s
    vv_cor = vv_cor / 1000.  # mm/s -> m/s

    # return the Northward Velocity Profile
    return vv_cor


def adcp_earth_vertical(w):
    """
    Description:

        Wrapper function to compute the Upward Velocity Profile (VELPROF-VLU)
        from Earth coordinate transformed velocity profiles as defined in the
        Data Product Specification for Velocity Profile and Echo Intensity -
        DCN 1341-00750.

    Implemented by:

        2014-06-25: Christopher Wingard. Initial code.

    Usage:

        w_scl = adcp_earth_vertical(w)

            where

        w_scl = scaled upward velocity profiles in Earth coordinates
                (VELPROF-VLN_L1) [m s-1]

        w = upward velocity profiles (VELPROF-VLU_L0) [mm s-1]
    """
    # scale velocity to m/s
    w_scl = w / 1000.  # mm/s -> m/s

    # return the Upward Velocity Profile
    return w_scl


def adcp_earth_error(e):
    """
    Description:

        Wrapper function to compute the Error Velocity Profile (VELPROF-ERR)
        from Earth coordinate transformed velocity profiles as defined in the
        Data Product Specification for Velocity Profile and Echo Intensity -
        DCN 1341-00750.

    Implemented by:

        2014-06-25: Christopher Wingard. Initial code.

    Usage:

        e_scl = adcp_earth_vertical(w)

            where

        e_scl = scaled error velocity profiles in Earth coordinates
                (VELPROF-ERR_L1) [m s-1]

        e = error velocity profiles (VELPROF-ERR_L0) [mm s-1]
    """
    # scale velocity to m/s
    e_scl = e / 1000.  # mm/s -> m/s

    # return the scaled Error Velocity Profile
    return e_scl


# Compute the VELTURB_L1 data products for the VADCP instrument deployed by RSN.
def vadcp_beam_eastward(b1, b2, b3, b4, h, p, r, vf, lat, lon, z, dt):
    """
    Description:

        Wrapper function to compute the Eastward Velocity Profile (VELTURB-VLE)
        from beam coordinate transformed velocity profiles as defined in the
        Data Product Specification for Turbulent Velocity Profile and Echo Intensity -
        DCN 1341-00760.

    Implemented by:

        2014-06-25: Christopher Wingard. Initial code, based on existing ADCP

    Usage:

        uu_cor = vadcp_beam_eastward(b1, b2, b3, b4, h, p, r, vf, lat, lon, z, dt)

            where

        uu_cor = east velocity profiles in Earth coordinates corrected for the
                  magnetic declination (VELTURB-VLE_L1) [m s-1]

        b1 = "beam 1" velocity profiles in beam coordinates (VELTURB-B1_L0) [mm s-1]
        b2 = "beam 2" velocity profiles in beam coordinates (VELTURB-B2_L0) [mm s-1]
        b3 = "beam 3" velocity profiles in beam coordinates (VELTURB-B3_L0) [mm s-1]
        b4 = "beam 4" velocity profiles in beam coordinates (VELTURB-B4_L0) [mm s-1]
        h = instrument's uncorrected magnetic heading [cdegrees]
        p = instrument pitch [cdegrees]
        r = instrument roll [cdegrees]
        vf = instrument's vertical orientation (0 = downward looking and
            1 = upward looking)
        lat = instrument's deployment latitude [decimal degrees]
        lon = instrument's deployment longitude [decimal degrees]
        z = instrument's pressure sensor reading (depth) [daPa]
        dt = sample date and time value [seconds since 1900-01-01]
    """
    # force shapes of inputs to arrays of the correct dimensions
    b1 = np.atleast_2d(b1)
    b2 = np.atleast_2d(b2)
    b3 = np.atleast_2d(b3)
    b4 = np.atleast_2d(b4)
    h = np.atleast_1d(h) / 100.  # scale cdegrees input to degrees
    p = np.atleast_1d(p) / 100.  # scale cdegrees input to degrees
    r = np.atleast_1d(r) / 100.  # scale cdegrees input to degrees
    vf = np.atleast_1d(vf)
    z = np.atleast_1d(z) / 1000.  # scale daPa depth input to dbar
    z = z * 1.019716  # use a simple approximation to calculate depth in m
    lat = np.atleast_1d(lat)
    lon = np.atleast_1d(lon)
    dt = np.atleast_1d(dt)

    # compute the beam to instrument transform
    u, v, w, _ = adcp_beam2ins(b1, b2, b3, b4)

    # compute the instrument to earth beam transform
    uu, vv, _ = adcp_ins2earth(u, v, w, h, p, r, vf)

    # compute the magnetic variation, and ...
    theta = magnetic_declination(lat, lon, dt, z)

    # ... correct for it
    uu_cor, _ = magnetic_correction(theta, uu, vv)

    # scale velocity to m/s
    uu_cor = uu_cor / 1000.  # mm/s -> m/s

    # return the Eastward Velocity Profile
    return uu_cor


def vadcp_beam_northward(b1, b2, b3, b4, h, p, r, vf, lat, lon, z, dt):
    """
    Description:

        Wrapper function to compute the Northward Velocity Profile
        (VELTURB-VLN) from beam coordinate transformed velocity profiles as
        defined in the Data Product Specification for Turbulent Velocity
        Profile and Echo Intensity - DCN 1341-00760.

    Implemented by:

        2014-06-25: Christopher Wingard. Initial code, based on existing ADCP

    Usage:

        vv_cor = vadcp_beam_northward(b1, b2, b3, b4, h, p, r, vf, lat, lon, z, dt)

            where

        vv_cor = north velocity profiles in Earth coordinates corrected for the
                  magnetic declination (VELTURB-VLN_L1) [m s-1]

        b1 = "beam 1" velocity profiles in beam coordinates (VELTURB-B1_L0) [mm s-1]
        b2 = "beam 2" velocity profiles in beam coordinates (VELTURB-B2_L0) [mm s-1]
        b3 = "beam 3" velocity profiles in beam coordinates (VELTURB-B3_L0) [mm s-1]
        b4 = "beam 4" velocity profiles in beam coordinates (VELTURB-B4_L0) [mm s-1]
        h = instrument's uncorrected magnetic heading [cdegrees]
        p = instrument pitch [cdegrees]
        r = instrument roll [cdegrees]
        vf = instrument's vertical orientation (0 = downward looking and
            1 = upward looking)
        lat = instrument's deployment latitude [decimal degrees]
        lon = instrument's deployment longitude [decimal degrees]
        z = instrument's pressure sensor reading (depth) [dm]
        dt = sample date and time value [seconds since 1900-01-01]
    """
    # force shapes of inputs to arrays of the correct dimensions
    b1 = np.atleast_2d(b1)
    b2 = np.atleast_2d(b2)
    b3 = np.atleast_2d(b3)
    b4 = np.atleast_2d(b4)
    h = np.atleast_1d(h) / 100.  # scale cdegrees input to degrees
    p = np.atleast_1d(p) / 100.  # scale cdegrees input to degrees
    r = np.atleast_1d(r) / 100.  # scale cdegrees input to degrees
    vf = np.atleast_1d(vf)
    z = np.atleast_1d(z) / 1000.  # scale daPa depth input to dbar
    z = z * 1.019716  # use a simple approximation to calculate depth in m
    lat = np.atleast_1d(lat)
    lon = np.atleast_1d(lon)
    dt = np.atleast_1d(dt)

    # compute the beam to instrument transform
    u, v, w, _ = adcp_beam2ins(b1, b2, b3, b4)

    # compute the instrument to earth beam transform
    uu, vv, _ = adcp_ins2earth(u, v, w, h, p, r, vf)

    # compute the magnetic variation, and ...
    theta = magnetic_declination(lat, lon, dt, z)

    # ... corect for it
    _, vv_cor = magnetic_correction(theta, uu, vv)

    # scale velocity to m/s
    vv_cor = vv_cor / 1000.  # mm/s -> m/s

    # return the Northward Velocity Profile
    return vv_cor


def vadcp_beam_vertical_est(b1, b2, b3, b4, h, p, r, vf):
    """
    Description:

        Wrapper function to compute the "estimated" Upward Velocity Profile
        (VELTURB-VLU) from the beam coordinate transformed velocity profiles as
        defined in the Data Product Specification for Turbulent Velocity
        Profile and Echo Intensity - DCN 1341-00760. This provides the
        traditional estimate of the vertical velocity component from a 4 beam
        solution, where each beam is facing outward at an angle (20 degrees)
        relative to the vertical.

    Implemented by:

        2014-06-25: Christopher Wingard. Initial code, based on existing ADCP

    Usage:

        ww_est = vadcp_beam_vertical_est(b1, b2, b3, b4, h, p, r, vf)

            where

        ww_est = estimated vertical velocity profiles in Earth coordinates
                 (VELTURB-W5_L1) [m s-1]

        b1 = "beam 1" velocity profiles in beam coordinates (VELTURB-B1_L0) [mm s-1]
        b2 = "beam 2" velocity profiles in beam coordinates (VELTURB-B2_L0) [mm s-1]
        b3 = "beam 3" velocity profiles in beam coordinates (VELTURB-B3_L0) [mm s-1]
        b4 = "beam 4" velocity profiles in beam coordinates (VELTURB-B4_L0) [mm s-1]
        h = instrument's uncorrected magnetic heading [cdegrees]
        p = instrument pitch [cdegrees]
        r = instrument roll [cdegrees]
        vf = instrument's vertical orientation (0 = downward looking and
            1 = upward looking)
    """
    # force shapes of inputs to arrays of the correct dimensions
    b1 = np.atleast_2d(b1)
    b2 = np.atleast_2d(b2)
    b3 = np.atleast_2d(b3)
    b4 = np.atleast_2d(b4)
    h = np.atleast_1d(h) / 100.  # scale cdegrees input to degrees
    p = np.atleast_1d(p) / 100.  # scale cdegrees input to degrees
    r = np.atleast_1d(r) / 100.  # scale cdegrees input to degrees
    vf = np.atleast_1d(vf)

    # compute the beam to instrument transform
    u, v, w, _ = adcp_beam2ins(b1, b2, b3, b4)

    # compute the instrument to earth beam transform
    _, _, ww = adcp_ins2earth(u, v, w, h, p, r, vf)

    # scale upward velocity to m/s
    ww = ww / 1000.  # mm/s -> m/s

    # return the estimated Upward Velocity Profile
    return ww


def vadcp_beam_vertical_true(b1, b2, b3, b4, b5, h, p, r, vf):
    """
    Description:

        Wrapper function to compute the "true" Upward Velocity Profile
        (VELTURB-W5) from the beam coordinate transformed velocity profiles as
        defined in the Data Product Specification for Turbulent Velocity
        Profile and Echo Intensity - DCN 1341-00760. This is assumed to provide
        a better estimate of the true vertical velocity component, since beam 5
        is pointing directly up.

    Implemented by:

        2014-06-25: Christopher Wingard. Initial code, based on existing ADCP

    Usage:

        ww_true = vadcp_beam_northward(b1, b2, b3, b4, b5, h, p, r, vf)

            where

        ww_true = true vertical velocity profiles in Earth coordinates
                  (VELTURB-W5_L1) [m s-1]

        b1 = "beam 1" velocity profiles in beam coordinates (VELTURB-B1_L0) [mm s-1]
        b2 = "beam 2" velocity profiles in beam coordinates (VELTURB-B2_L0) [mm s-1]
        b3 = "beam 3" velocity profiles in beam coordinates (VELTURB-B3_L0) [mm s-1]
        b4 = "beam 4" velocity profiles in beam coordinates (VELTURB-B4_L0) [mm s-1]
        b5 = "beam 5" velocity profiles in beam coordinates (VELTURB-B5_L0) [mm s-1]
        h = instrument's uncorrected magnetic heading [cdegrees]
        p = instrument pitch [cdegrees]
        r = instrument roll [cdegrees]
        vf = instrument's vertical orientation (0 = downward looking and
            1 = upward looking)
    """
    # force shapes of inputs to arrays of the correct dimensions
    b1 = np.atleast_2d(b1)
    b2 = np.atleast_2d(b2)
    b3 = np.atleast_2d(b3)
    b4 = np.atleast_2d(b4)
    b5 = np.atleast_2d(b5)
    h = np.atleast_1d(h) / 100.  # scale cdegrees input to degrees
    p = np.atleast_1d(p) / 100.  # scale cdegrees input to degrees
    r = np.atleast_1d(r) / 100.  # scale cdegrees input to degrees
    vf = np.atleast_1d(vf)

    # compute the beam to instrument transform
    u, v, _, _ = adcp_beam2ins(b1, b2, b3, b4)

    # compute the instrument to earth beam transform
    _, _, ww = adcp_ins2earth(u, v, b5, h, p, r, vf)

    # scale upward velocity to m/s
    ww = ww / 1000.  # mm/s -> m/s

    # return the true Upward Velocity Profile
    return ww


def vadcp_beam_error(b1, b2, b3, b4):
    """
    Description:

        Wrapper function to compute the Error Velocity Profile (VELTURB-ERR)
        from the beam coordinate transformed velocity profiles as defined in
        the Data Product Specification for Turbulent Velocity Profile and Echo
        Intensity - DCN 1341-00760.

    Implemented by:

        2014-06-25: Christopher Wingard. Initial code, based on existing ADCP

    Usage:

        e = vadcp_beam_northward(b1, b2, b3, b4)

            where

        e = error velocity profiles (VELTURB-ERR_L1) [m s-1]

        b1 = "beam 1" velocity profiles in beam coordinates (VELTURB-B1_L0) [mm s-1]
        b2 = "beam 2" velocity profiles in beam coordinates (VELTURB-B2_L0) [mm s-1]
        b3 = "beam 3" velocity profiles in beam coordinates (VELTURB-B3_L0) [mm s-1]
        b4 = "beam 4" velocity profiles in beam coordinates (VELTURB-B4_L0) [mm s-1]
    """
    # force input arrays to 2d shape
    b1 = np.atleast_2d(b1)
    b2 = np.atleast_2d(b2)
    b3 = np.atleast_2d(b3)
    b4 = np.atleast_2d(b4)

    # compute the beam to instrument transform
    _, _, _, e = adcp_beam2ins(b1, b2, b3, b4)

    # scale error velocity to m/s
    e = e / 1000.   # mm/s

    # return the Error Velocity Profile
    return e


# Calculates bin depths tRDI ADCPs configured to output data using the PD0 and PD12 formats
def adcp_bin_depths(dist_first_bin, bin_size, num_bins, pressure, adcp_orientation, latitude):
    """
    Description:

        Calculates the center bin depths for PD0 and PD12 ADCP data. As defined
        in the Data Product Specification for Velocity Profile and Echo
        Intensity - DCN 1341-00750.

    Implemented by:

        2015-01-29: Craig Risien. Initial code.

    Usage:

        bin_depths = adcp_bin_depths(dist_first_bin, bin_size, num_bins, pressure,
                                    adcp_orientation, latitude)

            where

        bin_depths =  [meters]

        dist_first_bin = distance to the first ADCP bin [centimeters]
        bin_size = depth of each ADCP bin [centimeters]
        num_bins = number of ADCP bins [unitless]
        pressure = pressure at the sensor head [dPa]
        adcp_orientation = 1=upward looking or 0=downward looking [unitless]
        latitude = latitude of the instrument [degrees]

    References:

        OOI (2012). Data Product Specification for Velocity Profile and Echo
            Intensity. Document Control Number 1341-00750.
            https://alfresco.oceanobservatories.org/ (See: Company Home >> OOI
            >> Controlled >> 1000 System Level >>
            1341-00050_Data_Product_SPEC_VELPROF_OOI.pdf)
    """
    #Convert from cm to meters
    dist_first_bin = dist_first_bin / 100
    bin_size = bin_size / 100

    #Convert pressure from decapascal to decibar
    pressure = pressure * -1
    pressure_dbar = pressure / 1000

    #Calculate sensor depth using TEOS-10 toolbox z_from_p function
    sensor_depth = z_from_p(pressure, latitude)

    #Calculate bin depths for an upward looking ADCP
    #For the PD0 format the convention is 0 = downward looking, 1 = upward looking
    if adcp_orientation == 1:
        bin_depths = sensor_depth - (dist_first_bin + bin_size * np.arange(0, num_bins))
    #Otherwise the ADCP is downward looking.
    else:
        bin_depths = sensor_depth + (dist_first_bin + bin_size * np.arange(0, num_bins))

    return bin_depths


# Calculates bin depths tRDI ADCPs configured to output data using the PD8 format
def adcp_bin_depths_pd8(dist_first_bin, bin_size, num_bins, sensor_depth, adcp_orientation):
    """
    Description:

        Calculates the center bin depths for PD8 ADCP data. As defined
        in the Data Product Specification for Velocity Profile and Echo
        Intensity - DCN 1341-00750.

    Implemented by:

        2015-01-30: Craig Risien. Initial code.

    Usage:

        bin_depths_pd8 = adcp_bin_depths(dist_first_bin, bin_size, num_bins, sensor_depth,
                                    adcp_orientation)

            where

        bin_depths_pd8 =  [meters]

        dist_first_bin = distance to the first ADCP bin [centimeters]
        bin_size = depth of each ADCP bin [centimeters]
        num_bins = number of ADCP bins [unitless]
        sensor_depth = estimated depth at the sensor head [meters]
        adcp_orientation = 1=upward looking or 0=downward looking [unitless]

    References:

        OOI (2012). Data Product Specification for Velocity Profile and Echo
            Intensity. Document Control Number 1341-00750.
            https://alfresco.oceanobservatories.org/ (See: Company Home >> OOI
            >> Controlled >> 1000 System Level >>
            1341-00050_Data_Product_SPEC_VELPROF_OOI.pdf)
    """
    #Convert from cm to meters
    dist_first_bin = dist_first_bin / 100
    bin_size = bin_size / 100

    if sensor_depth < 0:
        sensor_depth = sensor_depth * -1

    #Calculate bin depths for an upward looking ADCP
    #Following the PD0 convention where 0 = downward looking, 1 = upward looking
    if adcp_orientation == 1:
        bin_depths_pd8 = sensor_depth - (dist_first_bin + bin_size * np.arange(0, num_bins))
    #Otherwise the ADCP is downward looking.
    else:
        bin_depths_pd8 = sensor_depth + (dist_first_bin + bin_size * np.arange(0, num_bins))

    return bin_depths_pd8


# Calculates ECHOINT_L1 for all tRDI ADCPs
def adcp_backscatter(raw, sfactor):
    """
    Description:

        Converts the echo intensity data from counts to dB using a factory
        specified scale factor (nominally 0.45 dB/count for the Workhorse
        family of ADCPs and 0.61 dB/count for the ExplorerDVL family). As
        defined in the Data Product Specification for Velocity Profile and Echo
        Intensity - DCN 1341-00750.

    Implemented by:

        2014-04-21: Christopher Wingard. Initial code.

    Usage:

        dB = adcp_backscatter(raw, sfactor)

            where

        dB = Relative Echo Intensity (ECHOINT_L1) [dB]

        raw = raw echo intensity (ECHOINT_L0) [count]
        sfactor = factory supplied scale factor, instrument and beam specific [dB/count]

    References:

        OOI (2012). Data Product Specification for Velocity Profile and Echo
            Intensity. Document Control Number 1341-00750.
            https://alfresco.oceanobservatories.org/ (See: Company Home >> OOI
            >> Controlled >> 1000 System Level >>
            1341-00050_Data_Product_SPEC_VELPROF_OOI.pdf)
    """
    if np.isscalar(sfactor) is False:
        sfactor = sfactor.reshape(sfactor.shape[0], 1)

    dB = raw * sfactor
    return dB


##### ADCP Beam to Earth Transforms and Magnetic Variation Corrections
def adcp_beam2ins(b1, b2, b3, b4):
    """
    Description:

        This function converts the Beam Coordinate transformed velocity
        profiles to the instrument coordinate system. The calculations are
        defined in the Data Product Specification for Velocity Profile and Echo
        Intensity - DCN 1341-00750.

    Implemented by:

        2013-04-10: Christopher Wingard. Initial code.

    Usage:

        u, v, w, e = adcp_beam2ins(b1, b2, b3, b4)

            where

        u = "east" velocity profiles in instrument coordinates [mm s-1]
        v = "north" velocity profiles in instrument coordinates [mm s-1]
        w = "vertical" velocity profiles in instrument coordinates [mm s-1]
        e = "error" velocity profiles [mm s-1]

        b1 = "beam 1" velocity profiles in beam coordinates [mm s-1]
        b2 = "beam 2" velocity profiles in beam coordinates [mm s-1]
        b3 = "beam 3" velocity profiles in beam coordinates [mm s-1]
        b4 = "beam 4" velocity profiles in beam coordinates [mm s-1]

    References:

        OOI (2012). Data Product Specification for Velocity Profile and Echo
            Intensity. Document Control Number 1341-00750.
            https://alfresco.oceanobservatories.org/ (See: Company Home >> OOI
            >> Controlled >> 1000 System Level >>
            1341-00050_Data_Product_SPEC_VELPROF_OOI.pdf)
    """
    theta = 20.0 / 180.0 * np.pi
    a = 1.0 / (2.0 * np.sin(theta))
    b = 1.0 / (4.0 * np.cos(theta))
    c = 1.0   # +1.0 for convex transducer head, -1 for concave
    d = a / np.sqrt(2.0)

    u = c * a * (b1 - b2)
    v = c * a * (b4 - b3)
    w = b * (b1 + b2 + b3 + b4)
    e = d * (b1 + b2 - b3 - b4)

    return (u, v, w, e)


def adcp_ins2earth(u, v, w, heading, pitch, roll, vertical):
    """
    Description:

        This function converts the Instrument Coordinate transformed velocity
        profiles to the Earth coordinate system. The calculation is defined in
        the Data Product Specification for Velocity Profile and Echo Intensity
        - DCN 1341-00750.

    Implemented by:

        2013-04-10: Christopher Wingard. Initial code.
        2014-04-04: Russell Desiderio. Optimized code performance by replacing the for
                    loops previously used to calculate vectorized matrix multiplication
                    products with calls to np.einsum (numpy Einstein summation function).

    Usage:

        uu, vu, ww = adcp_ins2earth(u, v, w, heading, pitch, roll, vertical)

            where

        uu = "east" velocity profiles in earth coordinates [mm s-1]
        vv = "north" velocity profiles in earth coordinates [mm s-1]
        ww = "vertical" velocity profiles in earth coordinates [mm s-1]

        u = east velocity profiles in instrument coordinates [mm s-1]
        v = north velocity profiles in instrument coordinates [mm s-1]
        w = vertical velocity profiles in instrument coordinates [mm s-1]
        heading = instrument's uncorrected magnetic heading [degrees]
        pitch = instrument pitch [degrees]
        roll = instrument roll [degrees]
        vertical = instrument's vertical orientation (0 = downward looking and
            1 = upward looking)

    References:

        OOI (2012). Data Product Specification for Velocity Profile and Echo
            Intensity. Document Control Number 1341-00750.
            https://alfresco.oceanobservatories.org/ (See: Company Home >> OOI
            >> Controlled >> 1000 System Level >>
            1341-00050_Data_Product_SPEC_VELPROF_OOI.pdf)
    """
    # insure we are dealing with array inputs
    u = np.atleast_2d(u)
    v = np.atleast_2d(v)
    w = np.atleast_2d(w)

    heading = np.atleast_1d(heading)
    pitch = np.atleast_1d(pitch)
    roll = np.atleast_1d(roll)
    vertical = np.atleast_1d(vertical)

    # if the unit is oriented looking up, add 180 degrees
    mask = (vertical == 1)
    R = roll + (180.0 * mask)

    # roll
    Rrad = np.radians(R)
    cos_R = np.cos(Rrad)
    sin_R = np.sin(Rrad)
    # heading
    Hrad = np.radians(heading)
    cos_H = np.cos(Hrad)
    sin_H = np.sin(Hrad)
    # pitch
    t1rad = np.radians(pitch)
    t2rad = np.radians(roll)
    Prad = np.arctan(np.tan(t1rad) * np.cos(t2rad))
    cos_P = np.cos(Prad)
    sin_P = np.sin(Prad)

    # determine array size
    n_packets = u.shape[0]
    n_uvw = u.shape[1]

    # initialize vectors to be used as matrix elements
    ones = np.ones(n_packets)
    zeros = ones * 0.0

    # the rollaxis calls reorient the matrices so that their lead index is
    # the data packet index
    M1 = np.array([[cos_H, sin_H, zeros],
                   [-sin_H, cos_H, zeros],
                   [zeros, zeros, ones]])
    M1 = np.rollaxis(M1, 2)
    M2 = np.array([[ones, zeros, zeros],
                   [zeros, cos_P, -sin_P],
                   [zeros, sin_P, cos_P]])
    M2 = np.rollaxis(M2, 2)
    M3 = np.array([[cos_R, zeros, sin_R],
                   [zeros, ones, zeros],
                   [-sin_R, zeros, cos_R]])
    M3 = np.rollaxis(M3, 2)

    # construct input array of coordinates (velocities) to be transformed.
    # the basis set is 3D (E,N,U) so that the middle dimension is sized at 3.
    uvw = np.zeros((n_packets, 3, n_uvw))

    # pack the coordinates (velocities) to be transformed into the appropriate
    # slices.
    uvw[:, 0, :] = u
    uvw[:, 1, :] = v
    uvw[:, 2, :] = w

    # the Einstein summation is here configured to do the matrix
    # multiplication MM(i,l) = M1(i,j) * M2(j,k) * M3(k,l) on each slice h.
    MM = np.einsum('hij,hjk,hkl->hil', M1, M2, M3)

    # the Einstein summation is here configured to do the matrix
    # multiplication uvw_earth(i,m) = MM(i,l) * uvw(l,m) on each slice h.
    uvw_earth = np.einsum('hil,hlm->him', MM, uvw)

    # NOTE:
    # these last two executable statements run about a factor of 2
    # faster in the 10000 data packet performance tests versus combining
    # these operations into the one statement:
    #     uvw_earth = np.einsum('hij,hjk,hkl,hlm->him', M1, M2, M3, uvw)

    # break out the coordinate slices and return them
    uu = uvw_earth[:, 0, :]
    vv = uvw_earth[:, 1, :]
    ww = uvw_earth[:, 2, :]

    return (uu, vv, ww)


def magnetic_correction(theta, u, v):
    """
    Description:

        This function corrects velocity profiles for the magnetic variation
        (declination) at the measurement location.  The magnetic declination
        is obtained from the 2010 World Magnetic Model (WMM2010) provided by
        NOAA (see wmm_declination).

        This version handles 'vectorized' input variables without using for
        loops. It was specifically written to handle the case of a 1D array of
        theta values, theta=f(i), with corresponding sets of 'u' and 'v' values
        such that u=f(i,j) and v=f(i,j), where there are j 'u' and 'v' values
        for each theta(i).

    Implemented by:

        2014-04-04: Russell Desiderio. Initial code. This function is used to
                    calculate magnetic corrections by the functions contained
                    in this module instead of the function magnetic_correction
                    found in ion_functions.data.generic_functions.
        2015-04-10: Russell Desiderio. Corrected a typo:
                    uv = np.atleast_2d(u)  ->  u = np.atleast_2d(u)

    Usage:

        u_cor, v_cor = magnetic_correction(theta, u, v)

            where

        u_cor = eastward velocity profiles, in earth coordinates, with
            the correction for magnetic variation applied.
        v_cor = northward velocity profiles, in earth coordinates,
            with the correction for magnetic variation applied.

        theta = magnetic variation based on location (latitude, longitude and
            altitude) and date; units of theta are [degrees]
        u = uncorrected eastward velocity profiles in earth coordinates
        v = uncorrected northward velocity profiles in earth coordinates

    References:

        OOI (2012). Data Product Specification for Velocity Profile and Echo
            Intensity. Document Control Number 1341-00750.
            https://alfresco.oceanobservatories.org/ (See: Company Home >> OOI
            >> Controlled >> 1000 System Level >>
            1341-00750_Data_Product_SPEC_VELPROF_OOI.pdf)

        OOI (2013). Data Product Specification for Turbulent Velocity Profile
            and Echo Intensity. Document Control Number 1341-00760.
            https://alfresco.oceanobservatories.org/ (See: Company Home >> OOI
            >> Controlled >> 1000 System Level >>
            1341-00760_Data_Product_SPEC_VELPROF_OOI.pdf)
    """
    # force shapes of inputs to arrays
    theta = np.atleast_1d(theta)
    u = np.atleast_2d(u)
    v = np.atleast_2d(v)

    theta_rad = np.radians(theta)
    cosT = np.cos(theta_rad)
    sinT = np.sin(theta_rad)

    M = np.array([[cosT, sinT],
                  [-sinT, cosT]])

    # roll axes so that the lead index represents data packet #.
    M = np.rollaxis(M, 2)

    # the coordinate system is 2D, so the middle dimension is sized at 2.
    uv = np.zeros((u.shape[0], 2, u.shape[1]))

    # pack the coordinates to be rotated into the appropriate slices
    uv[:, 0, :] = u
    uv[:, 1, :] = v

    # the Einstein summation is here configured to do the matrix
    # multiplication uv_cor(i,k) = M(i,j) * uv(j,k) on each slice h.
    uv_cor = np.einsum('hij,hjk->hik', M, uv)

    # the magnetically corrected u values are:
    u_cor = uv_cor[:, 0, :]

    # the magnetically corrected v values are:
    v_cor = uv_cor[:, 1, :]

    # return corrected u and v values
    return (u_cor, v_cor)


def enthalpy_SSO_0_p(p):
    r"""This function calculates enthalpy at the Standard Ocean Salinty, SSO,
    and at a Conservative Temperature of zero degrees C, as a function of
    pressure, p, in dbar, using a streamlined version of the 48-term CT
    version of the Gibbs function, that is, a streamlined version of the
    code "enthalpy(SA,CT,p).
    Examples
    --------
    >>> import gsw
    >>> p = np.array([10, 50, 125, 250, 600, 1000])
    >>> gsw.library.enthalpy_SSO_0_p(p)
    array([   97.26388276,   486.27439004,  1215.47518168,  2430.24919716,
            5827.90973888,  9704.32296903])
    Modifications:
    VERSION NUMBER: 3.03 (29th April, 2013)
    References
    ----------
    .. [1] McDougall T.J., P.M. Barker, R. Feistel and D.R. Jackett, 2013:  A
    computationally efficient 48-term expression for the density of seawater in
    terms of Conservative Temperature, and related properties of seawater.  To
    be submitted to J. Atm. Ocean. Technol., xx, yyy-zzz.

    .. [2] https://pypi.python.org/pypi/gsw/
    """
    v01 = 9.998420897506056e+2
    v05 = -6.698001071123802
    v08 = -3.988822378968490e-2
    v12 = -2.233269627352527e-2
    v15 = -1.806789763745328e-4
    v17 = -3.087032500374211e-7
    v20 = 1.550932729220080e-10
    v21 = 1.0
    v26 = -7.521448093615448e-3
    v31 = -3.303308871386421e-5
    v36 = 5.419326551148740e-6
    v37 = -2.742185394906099e-5
    v41 = -1.105097577149576e-7
    v43 = -1.119011592875110e-10
    v47 = -1.200507748551599e-15
    SSO = 35.16504
    a0 = v21 + SSO * (v26 + v36 * SSO + v31 * np.sqrt(SSO))
    a1 = v37 + v41 * SSO
    a2 = v43
    a3 = v47
    b0 = v01 + SSO * (v05 + v08 * np.sqrt(SSO))
    b1 = 0.5 * (v12 + v15 * SSO)
    b2 = v17 + v20 * SSO
    b1sq = b1 ** 2
    sqrt_disc = np.sqrt(b1sq - b0 * b2)
    N = a0 + (2 * a3 * b0 * b1 / b2 - a2 * b0) / b2
    M = a1 + (4 * a3 * b1sq / b2 - a3 * b0 - 2 * a2 * b1) / b2
    A = b1 - sqrt_disc
    B = b1 + sqrt_disc
    part = (N * b2 - M * b1) / (b2 * (B - A))
    db2Pascal = 10000.0
    return (db2Pascal * (p * (a2 - 2 * a3 * b1 / b2 + 0.5 * a3 * p) / b2 +
            (M / (2 * b2)) * np.log(1 + p * (2 * b1 + b2 * p) / b0) + part *
            np.log(1 + (b2 * p * (B - A)) / (A * (B + b2 * p)))))


def z_from_p(p, lat, geo_strf_dyn_height=0):
    r"""Calculates height from sea pressure using the computationally-efficient
    48-term expression for density in terms of SA, CT and p (McDougall et
    al., 2011).  Dynamic height anomaly, geo_strf_dyn_height, if provided, must
    be computed with its pr=0 (the surface).

    Parameters
    ----------
    p : array_like
        pressure [dbar]
    lat : array_like
          latitude in decimal degrees north [-90..+90]
    geo_strf_dyn_height : float, optional
                          dynamic height anomaly [ m :sup:`2` s :sup:`-2` ]

    Returns
    -------
    z : array_like
        height [m]

    See Also
    --------
    # FIXME: enthalpy_SSO_0_CT25, changed!


    Examples
    --------
    >>> p = [10, 50, 125, 250, 600, 1000]
    >>> lat = 4
    >>> z_from_p(p, lat)
    array([  -9.94460074,  -49.71817465, -124.2728275 , -248.47044828,
           -595.82618014, -992.0931748 ])

    Notes
    -----
    At sea level z = 0, and since z (HEIGHT) is defined to be positive upwards,
    it follows that while z is positive in the atmosphere, it is NEGATIVE in
    the ocean.

    References
    ----------
    .. [1] IOC, SCOR and IAPSO, 2010: The international thermodynamic equation
    of seawater - 2010: Calculation and use of thermodynamic properties.
    Intergovernmental Oceanographic Commission, Manuals and Guides No. 56,
    UNESCO (English), 196 pp.

    .. [2] McDougall T.J., P.M. Barker, R. Feistel and D.R. Jackett, 2011:  A
    computationally efficient 48-term expression for the density of seawater
    in terms of Conservative Temperature, and related properties of seawater.

    .. [3] Moritz (2000) Goedetic reference system 1980. J. Geodesy, 74,
    128-133.

    .. [4] https://pypi.python.org/pypi/gsw/
    """

    X = np.sin(np.deg2rad(lat))
    sin2 = X ** 2
    B = 9.780327 * (1.0 + (5.2792e-3 + (2.32e-5 * sin2)) * sin2)
    gamma = 2.26e-07
    A = -0.5 * gamma * B
    C = enthalpy_SSO_0_p(p) - geo_strf_dyn_height

    return -2 * C / (B + np.sqrt(B ** 2 - 4 * A * C))
