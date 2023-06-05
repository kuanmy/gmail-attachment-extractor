import base64
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailAttachmentExtractor:
    def __init__(self) -> None:
        self.__set_creds()
        self.service = build('gmail', 'v1', credentials=self.creds)


    def get_message_ids(self, query: str = '') -> list:
        """ Get message ids that fulfill the specified query condition, and comes with attachments """
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


    def store_message_attachments(self, message_id: str, output_dir: str = '') -> None:
        """Get and store attachments from the message of specified id."""
        try:
            message = self.service.users().messages().get(userId='me', id=message_id, fields='payload(headers,parts)').execute()
            payload = message['payload']

            for part in payload.get('parts', ''):
                if part['filename']:
                    if 'data' in part['body']:
                        atch_data = part['body']['data']
                    else:
                        atch_id = part['body']['attachmentId']
                        atch = self.service.users().messages().attachments().get(userId='me', messageId=message_id, id=atch_id).execute()
                        atch_data = atch['data']
                    atch_content = base64.urlsafe_b64decode(atch_data.encode('UTF-8'))

                    output_atch_path = os.path.join(output_dir, part['filename'])
                    self.__store_attachment(output_atch_path, atch_content)

        except HttpError as error:
            print('An error occurred: %s' % error)  
    

    def __set_creds(self) -> None:
        """ Get and set the credentials for authenticating the Gmail API service """
        self.creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())


    def __store_attachment(self, output_atch_path: str, atch_content) -> None:
        """ Store attachment in specified path """
        os.makedirs(os.path.dirname(output_atch_path), exist_ok=True)
        with open(output_atch_path, 'wb') as f:
            f.write(atch_content)


if __name__ == '__main__':
    extractor = GmailAttachmentExtractor()
    message_ids = extractor.get_message_ids()
    for message_id in message_ids:
        extractor.store_message_attachments(message_id)