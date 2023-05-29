import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailAttachmentExtractor:
    def __init__(self) -> None:
        self.set_creds()
        self.service = build('gmail', 'v1', credentials=self.creds)


    def set_creds(self):
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


    def get_message_ids(self, query='', labelIds=[]):
        """ Get message ids that fulfill the specified query condition, and comes with attachments """
        query += ' has:attachment'
        results = self.service.users().messages().list(userId='me',q=query, labelIds=labelIds, fields='messages(id),nextPageToken').execute()
        messages = []
        if 'messages' in results:
            messages.extend(list(map(lambda msg: msg['id'], results['messages'])))
        while 'nextPageToken' in results:
            page_token = results['nextPageToken']
            results = self.service.users().messages().list(userId='me',q=query, pageToken=page_token, fields='messages(id),nextPageToken').execute()
            if 'messages' in results:
                messages.extend(list(map(lambda msg: msg['id'], results['messages'])))
        return messages


if __name__ == '__main__':
    extractor = GmailAttachmentExtractor()
    message_ids = extractor.get_message_ids()