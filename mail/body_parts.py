def select_inline_body_parts(message):
    html = []
    text = []

    def collect(part):
        disposition = (part.get("Content-Disposition", "") or "").split(";", 1)[0]
        if disposition.strip().lower() == "attachment" or part.get_filename():
            return
        if part.is_multipart():
            for child in part.get_payload():
                collect(child)
            return
        content_type = part.get_content_type()
        if content_type == "text/plain":
            text.append(part)
        elif content_type == "text/html":
            html.append(part)

    collect(message)
    return html, text
