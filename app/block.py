import random
from typing import NamedTuple, Self

import numpy as np
import pyautogui as pg

from app.custom_exception import InvalidItemError
from app.utils import get_std_color_sum


class Position(NamedTuple):
    x: int
    y: int

    def __str__(self):
        return f"x - {self.x}, y - {self.y}"


class Size(NamedTuple):
    width: int
    height: int

    def __str__(self):
        return f"width - {self.width}, height - {self.height}"


class Block(NamedTuple):
    start: Position
    size: Size

    def __str__(self):
        return f"Block start: {self.start}. Size: {self.size}"

    def get_region(self):
        return self.start.x, self.start.y, self.size.width, self.size.height

    def get_random_position(self):
        return Position(
            x=random.randint(self.start.x + 1, self.start.x + self.size.width - 1),
            y=random.randint(self.start.y + 1, self.start.y + self.size.height - 1),
        )

    def get_top_center_position(self):
        return Position(
            x=self.start.x + self.size.width // 2,
            y=self.start.y
        )

    def make_screenshot(self):
        screenshot = pg.screenshot(region=self.get_region())
        return screenshot

    def save_screenshot(self, path: str):
        screenshot = self.make_screenshot()
        screenshot.save(path)


class Item:
    def __init__(self, block: Block, item_array: np.ndarray, page: int):
        self.block = block
        self.page = page
        self.item_array = item_array

    @property
    def item_array(self):
        return self._item_array

    @item_array.setter
    def item_array(self, value: np.ndarray):
        if type(value) is not np.ndarray:
            raise InvalidItemError

        for column_pixels in np.transpose(value, (1, 0, 2))[:3]:
            std_color_sum = get_std_color_sum(column_pixels)
            if std_color_sum > 15:
                raise InvalidItemError

        self._item_array = value

    def __eq__(self, other: Self):
        if isinstance(other, Item):
            return np.allclose(self.item_array, other.item_array, rtol=1)
        return False
