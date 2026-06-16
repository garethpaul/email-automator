def _normalize_content_id(value):
    if value is None:
        return None
    value = value.strip()
    if value.startswith("<") and value.endswith(">"):
        return value[1:-1]
    return value


def _related_root(part):
    children = part.get_payload()
    if not children:
        return None
    start = part.get_param("start")
    if start is None:
        return children[0]
    expected_content_id = _normalize_content_id(start)
    for child in children:
        if _normalize_content_id(child.get("Content-ID")) == expected_content_id:
            return child
    return None


def select_inline_body_parts(message):
    html = []
    text = []

    def collect(part):
        disposition = (part.get("Content-Disposition", "") or "").split(";", 1)[0]
        if disposition.strip().lower() == "attachment" or part.get_filename():
            return
        content_type = part.get_content_type()
        if content_type == "message/rfc822":
            return
        if content_type == "multipart/related":
            root = _related_root(part)
            if root is not None:
                collect(root)
            return
        if part.is_multipart():
            for child in part.get_payload():
                collect(child)
            return
        if content_type == "text/plain":
            text.append(part)
        elif content_type == "text/html":
            html.append(part)

    collect(message)
    return html, text
