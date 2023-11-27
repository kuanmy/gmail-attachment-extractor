import os
import argparse

from gmail_service import GmailService
from logger import CsvLogger, TxtLogger
from typing import List


def extract_gmail_attachments(output_atch_dir: str, output_record_log_path: str, output_error_log_path: str, processed_record_log_path: str) -> None:
    service = GmailService()
    all_message_ids = service.get_message_ids()
    message_ids = all_message_ids
    
    processed_message_ids = TxtLogger.read(processed_record_log_path + '.txt')
    processed_message_ids = set(processed_message_ids)
    message_ids = [message_id for message_id in all_message_ids if message_id not in processed_message_ids]

    for message_id in message_ids:
        message = service.get_message(message_id)            

        module_ref_no = message.get_module_ref_no()
        if module_ref_no is None:
            module = ref_no = 'Uncategorized'
            CsvLogger.write(output_error_log_path + '.csv', [message.id, "Module Ref No not found for subject: " + message.subject])
        else:
            (module, ref_no) = module_ref_no
        for attachment in message.attachments:
            attachment.save(dir=os.path.join(output_atch_dir, module, ref_no))
        TxtLogger.write(output_record_log_path + '.txt', message.id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output-atch-dir', dest='output_atch_dir', default='')
    parser.add_argument('--output-record-log-path', dest='output_record_log_path', default='record_log')
    parser.add_argument('--output-error-log-path', dest='output_error_log_path', default='error_log')
    parser.add_argument('--processed-record-log-path', dest='processed_record_log_path', default='record_log')
    args = parser.parse_args()

    extract_gmail_attachments(args.output_atch_dir, args.output_record_log_path, args.output_error_log_path, args.processed_record_log_path)