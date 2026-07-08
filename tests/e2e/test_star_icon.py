"""
E2E: each card links to the tool's real GitHub page — from both the tool name
and the star icon.

Fully deterministic: it renders the page and inspects the rendered links. No
sync and no call to GitHub is involved, so it purely checks that the
``github_repo`` field flows all the way from the DB into clickable links.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

PYTEST_REPO = "https://github.com/pytest-dev/pytest"


def _wait_for_cards(driver):
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".card"))
    )


def test_name_and_star_link_to_github(driver, base_url):
    driver.get(base_url)
    _wait_for_cards(driver)

    # pytest's repo is pytest-dev/pytest — both its name link and star link
    # should point there and open in a new tab.
    name = driver.find_element(By.CSS_SELECTOR, f'a.card-name[href="{PYTEST_REPO}"]')
    star = driver.find_element(By.CSS_SELECTOR, f'a.github-stars[href="{PYTEST_REPO}"]')

    assert name.get_attribute("target") == "_blank"
    assert star.get_attribute("target") == "_blank"


def test_every_card_links_to_github(driver, base_url):
    driver.get(base_url)
    _wait_for_cards(driver)

    # Every seeded tool has a repo, so every card carries a name link and a
    # star link.
    cards = driver.find_elements(By.CSS_SELECTOR, ".card")
    name_links = driver.find_elements(By.CSS_SELECTOR, ".card a.card-name")
    star_links = driver.find_elements(By.CSS_SELECTOR, ".card a.github-stars")

    assert len(name_links) == len(cards)
    assert len(star_links) == len(cards)
