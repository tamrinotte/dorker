# -*- coding: utf-8 -*-

# MODULES AND/OR LIBRARIES
from io import BytesIO
from math import ceil
from time import sleep
from typing import Any
from PIL import Image
from selenium.common.exceptions import WebDriverException
from modules.logging_config import debug

##############################

# FULL PAGE SCREENSHOT NATIVE

##############################

def save_full_page_screenshot_native(driver, path):
    try:
        driver.get_full_page_screenshot_as_file(path)
        return True
    except AttributeError:
        return False
    except WebDriverException as e:
        debug(f"Native full-page screenshot failed: {e}")
        return False

##############################

# FULL PAGE SCREENSHOT STITCHED

##############################

def save_full_page_screenshot_stitched(driver, path, delay = 0.2):
    try:
        total_width = driver.execute_script(
            "return Math.max(document.body.scrollWidth, document.documentElement.scrollWidth)"
        )
        total_height = driver.execute_script(
            "return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)"
        )
        viewport_width = driver.execute_script("return window.innerWidth")
        viewport_height = driver.execute_script("return window.innerHeight")
    except WebDriverException as e:
        debug(f"Failed to read page dimensions: {e}")
        return False

    if not all(isinstance(v, (int, float)) and v > 0 for v in (total_width, total_height, viewport_width, viewport_height)):
        debug("Invalid page/viewport dimensions; aborting stitched screenshot.")
        return False

    cols = ceil(total_width / viewport_width)
    rows = ceil(total_height / viewport_height)

    stitched = Image.new("RGB", (int(total_width), int(total_height)))
    for row in range(rows):
        for col in range(cols):
            x = int(col * viewport_width)
            y = int(row * viewport_height)
            try:
                driver.execute_script(f"window.scrollTo({x}, {y})")
                sleep(delay)
                png = driver.get_screenshot_as_png()
                img = Image.open(BytesIO(png)).convert("RGB")
                stitched.paste(img, (x, y))
            except Exception as e:
                debug(f"Failed capturing tile ({row},{col}): {e}")
                return False

    try:
        stitched.save(path)
        return True
    except Exception as e:
        debug(f"Failed to save stitched image: {e}")
        return False

##############################

# SAVE FULL PAGE SCREENSHOT

##############################

def save_full_page_screenshot(driver, path):
    if save_full_page_screenshot_native(driver, path):
        return True

    if save_full_page_screenshot_stitched(driver, path):
        return True

    try:
        driver.save_screenshot(path)
        return True
    except Exception as e:
        debug(f"Screenshot failed: {e}")
        return False
