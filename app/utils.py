import subprocess

import numpy as np


def switch_to_window(req_window_name: str):
    result = subprocess.run(['xdotool', 'search', '--name', '.*'], capture_output=True, text=True)

    window_ids = result.stdout.splitlines()

    for window_id in window_ids:
        result = subprocess.run(['xdotool', 'getwindowname', window_id], capture_output=True, text=True)
        window_name = result.stdout.strip()

        if window_name == req_window_name or req_window_name in window_name:
            subprocess.run(['xdotool', 'windowactivate', window_id])


def get_std_color_sum(row_pixels):
    std_color = np.std(row_pixels, axis=0)
    return sum(std_color)


if __name__ == '__main__':
    switch_to_window("Image Viewer")
