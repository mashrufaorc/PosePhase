import csv, os
from typing import List, Dict, Any

class CSVLogger:
    def __init__(self, path: str, header: List[str]):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.file = open(path, "w", newline="", encoding="utf-8")
        self.writer = csv.DictWriter(self.file, fieldnames=header)
        self.writer.writeheader()

    def log(self, row: Dict[str, Any]):
        self.writer.writerow(row)

    def close(self):
        self.file.close()
