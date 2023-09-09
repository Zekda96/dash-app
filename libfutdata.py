# field_dim = (106.0, 68.0)
# x from -53 to 53
# y from -34 to 34

# self.meters_per_yard = 0.9144
import numpy as np


def convert_x(val, max_x=120):
    """Transform x coordinates to Pitchly coordinates"""
    r_x = 106 / max_x  # ratio to scale down statsbomb max
    h_x = 106 / 2  # Half of pitch length
    res = (val * r_x) - h_x
    return res


def invert(val, max):
    # If 100% is bottom and 0% is top, now 100% is top.
    res = np.abs(val - max)
    return res


def convert_y(val, max_y=80, invert_y=True):
    """Transform y coordinates to Pitchly coordinates"""
    r_y = 68 / max_y
    h_y = 68 / 2
    if invert_y: val = invert(val, max_y)

    res = (val * r_y - h_y)
    return res
