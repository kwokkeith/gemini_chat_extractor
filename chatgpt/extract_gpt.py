from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

import logging
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import json
import os
import re
import argparse

DEFAULT_SHARE_URL = "https://chatgpt.com/share/69216b86-6864-8009-96f5-5d5ee0f9cdb1"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def initialise_driver():
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)
    driver.maximize_window()
    return driver

def wait_for_chat_history(driver, timeout):
    # Wait for the chat root to load!
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div>article")
        )
    )

def form_user_model_list(driver):
    """
    Takes in the driver with a page source, then extracts out the contents of the user
    query and model response for GEMINI's html page content.

    args:
        driver: selenium driver loaded with page content (Gemini chat convo page)
    return:
        user_chat_history: list of user chat queries in temporal order
        model_chat_history: list of model chat responses in temporal order
    """


    # Form the json formatted chat output
    soup = BeautifulSoup(driver.page_source, "html.parser")
    text = soup.prettify()
    with open("output.txt","w+") as f:
        f.write(text)

    chat_history = [chat.text.strip() for chat in soup.find_all("article")]

    user_chat_history = []
    model_chat_history = []

    for entry in chat_history:
        if entry.startswith("You said:"):
            user_chat_history.append(entry.split("You said:", 1)[1].strip())
        elif entry.startswith("ChatGPT said:"):
            model_chat_history.append(entry.split("ChatGPT said:", 1)[1].strip())

    return user_chat_history, model_chat_history


def get_next_conversation_path(data_dir, prefix="gpt_conversation", ext=".json"):
    """
    Scan data_dir for existing gpt_conversation_XXX.json files and
    return the next available path and conversation_id.
    """

    os.makedirs(data_dir, exist_ok=True)

    pattern = re.compile(rf"{re.escape(prefix)}_(\d+){re.escape(ext)}$")
    max_index = 0

    for fname in os.listdir(data_dir):
        match = pattern.match(fname)
        if match:
            idx = int(match.group(1))
            if idx > max_index:
                max_index = idx

    next_index = max_index + 1
    filename = f"{prefix}_{next_index:03d}{ext}"
    conversation_id = f"c_{next_index:03d}"

    return os.path.join(data_dir, filename), conversation_id


def export_conversation_json(json_path, user_chat_history, model_chat_history, conversation_id="c_001"):
    """
    Takes in the list of user chat and model chat in temporal order
    and exports it to the relevant json format for data exploitation.

    args:
        json_path: the path to the output json
        user_chat_history: list of user chat queries in temporal order
        model_chat_history: list of model chat responses in temporal order
    return:
        None
    """
    messages = []

    for i, (user_msg, model_msg) in enumerate(zip(user_chat_history, model_chat_history)):
        # User message
        messages.append({
            "id": f"u_{i}",
            "agent": "user",            
            "role": "user",
            "content": user_msg,
        })

        # Model message
        messages.append({
            "id": f"m_{i}",
            "agent": "model",         
            "role": "assistant",
            "content": model_msg,
        })

    conversation_obj = {
        "conversation_id": conversation_id,
        "title": "Shared ChatGPT Conversation",
        "agents": {
            "user": {
                "id": "user",
                "display_name": "User",
                "type": "human",
            },
            "model": {
                "id": "model",
                "display_name": "ChatGPT",
                "type": "assistant",
            },
        },
        "messages": messages,
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(conversation_obj, f, ensure_ascii=False, indent=2)


def extract_chat(driver, share_url):
    logging.info("Opening shared ChatGPT URL")
    driver.get(share_url)

    try:
        logging.info("Trying to find chat without sign in")
        wait_for_chat_history(driver, timeout=30) # Wait for share page to load
        logging.info("Chat found without sign in")
    except TimeoutException:
        logging.info("Chat not visible")
        raise

    # Form up the conversation json
    user_chat, model_chat = form_user_model_list(driver)

    print("user", user_chat)
    print("model", model_chat)

    data_dir = os.path.join(os.curdir, "gpt_convo_data")
    json_path, conversation_id = get_next_conversation_path(data_dir)

    export_conversation_json(json_path, user_chat, model_chat, conversation_id=conversation_id)
    logging.info(f"Saved chat to {json_path}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scrape a shared Gemini conversation and export it as json"
    )
    parser.add_argument(
        "share_url",
        nargs="?",
        default=DEFAULT_SHARE_URL,
        help="Gemini share URL (defaults to the hard coded demo URL if omitted)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    driver = None
    try:
        driver = initialise_driver()
        extract_chat(driver, args.share_url)
    finally:
        if driver is not None:
            driver.quit()
            logging.info("Driver closed")


if __name__ == "__main__":
    main()