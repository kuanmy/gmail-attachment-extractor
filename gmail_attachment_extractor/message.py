import re

from attachment import Attachment
from typing import Optional, Tuple


class Message:
    """Class that represents a gmail message.

    Attributes
    ----------
    id: str
        Id of the gmail message.
    subject: str
        The gmail's subject.
    attachments: List[Attachment]
        List of Attachment object attached with the gmail.
    """

    def __init__(self, id: str, subject: str) -> None:
        """
        Parameters
        ----------
        id: str
            Id of the gmail message.
        subject: str
            The gmail's subject.
        """
        self.id = id
        self.subject = subject
        self.attachments = []

    def add_attachment(self, attachment: Attachment) -> None:
        """Add attachment for the message.

        Parameters
        ----------
        attachment: Attachment
            Attachment object to be added for the message.
        """
        self.attachments.append(attachment)

    def get_module_ref_no(self) -> Optional[Tuple[str, str]]:
        """Get module and ref no of gmail message.

        Module and ref no extracted from gmail subject using the template
        {module} #{ref_no}, where module must be RQ/PR/PO.

        Returns
        -------
        Optional[Tuple[str, str]]
            A tuple containing both module (RQ/PR/PO) and ref no. If either
            module or ref no not exists, return None.
        """
        matching_substring = re.search(r"(RQ|PR|PO #\S*")
        if matching_substring is not None:
            module_ref_no = matching_substring.group().split(" #")
            return tuple(module_ref_no)
        else:
            return None
