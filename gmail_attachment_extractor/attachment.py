import os
from typing import Any


class Attachment:
    """Class that represents an attachment.

    Attributes
    ----------
    filename: str
        File name of attachment (including extension).
    file_content
        Content of the attachment file.
    """

    def __init__(self, filename: str, file_content: Any) -> None:
        """
        Parameters
        ----------
        filename: str
            File name of attachment (including extension).
        file_content: Any
            Content of the attachment file.
        """
        self.filename = filename
        self.file_content = file_content

    def save(self, dir: str = "") -> None:
        """Save attachment to given directory.

        Parameters
        ----------
        dir: str, optional
            Directory to save attachment to (default is "").
        """
        os.makedirs(dir, exist_ok=True)
        with open(os.path.join(dir, self.filename), "wb") as f:
            f.write(self.file_content)
