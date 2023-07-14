from attachment import Attachment

class Message:
    def __init__(self, id: str, subject: str) -> None:
        self.id = id
        self.subject = subject
        self.attachments = []


    def add_attachment(self, attachment: Attachment) -> None:
        self.attachments.append(attachment)

