####
# Author: Kwok Keith
# Last Edited: 06 December 2025
####

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium_chat_extractor import SeleniumChatExtractor


DEFAULT_SHARE_URL = "https://chatgpt.com/share/692be9da-04f8-8009-a0c1-9f053e406d3f"

class GPTChatExtractor(SeleniumChatExtractor):
    def __init__(self):
        super().__init__(
            default_share_url=DEFAULT_SHARE_URL,
            data_dir="gpt_convo_data",
            prefix="gpt_conversation",
            title="Shared ChatGPT Conversation",
            model_display_name="ChatGPT",
        )

    def wait_for_chat_history(self, driver, timeout):
        """
        Wait until ChatGPT chat history articles are present in the DOM.
        """
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div>article")
            )
        )

    def form_user_model_list(self, driver):
        """
        Parse the ChatGPT chat html into user and model lists.
        """
        soup = BeautifulSoup(driver.page_source, "html.parser")
        text = soup.prettify()
        with open("output.txt", "w+", encoding="utf-8") as f:
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


def main():
    extractor = GPTChatExtractor()
    extractor.run_from_cli()


if __name__ == "__main__":
    main()
