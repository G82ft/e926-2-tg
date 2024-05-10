import csv
from io import StringIO
from logging import Formatter, LogRecord


class CsvFormatter(Formatter):
    def __init__(self, attrs: tuple[str, ...] = ('message',), datefmt: str = None) -> None:
        super().__init__(f"{{{'} {'.join(attrs)}}}", style='{', datefmt=datefmt)
        self.attrs: tuple = attrs
        self.output: StringIO = StringIO()
        self.writer = csv.writer(self.output, dialect='excel-tab', quoting=csv.QUOTE_ALL)

    def format(self, record: LogRecord) -> str:
        super().format(record)
        self.writer.writerow([record.__getattribute__(attr) for attr in self.attrs])
        data = self.output.getvalue()
        self.output.truncate(0)
        self.output.seek(0)
        return data.strip()

