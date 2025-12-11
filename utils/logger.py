import csv, os
from typing import List, Dict, Any

class CSVLogger:
    def __init__(self, path: str, header: List[str]):
        """
        Create a CSV logger.

        - Ensures the target directory exists.
        - Opens a CSV file for writing.
        - Writes a header row based on the provided field list.
        """
        self.path = path

        # Create parent directory when missing
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Open CSV file for writing; overwrite existing content
        self.file = open(path, "w", newline="", encoding="utf-8")

        # Configure a DictWriter for structured row output
        self.writer = csv.DictWriter(self.file, fieldnames=header)

        # Write header to the file
        self.writer.writeheader()

    def log(self, row: Dict[str, Any]):
        """
        Append a single row to the CSV file.
        The row must match the header's field names.
        """
        self.writer.writerow(row)

    def close(self):
        """
        Close the file handle to flush buffered data.
        """
        self.file.close()
