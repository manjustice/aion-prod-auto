import random
from typing import NamedTuple
import pyautogui as pg


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


class Item(NamedTuple):
    block: Block
    page: int
