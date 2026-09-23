import logging
import os
import time

from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=ENV_FILE)


PHONE_NUMBER = os.getenv("WHATSAPP_NUMBER")
MESSAGE = os.getenv("MESSAGE")
BRAVE_BINARY_LOCATION = os.getenv("BROWSER_BINARY_LOCATION")

BRAVE_USER_DATA = os.getenv("BROWSER_USER_DATA")
BRAVE_PROFILE = os.getenv("BROWSER_PROFILE")

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / f"{datetime.now().strftime('%m_%d_%y')}.txt"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def validate_configuration():
    required_variables = {
        "WHATSAPP_NUMBER": PHONE_NUMBER,
        "MESSAGE": MESSAGE,
        "BROWSER_BINARY_LOCATION": BRAVE_BINARY_LOCATION,
    }

    for variable_name, value in required_variables.items():
        if not value:
            raise ValueError(
                f"Environment variable '{variable_name}' is not configured."
            )

    brave_path = Path(BRAVE_BINARY_LOCATION)

    if not brave_path.exists():
        raise FileNotFoundError(
            f"Brave browser not found: {BRAVE_BINARY_LOCATION}"
        )

    if not brave_path.is_file():
        raise ValueError(
            f"BROWSER_BINARY_LOCATION is not a file: {BRAVE_BINARY_LOCATION}"
        )


def create_driver():
    logger.info(
        "Service: Creating Selenium WebDriver instance with Brave browser."
    )

    options = Options()

    options.binary_location = BRAVE_BINARY_LOCATION
    options.add_argument(f"--user-data-dir={BRAVE_USER_DATA}")
    options.add_argument(f"--profile-directory={BRAVE_PROFILE}")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)

    driver.get("https://web.whatsapp.com/")

    return driver


def send_message(driver):
    logger.info(
        "Service: Sending WhatsApp message to %s.",
        PHONE_NUMBER
    )

    url = (
        "https://web.whatsapp.com/send"
        f"?phone={PHONE_NUMBER}"
        f"&text={quote(MESSAGE)}"
    )

    driver.get(url)

    send_button = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//button[@aria-label="Send"]')
        )
    )

    send_button.click()

    logger.info("Service: Message sent successfully.")


def main():
    driver = None

    logger.info(
        "Service: WhatsApp Personal - Starting service."
    )

    try:
        validate_configuration()

        logger.info(
            "Service: Configuration validated successfully."
        )

        driver = create_driver()

        logger.info(
            "Service: Waiting for WhatsApp Web connection."
        )

        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located(
                (By.ID, "pane-side")
            )
        )

        logger.info(
            "Service: WhatsApp Web connected successfully."
        )

        send_message(driver)

        time.sleep(5)

    except Exception:
        logger.exception(
            "Service: An unexpected error occurred."
        )
        raise

    finally:
        if driver:
            driver.quit()

            logger.info(
                "Service: WebDriver closed."
            )


if __name__ == "__main__":
    main()