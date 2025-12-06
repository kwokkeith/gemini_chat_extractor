####
# Author: Kwok Keith
# Last Edited: 06 December 2025
####
from library import *
import argparse
from abc import ABC, abstractmethod

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SeleniumChatExtractor(ABC):
    """
    Base extractor for any shared chat page that uses Selenium.

    Child classes must implement:
        wait_for_chat_history(driver, timeout)
        form_user_model_list(driver)
    """

    def __init__(
        self,
        default_share_url,
        data_dir,
        prefix,
        title,
        model_display_name,
    ):
        self.default_share_url = default_share_url
        self.data_dir = data_dir
        self.prefix = prefix
        self.title = title
        self.model_display_name = model_display_name


    @abstractmethod
    def wait_for_chat_history(self, driver, timeout):
        """
        Provider specific wait condition.
        Should use WebDriverWait and EC with the right selector.
        """
        raise NotImplementedError


    @abstractmethod
    def form_user_model_list(self, driver):
        """
        Provider specific parsing.

        Returns:
            user_chat_history, model_chat_history
        """
        raise NotImplementedError


    def extract_chat(self, driver, share_url):
        logging.info("Opening shared URL")
        driver.get(share_url)

        try:
            logging.info("Trying to find chat without sign in")
            self.wait_for_chat_history(driver, timeout=30)
            logging.info("Chat found without sign in")
        except TimeoutException:
            logging.info("Chat not visible")
            raise

        user_chat, model_chat = self.form_user_model_list(driver)

        json_path, conversation_id = get_next_conversation_path(
            self.data_dir,
            prefix=self.prefix,
            ext=".json",
        )

        export_conversation_json(
            json_path=json_path,
            user_chat_history=user_chat,
            model_chat_history=model_chat,
            conversation_id=conversation_id,
            title=self.title,
            model_display_name=self.model_display_name,
        )

        logging.info(f"Saved chat to {json_path}")
        return json_path, conversation_id


    def parse_args(self):
        parser = argparse.ArgumentParser(
            description=f"Scrape a shared {self.model_display_name} conversation and export it as json"
        )
        parser.add_argument(
            "share_url",
            nargs="?",
            default=self.default_share_url,
            help=f"Share URL (defaults to the hard coded demo URL if omitted)",
        )
        return parser.parse_args()


    def run_from_cli(self):
        args = self.parse_args()
        driver = None
        try:
            driver = initialise_driver()
            self.extract_chat(driver, args.share_url)
        finally:
            # Close driver (cleanup)
            if driver is not None:
                driver.quit()
                logging.info("Driver closed")