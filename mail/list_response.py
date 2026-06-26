MAX_MESSAGE_SUMMARIES = 30


def bounded_message_summaries(response):
    if not isinstance(response, dict):
        return []
    messages = response.get("messages", [])
    if not isinstance(messages, (list, tuple)):
        return []
    return list(messages[:MAX_MESSAGE_SUMMARIES])
