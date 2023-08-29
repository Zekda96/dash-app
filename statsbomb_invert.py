# field_dim = (106.0, 68.0)
# self.meters_per_yard = 0.9144
import numpy as np


def convert_x(val):
    r_x = 106/120  # ratio to scale down statsbomb max
    h_x = 106/2  # Half of pitch length
    res = (val * r_x) - h_x
    return res


def invert(val, max):
    # If 100% is bottom and 0% is top, now 100% is top.
    res = np.abs(val - max)
    return res


def convert_y(val):
    max = 80
    r_y = 68/max
    h_y = 68/2
    res = (invert(val, max) * r_y) - h_y
    return res
