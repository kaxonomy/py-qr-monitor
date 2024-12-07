import cv2
import webbrowser
from pyzbar.pyzbar import decode
import pyautogui
import os
import numpy as np
import time
import logging
import re
import warnings

LINKS_FILE = "links.txt"

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
warnings.filterwarnings("ignore", category=UserWarning, module="zbar")

URL_REGEX = re.compile(r'^(https?://)([a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+)(:[0-9]+)?(/.*)?$')

def read_opened_links():
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, "r") as file:
            return set(line.strip() for line in file.readlines())
    return set()

def log_link(link):
    with open(LINKS_FILE, "a") as file:
        file.write(link + "\n")

def is_valid_url(url):
    return bool(URL_REGEX.match(url))

def process_qr_code(frame, opened_links):
    detected_qr_codes = decode(frame)
    for qr_code in detected_qr_codes:
        qr_data = qr_code.data.decode("utf-8")
        if is_valid_url(qr_data) and qr_data not in opened_links:
            logging.info(f"Opening new valid link: {qr_data}")
            webbrowser.open(qr_data)
            log_link(qr_data)
            opened_links.add(qr_data)

def main():
    logging.info("Screen QR code monitor is starting...")
    opened_links = read_opened_links()
    screen_width, screen_height = pyautogui.size()
    logging.info(f"Screen size detected: {screen_width}x{screen_height}")
    try:
        while True:
            screenshot = pyautogui.screenshot(region=(0, 0, screen_width, screen_height))
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            process_qr_code(frame, opened_links)
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        logging.info("Exiting screen monitoring...")

if __name__ == "__main__":
    main()
