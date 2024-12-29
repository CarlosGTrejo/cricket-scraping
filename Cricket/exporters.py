from scrapy.exporters import BaseItemExporter
import openpyxl

class ExcelItemExporter(BaseItemExporter):
    def __init__(self, file, **kwargs):
        super().__init__(**kwargs)
        self.file = file
        self.wb = openpyxl.Workbook()
        self.ws = self.wb.active
        self.headers_written = False

    def export_item(self, item):
        if not self.headers_written:
            # Write headers
            headers = list(item.keys())
            self.ws.append(headers)
            self.headers_written = True

        # Write item values
        row = self.ws.max_row + 1
        self.ws.append(list(item.values()))

    def finish_exporting(self):
        self.wb.save(self.file) 