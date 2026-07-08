import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# URL of the running nginx frontend (all /api calls are same-origin from there).
BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost")

# The remote Chrome (the `selenium` Docker Compose service).
SELENIUM_REMOTE_URL = os.getenv("SELENIUM_REMOTE_URL", "http://selenium:4444")


def _new_driver() -> webdriver.Remote:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,1024")
    return webdriver.Remote(command_executor=SELENIUM_REMOTE_URL, options=options)


@pytest.fixture()
def driver():
    """
    A remote Chrome session. The Selenium container may still be booting when the
    tests start, so the initial connection is retried for up to a minute.
    """
    deadline = time.time() + 60
    while True:
        try:
            drv = _new_driver()
            break
        except Exception:
            if time.time() > deadline:
                raise
            time.sleep(2)

    drv.set_page_load_timeout(30)
    try:
        yield drv
    finally:
        drv.quit()


@pytest.fixture()
def base_url() -> str:
    return BASE_URL
