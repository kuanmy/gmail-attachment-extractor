import os
import argparse

from gmail_attachment_extractor import GmailService
from gmail_attachment_extractor.logger import CsvLogger, TxtLogger


def extract_gmail_attachments(
    output_atch_dir: str,
    output_record_log_path: str,
    output_error_log_path: str,
    processed_record_log_path: str,
) -> None:
    """Extract gmail attachments.

    The extracted gmail attachments will be stored in the following structure:
        {output_atch_dir}/
            {module}/
                {ref_no}/
                    {attachment_file}
            Uncategorized/
                {attachment_file}

    Parameters
    ----------
    output_atch_dir: str
        Directory to store the extracted gmail attachment outputs.
    output_record_log_path: str
        .txt file path to store the logs of current processing output's gmail records.
        Log will store the list of gmail ids that are processed in current run.
    output_error_log_path: str
        .csv file path to store the logs of gmail attachment extraction errors.
        Log will store the gmail id + error message if error occurred during extraction process.
    processed_record_log_path: str
        .txt file path to store the logs of previously processed gmail records.
        Log should store the list of gmail ids that were processed in previous runs.
        Gmails recorded in the log will not be processed again.
    """
    service = GmailService()
    # Get ids of gmail messages that have attachments
    all_message_ids = service.get_message_ids()
    message_ids = all_message_ids

    # Filter out previously processed gmail message ids
    processed_message_ids = TxtLogger.read(processed_record_log_path)
    processed_message_ids = set(processed_message_ids)
    message_ids = [
        message_id
        for message_id in all_message_ids
        if message_id not in processed_message_ids
    ]

    for message_id in message_ids:
        # Get gmail message
        message = service.get_message(message_id)

        # Get module and ref no
        module_ref_no = message.get_module_ref_no()
        if module_ref_no is None:
            module = ref_no = "Uncategorized"
            # Log error
            CsvLogger.write(
                output_error_log_path,
                [message.id, "Module Ref No not found for subject: " + message.subject],
            )
        else:
            (module, ref_no) = module_ref_no

        # Save attachment based on module and ref no
        for attachment in message.attachments:
            attachment.save(dir=os.path.join(output_atch_dir, module, ref_no))

        # Log processed gmail message
        TxtLogger.write(output_record_log_path, message.id)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--output-atch-dir",
        dest="output_atch_dir",
        default="",
        help="Directory to store the extracted gmail attachment outputs. Default is current directory.",
    )
    parser.add_argument(
        "--output-record-log-path",
        dest="output_record_log_path",
        default="record_log.txt",
        help=".txt file path to store the logs of current processing output's gmail records. Default is record_log.txt",
    )
    parser.add_argument(
        "--output-error-log-path",
        dest="output_error_log_path",
        default="error_log.csv",
        help=".csv file path to store the logs of gmail attachment extraction errors. Default is error_log.csv",
    )
    parser.add_argument(
        "--processed-record-log-path",
        dest="processed_record_log_path",
        default="record_log.txt",
        help=".txt file path to store the logs of previously processed gmail records. \
            Gmails recorded in the log will not be processed again. Default is record_log.txt",
    )
    args = parser.parse_args()
    extract_gmail_attachments(
        args.output_atch_dir,
        args.output_record_log_path,
        args.output_error_log_path,
        args.processed_record_log_path,
    )


if __name__ == "__main__":
    main()
