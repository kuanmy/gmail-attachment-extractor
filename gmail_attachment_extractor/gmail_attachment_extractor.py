import os

from gmail_service import GmailService
from logger import CsvLogger, TxtLogger
from typing import List

def extract_gmail_attachments(output_atch_dir: str = '', output_error_log_path: str = 'error_log', output_record_log_path: str = 'record_log', processed_record_log_paths: List[str] = []) -> None:
    service = GmailService()
    all_message_ids = service.get_message_ids()
    message_ids = all_message_ids
    
    processed_message_ids = []
    for processed_record_log_path in processed_record_log_paths:
        processed_message_ids.extend(TxtLogger.read(processed_record_log_path + '.txt'))
    processed_message_ids = set(processed_message_ids)
    message_ids = [message_id for message_id in all_message_ids if message_id not in processed_message_ids]

    for message_id in message_ids:
        message = service.get_message(message_id)            

        module_ref_no = message.get_module_ref_no()
        if module_ref_no is None:
            CsvLogger.write(output_error_log_path + '.csv', [message.id, "Module Ref No not found for subject: " + message.subject])
        else:
            (module, ref_no) = module_ref_no
            for attachment in message.attachments:
                attachment.save(dir=os.join(output_atch_dir, module, ref_no))
            TxtLogger.write(output_record_log_path + '.txt', message.id)
    