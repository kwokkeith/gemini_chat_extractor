import logging
import undetected_chromedriver as uc
import os
import re
import json


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


def initialise_driver():
    """
    Create and return a maximised undetected Chrome driver.
    """
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)
    driver.maximize_window()
    return driver


def get_next_conversation_path(data_dir, prefix="conversation", ext=".json"):
    """
    Scan data_dir for existing <prefix>_XXX<ext> files and
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


def build_conversation_json(
    user_chat_history,
    model_chat_history,
    conversation_id,
    title,
    model_display_name,
):
    """
    Build a conversation object in the shared JSON format.
    """
    messages = []

    for i, (user_msg, model_msg) in enumerate(zip(user_chat_history, model_chat_history)):
        messages.append({
            "id": f"u_{i}",
            "agent": "user",
            "role": "user",
            "content": user_msg,
        })

        messages.append({
            "id": f"m_{i}",
            "agent": "model",
            "role": "assistant",
            "content": model_msg,
        })

    conversation_obj = {
        "conversation_id": conversation_id,
        "title": title,
        "agents": {
            "user": {
                "id": "user",
                "display_name": "User",
                "type": "human",
            },
            "model": {
                "id": "model",
                "display_name": model_display_name,
                "type": "assistant",
            },
        },
        "messages": messages,
    }

    return conversation_obj


def export_conversation_json(
    json_path,
    user_chat_history,
    model_chat_history,
    conversation_id,
    title,
    model_display_name,
):
    """
    Build and write the conversation JSON to disk.
    """
    conversation_obj = build_conversation_json(
        user_chat_history=user_chat_history,
        model_chat_history=model_chat_history,
        conversation_id=conversation_id,
        title=title,
        model_display_name=model_display_name,
    )

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(conversation_obj, f, ensure_ascii=False, indent=2)
