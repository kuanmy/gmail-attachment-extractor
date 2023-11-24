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
        patterns = [
            # 1st pattern: [moduleShortForm] #[refNo]
            (r"(RQ|PR|PO|PRQ|Payment Service) #\S*", " #"),
            # 2nd pattern: [moduleShortForm] Approval of [refNo]
            (r"(RQ|PR|PO|PRQ) Approval of \S*", " Approval of "),
            # 3rd pattern: [moduleShortForm] Approval [refNo]
            (r"(RQ|PR|PO|PRQ) Approval \S*", " Approval "),
            # 4th pattern: [moduleShortForm] Reviewer [refNo]
            (r"(RQ|PR|PO|PRQ) Reviewer \S*", " Reviewer ")
        ]

        for pattern, split_key in patterns:
            matching_substring = re.search(pattern, self.subject)
            if matching_substring is not None:
                module_ref_no = matching_substring.group().split(split_key)
                return tuple(module_ref_no)

        return None

