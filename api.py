####
# Author: Kwok Keith
# Last Edited: 06 December 2025
####

from typing import Optional, Tuple

from selenium_chat_extractor import initialise_driver
from gemini.extract_gemini import GeminiChatExtractor, DEFAULT_SHARE_URL as GEMINI_DEFAULT_SHARE_URL
from chatgpt.extract_gpt import GPTChatExtractor, DEFAULT_SHARE_URL as GPT_DEFAULT_SHARE_URL


def extract_gemini_conversation(
    share_url: Optional[str] = None,
) -> Tuple[str, str]:
    """
    Scrape a shared Gemini conversation and save it to disk.

    Args:
        share_url: Optional share URL. If omitted, uses the Gemini default.

    Returns:
        (json_path, conversation_id)
    """
    extractor = GeminiChatExtractor()
    if share_url is None:
        share_url = GEMINI_DEFAULT_SHARE_URL

    driver = None
    try:
        driver = initialise_driver()
        json_path, conversation_id = extractor.extract_chat(driver, share_url)
        return json_path, conversation_id
    finally:
        if driver is not None:
            driver.quit()


def extract_gpt_conversation(
    share_url: Optional[str] = None,
) -> Tuple[str, str]:
    """
    Scrape a shared ChatGPT conversation and save it to disk.

    Args:
        share_url: Optional share URL. If omitted, uses the ChatGPT default.

    Returns:
        (json_path, conversation_id)
    """
    extractor = GPTChatExtractor()
    if share_url is None:
        share_url = GPT_DEFAULT_SHARE_URL

    driver = None
    try:
        driver = initialise_driver()
        json_path, conversation_id = extractor.extract_chat(driver, share_url)
        return json_path, conversation_id
    finally:
        if driver is not None:
            driver.quit()
