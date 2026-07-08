"""
E2E: clicking "Sync stars" refreshes the data and advances the sync timestamp.

This is the test that only an end-to-end check can catch. The sync runs in a
FastAPI *background task*, so a single API response and the response schema look
perfectly fine — unit/integration/smoke tests all pass. Only by driving the real
UI, triggering the sync, and waiting for the ``last_synced_at`` timestamp to
actually change do we find out whether the background side-effect really works.

The breaking patch removes the line that stamps ``last_synced_at`` inside the
background task; this test then times out waiting for the change and fails,
while every lower-level test stays green.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def _synced_value(driver) -> str:
    # Re-find the element every time — the grid is re-rendered while polling.
    return driver.find_element(By.ID, "last-synced").get_attribute("data-last-synced") or ""


def test_sync_updates_last_synced(driver, base_url):
    driver.get(base_url)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".card"))
    )

    before = _synced_value(driver)

    # Trigger the sync. The frontend POSTs /api/tools/sync then polls until the
    # timestamp advances.
    driver.find_element(By.ID, "btn-sync").click()

    # Real GitHub calls + background task + frontend polling — allow a generous
    # window. Under the broken patch the timestamp never changes and this fails.
    WebDriverWait(driver, 60).until(lambda d: _synced_value(d) != before)
