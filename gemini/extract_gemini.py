####
# Author: Kwok Keith
# Last Edited: 06 December 2025
####

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium_chat_extractor import SeleniumChatExtractor


DEFAULT_SHARE_URL = "https://gemini.google.com/share/e230b881ff8d"

class GeminiChatExtractor(SeleniumChatExtractor):
    def __init__(self):
        super().__init__(
            default_share_url=DEFAULT_SHARE_URL,
            data_dir="gemini_convo_data",
            prefix="gemini_conversation",
            title="Shared Gemini Conversation",
            model_display_name="Gemini",
        )

    def wait_for_chat_history(self, driver, timeout):
        """
        Wait until Gemini chat history is present in the DOM.
        """
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.chat-history")
            )
        )

    def form_user_model_list(self, driver):
        """
        Parse the Gemini chat html into user and model lists.
        """
        soup = BeautifulSoup(driver.page_source, "html.parser")

        user_chat_history = [chat.text.strip()
                            for chat in soup.find_all("user-query")]
        model_chat_history = [chat.text.strip()
                            for chat in soup.find_all("response-container")]

        return user_chat_history, model_chat_history


def main():
    extractor = GeminiChatExtractor()
    extractor.run_from_cli()


if __name__ == "__main__":
    main()
