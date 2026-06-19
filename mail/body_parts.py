MAX_MIME_DEPTH = 64
MAX_MIME_PARTS = 256


def _normalize_content_id(value):
    if value is None:
        return None
    value = value.strip()
    if value.startswith("<") and value.endswith(">"):
        return value[1:-1]
    return value


def _related_root(part):
    children = part.get_payload()
    if not isinstance(children, (list, tuple)) or not children:
        return None
    start = part.get_param("start")
    if start is None:
        return children[0]
    expected_content_id = _normalize_content_id(start)
    matches = [
        child
        for child in children
        if _normalize_content_id(child.get("Content-ID")) == expected_content_id
    ]
    if len(matches) != 1:
        return None
    return matches[0]


def select_inline_body_parts(message):
    html = []
    text = []

    def collect(root):
        stack = [(root, 0)]
        seen = set()
        part_count = 0
        while stack:
            part, depth = stack.pop()
            part_count += 1
            if depth > MAX_MIME_DEPTH or part_count > MAX_MIME_PARTS:
                return False
            part_identity = id(part)
            if part_identity in seen:
                return False
            seen.add(part_identity)

            if part.get_content_maintype() == "message":
                continue
            disposition = (part.get("Content-Disposition", "") or "").split(";", 1)[0]
            if disposition.strip().lower() == "attachment" or part.get_filename():
                continue
            content_type = part.get_content_type()
            if content_type == "message/rfc822":
                continue
            if content_type == "multipart/related":
                root = _related_root(part)
                if root is None:
                    return False
                stack.append((root, depth + 1))
                continue
            if part.is_multipart():
                children = part.get_payload()
                if not isinstance(children, (list, tuple)):
                    return False
                for child in reversed(children):
                    stack.append((child, depth + 1))
                continue
            if content_type == "text/plain":
                text.append(part)
            elif content_type == "text/html":
                html.append(part)
        return True

    if not collect(message):
        return [], []
    return html, text
