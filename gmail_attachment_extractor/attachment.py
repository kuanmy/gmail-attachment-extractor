import os

class Attachment:
    def __init__(self, filename: str, file_content) -> None:
        self.filename = filename
        self.file_content = file_content


    def save(self, dir: str = '') -> None:
        os.makedirs(dir, exist_ok=True)
        with open(os.path.join(dir, self.filename), 'wb') as f:
            f.write(self.file_content)