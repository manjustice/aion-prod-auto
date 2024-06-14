import numpy as np


def get_std_color_sum(row_pixels):
    std_color = np.std(row_pixels, axis=0)
    return sum(std_color)
