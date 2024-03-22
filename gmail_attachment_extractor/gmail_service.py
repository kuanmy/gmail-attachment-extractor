import base64
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List

from gmail_attachment_extractor.attachment import Attachment
from gmail_attachment_extractor.message import Message


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailService:
    """Service class to interact with Gmail API.

    Attributes
    ----------
    service: Any
        Resource object for interacting with the Gmail API. Constructed
        based on the gmail user credentials configured.
    """

    def __init__(self) -> None:
        self.__set_creds()
        self.service = build("gmail", "v1", credentials=self.creds)

    def get_label_ids(self) -> List[str]:
        """Get the list of gmail label ids.

        Returns
        -------
        List[str]
            A list of ids of the gmail labels.
        """
        results = self.service.users().labels().list(userId="me").execute()
        label_ids = []
        if "labels" in results:
            label_ids = list(map(lambda label: label["id"], results["labels"]))
        return label_ids

    def get_message(self, message_id: str) -> Message:
        """Get the gmail message of given id and its attachments.

        Parameters
        ----------
        message_id: str
            Id of the gmail message to get.

        Returns
        -------
        Message
            A Message object.
        """
        try:
            # Query gmail message from API
            message = (
                self.service.users()
                .messages()
                .get(userId="me", id=message_id, fields="payload(headers,parts)")
                .execute()
            )
            payload = message["payload"]

            # Extract gmail subject from headers
            subject = ""
            for header in payload.get("headers", []):
                if header.get("name").lower() == "subject":
                    subject = header.get("value")

            # Create Message object
            message_obj = Message(id=message_id, subject=subject)

            # Get gmail attachments
            for part in payload.get("parts", []):
                if part["filename"]:
                    # Get attachment data
                    if "data" in part["body"]:
                        # Can directly get data if already included in body
                        atch_data = part["body"]["data"]
                    else:
                        # Query attachment data from API
                        atch_id = part["body"]["attachmentId"]
                        atch = (
                            self.service.users()
                            .messages()
                            .attachments()
                            .get(userId="me", messageId=message_id, id=atch_id)
                            .execute()
                        )
                        atch_data = atch["data"]

                    # Create Attachment object
                    atch_name = part["filename"]
                    atch_content = base64.urlsafe_b64decode(atch_data.encode("UTF-8"))
                    atch_obj = Attachment(filename=atch_name, file_content=atch_content)

                    # Assign Attachment object to Message object
                    message_obj.add_attachment(atch_obj)

            return message_obj

        except HttpError as error:
            print("An error occurred: %s" % error)

    def get_message_ids(self, query: str = "") -> List[str]:
        """Get the list of gmail message ids that fulfill the given query condition,
        and comes with attachments.

        Parameters
        ----------
        query: str, Optional
            Query conditions to filter the gmail message ids with. (default is "").

        Returns
        -------
        List[str]
            List of gmail message ids
        """
        # Query gmail message ids from API
        query += " has:attachment"
        results = (
            self.service.users()
            .messages()
            .list(userId="me", q=query, fields="messages(id),nextPageToken")
            .execute()
        )
        messages = []
        if "messages" in results:
            messages.extend(list(map(lambda msg: msg["id"], results["messages"])))

        # Repeat process if has next page
        while "nextPageToken" in results:
            page_token = results["nextPageToken"]
            results = (
                self.service.users()
                .messages()
                .list(
                    userId="me",
                    q=query,
                    pageToken=page_token,
                    fields="messages(id),nextPageToken",
                )
                .execute()
            )
            if "messages" in results:
                messages.extend(list(map(lambda msg: msg["id"], results["messages"])))
        return messages

    def __set_creds(self) -> None:
        """Set the credentials for authenticating the Gmail API service. Activate
        gmail authentication flow based on configured user credentials if no
        token.json found.
        """
        self.creds = None
        # If token.json exists
        if os.path.exists("../creds/token.json"):
            # Initialize credentials from token
            self.creds = Credentials.from_authorized_user_file(
                "../creds/token.json", SCOPES
            )

        # If no valid credentials
        if not self.creds or not self.creds.valid:
            # If credentials already expired but can be refreshed
            if self.creds and self.creds.expired and self.creds.refresh_token:
                # Refresh credentials
                self.creds.refresh(Request())
            else:
                os.makedirs(os.path.dirname("../creds"), exist_ok=True)
                # Activate authentication flow for user to login
                flow = InstalledAppFlow.from_client_secrets_file(
                    "../creds/credentials.json", SCOPES
                )
                self.creds = flow.run_local_server(port=0)

                # Save the credentials into token.json for the next run
                with open("../creds/token.json", "w") as token:
                    token.write(self.creds.to_json())
