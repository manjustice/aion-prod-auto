import os.path
import time
from math import ceil

import numpy as np
import pyautogui as pg
import pygetwindow as gw
import win32gui

from app.block import Block, Position, Size, Item
from app.custom_exception import InvalidItemError, CantFindAionError, CantFindAionProdWindowError
from app.utils import get_std_color_sum
from config import PRODUCT_WINDOW_SIZE, ITEMS_BLOCK_SIZE, START_PRODUCTION_BUTTON, BASE_DIR, root_logger


class ProductionWindow:
    def __init__(self):
        self.switch_to_aion()
        self.main_window = self._find_main_window()

        if self.main_window is None:
            raise CantFindAionProdWindowError

        self.block_with_items = Block(
            start=Position(
                x=self.main_window.start.x + 120,
                y=self.main_window.start.y + 85
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

        self.items: list[Item] = []
        self._update_available_items()
        root_logger.debug(f"Found {len(self.items)}")

    def start_make_item(self, item: Item):
        self._change_page(item.page)
        item_pos = item.block.get_random_position()

        pg.moveTo(*item_pos, duration=0.1)
        pg.click()

        start_button_pos = self.start_production_button.get_random_position()

        pg.moveTo(*start_button_pos, duration=0.1)
        pg.click()

    def _update_available_items(self):
        """Update a list of available items in the production window."""
        for page in range(1, self.page_count + 1):
            self._change_page(page)
            self._parse_prod_items()

    def _parse_prod_items(self):
        screen_of_items = self.block_with_items.make_screenshot()

        image_array = np.array(screen_of_items)

        height, width, _ = image_array.shape
        row = 0

        while row < height:
            std_color_sum = get_std_color_sum(image_array[row, :, :])

            if std_color_sum > 15:
                height_start = row - 3
                row += 1
                while row < height:
                    std_color_sum = get_std_color_sum(image_array[row, :, :])
                    row += 1

                    if std_color_sum < 15:
                        height_end = row + (18 - (row - height_start))
                        cropped_image = screen_of_items.crop((0, height_start, width, height_end))

                        try:
                            item = Item(
                                item_array=np.array(cropped_image),
                                page=self.current_page,
                                block=Block(
                                    start=Position(
                                        x=self.block_with_items.start.x,
                                        y=self.block_with_items.start.y + height_start
                                    ),
                                    size=Size(*cropped_image.size)
                                )
                            )
                        except InvalidItemError:
                            pass
                        else:
                            if item not in self.items:
                                self.items.append(item)
                        finally:
                            break

            else:
                row += 1

    def _change_page(self, page: int):
        root_logger.debug(f"Changing to page {page}")
        from_x, from_y = self.scroll_bar.get_top_center_position()
        pg.moveTo(from_x, from_y, duration=0.2)
        pg.mouseDown()

        to_x = from_x
        to_y = self.scroll_bar_box.start.y + (self.scroll_bar.size.height * (page - 1))
        pg.moveTo(to_x, to_y, duration=0.2)
        pg.mouseUp()

        self.current_page = page

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
                os.path.join(BASE_DIR, "screenshot_of_the_prod_window_hat.png"), confidence=0.9
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

    @staticmethod
    def switch_to_aion():
        root_logger.debug("Trying to find Aion")

        aion_window_names = ["Aion", "AIONClassic", "aion"]
        windows = gw.getAllWindows()

        for window in windows:
            if window.title in aion_window_names:
                root_logger.debug(f"Aion found name - {aion_window_names}. Activating")
                window.activate()

        for _ in range(50):
            hwnd = win32gui.GetForegroundWindow()

            if hwnd:
                active_window_title = win32gui.GetWindowText(hwnd)
                if active_window_title in aion_window_names:
                    return

            time.sleep(0.1)

        raise CantFindAionError
