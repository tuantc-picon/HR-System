


@staticmethod
def is_cv_email(message):
    subject = ""
    headers = message["payload"].get("headers", [])
    for h in headers:
        if h["name"].lower() == "subject":
            subject = h["value"]

    parts = message["payload"].get("parts", [])
    has_attachment = any(p.get("filename") for p in parts if p.get("filename"))
    keywords = ["cv", "resume", "ứng tuyển", "apply"]

    if has_attachment and any(kw in subject.lower() for kw in keywords):
        return True
    return False