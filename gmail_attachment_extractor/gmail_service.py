import base64
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from attachment import Attachment
from message import Message


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailService:
    def __init__(self) -> None:
        self.__set_creds()
        self.service = build('gmail', 'v1', credentials=self.creds)

    
    def get_label_ids(self):
        results = self.service.users().labels().list(userId='me').execute()
        label_ids = []
        if 'labels' in results:
            label_ids = list(map(lambda label: label['id'], results['labels']))
        return label_ids


    def get_message(self, message_id: str) -> Message:
        """Get and store attachments from the message of specified id."""
        try:
            message = self.service.users().messages().get(userId='me', id=message_id, fields='payload(headers,parts)').execute()
            payload = message['payload']

            # Extract message subject from headers
            subject = ''
            for header in payload.get('headers', []):
                if header.get('name').lower() == 'subject':
                    subject = header.get('value')
        
            # Create message object
            message_obj = Message(
                id=message_id,
                subject=subject
            )

            # Get message attachments
            for part in payload.get('parts', []):
                if part['filename']:
                    # Get attachment data
                    if 'data' in part['body']:
                        atch_data = part['body']['data']
                    else:
                        atch_id = part['body']['attachmentId']
                        atch = self.service.users().messages().attachments().get(userId='me', messageId=message_id, id=atch_id).execute()
                        atch_data = atch['data']
                    
                    # Create attachment object
                    atch_name = part['filename']
                    atch_content = base64.urlsafe_b64decode(atch_data.encode('UTF-8'))
                    atch_obj = Attachment(
                        filename=atch_name,
                        file_content=atch_content
                    )

                    # Assign attachment to message object
                    message_obj.add_attachment(atch_obj)

            return message_obj

        except HttpError as error:
            print('An error occurred: %s' % error)


    def get_message_ids(self, query: str = '') -> list:
        """Get message ids that fulfill the specified query condition, and comes with attachments """
        query += ' has:attachment'
        results = self.service.users().messages().list(userId='me', q=query, fields='messages(id),nextPageToken').execute()
        messages = []
        if 'messages' in results:
            messages.extend(list(map(lambda msg: msg['id'], results['messages'])))
        while 'nextPageToken' in results:
            page_token = results['nextPageToken']
            results = self.service.users().messages().list(userId='me', q=query, pageToken=page_token, fields='messages(id),nextPageToken').execute()
            if 'messages' in results:
                messages.extend(list(map(lambda msg: msg['id'], results['messages'])))
        return messages


    def __set_creds(self) -> None:
        """Get and set the credentials for authenticating the Gmail API service """
        self.creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('../creds/token.json'):
            self.creds = Credentials.from_authorized_user_file('../creds/token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                os.makedirs(os.path.dirname('../creds'), exist_ok=True)
                flow = InstalledAppFlow.from_client_secrets_file('../creds/credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('../creds/token.json', 'w') as token:
                token.write(self.creds.to_json())