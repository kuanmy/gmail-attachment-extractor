import csv
import os
from typing import List

from abc import ABC, abstractmethod


class Logger(ABC):

    @staticmethod
    @abstractmethod
    def write(log_file_path: str, data) -> None:
        pass

    @staticmethod
    @abstractmethod
    def read(log_file_path: str) -> List:
        pass


class TxtLogger(Logger):

    @staticmethod
    def write(log_file_path: str, data) -> None:
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        with open(log_file_path, 'a') as f:
            f.write(data + '\n')

    @staticmethod
    def read(log_file_path: str) -> List:
        logs = []
        if os.path.exists(log_file_path):
            with open(log_file_path) as f:
                logs = f.read().splitlines()
        return logs



class CsvLogger(Logger):

    @staticmethod
    def write(log_file_path: str, data) -> None:
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        with open(log_file_path, "a", newline='\n') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(data)

    @staticmethod
    def read(log_path: str) -> List:
        logs = []
        if os.path.exists(log_path):
            with open(log_path) as f:
                reader = csv.reader(f, delimiter=',')
                logs = [row for row in reader]
        return logs