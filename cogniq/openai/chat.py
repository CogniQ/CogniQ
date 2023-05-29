def message(role, content):
    return {"role": f"{role}", "content": f"{content}"}


def user_message(content):
    return message("user", content)


def system_message(content):
    return message("system", content)


def assistant_message(content):
    return message("assistant", content)


def message_to_string(message):
    return f"{message['role']}: {message['content']}"