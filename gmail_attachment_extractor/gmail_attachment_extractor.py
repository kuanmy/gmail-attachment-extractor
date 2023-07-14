from gmail_service import GmailService

# params:
# output dir
# processing logs filepath

service = GmailService()
all_message_ids = service.get_message_ids()
for message_id in all_message_ids:
    message = service.get_message(message_id)

    # Get atch dir based on messages subject
    # Handle error case - no message, cannot determine atch dir

    for attachment in message.attachments:
        attachment.save()