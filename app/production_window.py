import numpy as np
import pyautogui as pg
from math import ceil

from block import Block, Position, Size, Item
from config import PRODUCT_WINDOW_SIZE, ITEMS_BLOCK_SIZE, START_PRODUCTION_BUTTON
from utils import get_std_color_sum


class ProductionWindow:
    def __init__(self):
        self.main_window = self._find_main_window()

        if self.main_window is None:
            raise Exception("Main window not found!")

        self.block_with_items = Block(
            start=Position(
                x=self.main_window.start.x + 120,
                y=self.main_window.start.y + 75
            ),
            size=Size(
                width=ITEMS_BLOCK_SIZE[0],
                height=ITEMS_BLOCK_SIZE[1]
            )
        )
        self.start_production_button = Block(
            start=Position(
                x=self.main_window.start.x + 423,
                y=self.main_window.start.y + 530
            ),
            size=Size(
                width=START_PRODUCTION_BUTTON[0],
                height=START_PRODUCTION_BUTTON[1]
            )
        )

        self.scroll_bar_box = Block(
            start=Position(
                x=self.main_window.start.x + 507,
                y=self.main_window.start.y + 94
            ),
            size=Size(width=16, height=398)
        )
        self.current_page = 1
        self.scroll_bar = self._get_scroll_bar()
        self.page_count = ceil(self.scroll_bar_box.size.height / self.scroll_bar.size.height)

        self._change_page(self.current_page)

        self.scroll_bar.save_screenshot("text.png")

        self.items: list[Item] = self._get_available_items()

    def _get_available_items(self) -> list[Item]:
        """Return a list of available items in the production window."""
        items = []

        screen_of_items = self.block_with_items.make_screenshot()
        image_array = np.array(screen_of_items)

        height, width, _ = image_array.shape
        row = 0
        image_count = 0

        while row < height:
            std_color_sum = get_std_color_sum(image_array[row, :, :])

            if std_color_sum > 15:
                height_start = row - 3
                row += 1
                while row < height:
                    std_color_sum = get_std_color_sum(image_array[row, :, :])
                    row += 1

                    if std_color_sum < 15:
                        cropped_image = screen_of_items.crop((0, height_start, width, row + 2))
                        cropped_image.save(f"items/item-{image_count}.png")

                        image_count += 1
                        break

            else:
                row += 1

        return items

    def _change_page(self, page: int):
        mouse_pos = self.scroll_bar.get_top_center_position()
        pg.moveTo(mouse_pos.x, mouse_pos.y, duration=1)
        pg.mouseDown()

        to_x = mouse_pos.x
        to_y = self.scroll_bar_box.start.y + self.scroll_bar.size.height * (page - 1)
        pg.moveTo(to_x, to_y, duration=1)
        pg.mouseUp()

    def _get_scroll_bar(self) -> Block:
        screenshot = self.scroll_bar_box.make_screenshot()
        image_array = np.array(screenshot)

        height, width, _ = image_array.shape
        row = 0
        start = None

        while row < height:
            std_color_sum = get_std_color_sum(image_array[row, :, :])

            if start is None:
                if std_color_sum > 15:
                    start = row
            elif type(start) is int:
                if std_color_sum < 15:
                    end = row
                    break
            row += 1
        else:
            end = row

        return Block(
            start=Position(
                x=self.scroll_bar_box.start.x,
                y=self.scroll_bar_box.start.y + start
            ),
            size=Size(
                width=self.scroll_bar_box.size.width,
                height=end - start
            )
        )

    @staticmethod
    def _find_main_window() -> Block | None:
        """Try to find the hat of the production window on the screen. If it is not found, return None."""
        try:
            hat_of_product_window_loc = pg.locateOnScreen(
                "screenshot_of_the_prod_window_hat.png", confidence=0.9
            )
        except pg.ImageNotFoundException:
            return None

        if hat_of_product_window_loc is None:
            return None

        pixels_y_main_window = 5

        start = Position(
            x=int(hat_of_product_window_loc.left),
            y=int(hat_of_product_window_loc.top + hat_of_product_window_loc.height + pixels_y_main_window),
        )

        return Block(
            start=start,
            size=Size(
                width=PRODUCT_WINDOW_SIZE[0],
                height=PRODUCT_WINDOW_SIZE[1]
            )
        )

