import time
from pathlib import Path
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# =========================
# CONFIG
# =========================

PHONE_NUMBER = "6281234567890"
MESSAGE = "Halo bro, ini file database yang diminta."

DATABASE_FILE = Path(r"C:\path\to\database.bak")

# Persistent Chrome profile so you do not need to scan QR every time.
CHROME_PROFILE = Path("./whatsapp_chrome_profile").resolve()


# =========================
# WHATSAPP CONNECTION
# =========================

def create_driver():
    options = Options()

    options.add_argument(f"--user-data-dir={CHROME_PROFILE}")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    driver.get("https://web.whatsapp.com/")

    return driver


def wait_for_whatsapp(driver):
    print("Waiting for WhatsApp Web...")

    WebDriverWait(driver, 120).until(
        EC.presence_of_element_located(
            (By.ID, "pane-side")
        )
    )

    print("WhatsApp Web connected.")


# =========================
# SEND MESSAGE
# =========================

def send_message(driver, phone_number, message):
    url = (
        "https://web.whatsapp.com/send"
        f"?phone={phone_number}"
        f"&text={quote(message)}"
    )

    driver.get(url)

    send_button = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                '//button[@aria-label="Send"]'
            )
        )
    )

    send_button.click()

    print("Message sent.")


# =========================
# SEND DATABASE FILE
# =========================

def send_file(driver, phone_number, file_path, caption=""):
    file_path = Path(file_path).resolve()

    if not file_path.exists():
        raise FileNotFoundError(
            f"Database file not found: {file_path}"
        )

    url = (
        "https://web.whatsapp.com/send"
        f"?phone={phone_number}"
    )

    driver.get(url)

    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located(
            (By.ID, "main")
        )
    )

    attachment_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                '//button[@title="Attach"]'
            )
        )
    )

    attachment_button.click()

    file_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                '//input[@type="file"]'
            )
        )
    )

    file_input.send_keys(str(file_path))

    time.sleep(2)

    if caption:
        caption_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//div[@contenteditable="true"][@role="textbox"]'
                )
            )
        )

        caption_box.send_keys(caption)

    send_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                '//button[@aria-label="Send"]'
            )
        )
    )

    send_button.click()

    print(f"File sent: {file_path}")


# =========================
# MAIN
# =========================

def main():
    driver = create_driver()

    try:
        wait_for_whatsapp(driver)

        send_message(
            driver,
            PHONE_NUMBER,
            MESSAGE
        )

        send_file(
            driver,
            PHONE_NUMBER,
            DATABASE_FILE,
            caption="Database backup."
        )

        print("Done.")
        print("Press Ctrl+C or close the browser when finished.")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Stopping...")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
