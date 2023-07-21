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
        module_ref_no = None

        # 1st pattern: [moduleShortForm] #[refNo]
        module_ref_no = re.search(r"(RQ|PR|PO|PRQ) #\S*", self.subject)
        if module_ref_no is not None:
            module_ref_no = module_ref_no.group().split(" #")

        # 2nd pattern: [moduleShortForm] Approval [refNo]
        module_ref_no = re.search(r"(RQ|PR|PO|PRQ) Approval \S*", self.subject)
        if module_ref_no is not None:
            module_ref_no = module_ref_no.group().split(" Approval ")

        # 3rd pattern: [moduleShortForm] Reviewer [refNo]
        module_ref_no = re.search(r"(RQ|PR|PO|PRQ) Reviewer \S*", self.subject)
        if module_ref_no is not None:
            module_ref_no = module_ref_no.group().split(" Reviewer ")
            
        return tuple(module_ref_no) if module_ref_no is not None else None

