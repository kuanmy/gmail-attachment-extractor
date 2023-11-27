import re

from attachment import Attachment
from typing import Optional, Tuple


class Message:
    def __init__(self, id: str, subject: str) -> None:
        self.id = id
        self.subject = subject
        self.attachments = []


    def add_attachment(self, attachment: Attachment) -> None:
        self.attachments.append(attachment)

    
    def get_module_ref_no(self) -> Optional[Tuple[str, str]]:
        matching_substring = re.search(r"(RQ|PR|PO|PRQ #\S*")
        if matching_substring is not None:
            module_ref_no = matching_substring.group().split(" #")
            return tuple(module_ref_no)
        else:
            return None

