import csv
import os

from abc import ABC, abstractmethod
from typing import List


class Logger(ABC):
    """Abstract class for log I/O operations."""

    @staticmethod
    @abstractmethod
    def write(log_file_path: str, data) -> None:
        """Write data into given log file path.

        Parameters
        ----------
        log_file_path: str
            File path of the log file to write into.
        data: Any
            Data to write into log file.
        """
        pass

    @staticmethod
    @abstractmethod
    def read(log_file_path: str) -> List:
        """Read data from given log file path.

        Parameters
        ----------
        log_file_path: str
            File path of the log file to read from.

        Returns
        -------
        List[Any]
            A list of data read from the log file.
        """
        pass


class TxtLogger(Logger):
    """Logger for text log files."""

    @staticmethod
    def write(log_file_path: str, data) -> None:
        if not log_file_path.endswith(".txt"):
            log_file_path += ".txt"

        dirname = os.path.dirname(log_file_path)
        if os.path.isdir(dirname):
            os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

        with open(log_file_path, "a") as f:
            f.write(data + "\n")

    @staticmethod
    def read(log_file_path: str) -> List:
        logs = []

        if not log_file_path.endswith(".txt"):
            log_file_path += ".txt"

        if os.path.exists(log_file_path):
            with open(log_file_path) as f:
                logs = f.read().splitlines()

        return logs


class CsvLogger(Logger):
    """Logger for csv log files."""

    @staticmethod
    def write(log_file_path: str, data) -> None:
        if not log_file_path.endswith(".csv"):
            log_file_path += ".csv"

        dirname = os.path.dirname(log_file_path)
        if os.path.isdir(dirname):
            os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

        with open(log_file_path, "a", newline="\n") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(data)

    @staticmethod
    def read(log_file_path: str) -> List:
        logs = []

        if not log_file_path.endswith(".csv"):
            log_file_path += ".csv"

        if os.path.exists(log_file_path):
            with open(log_file_path) as f:
                reader = csv.reader(f, delimiter=",")
                logs = [row for row in reader]

        return logs
