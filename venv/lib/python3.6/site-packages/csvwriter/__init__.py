import csv
import io
import itertools


class DictWriter(csv.DictWriter):
    @classmethod
    def append(cls, f, fieldnames=None, writeheader=False, **kwargs):
        curpos = f.tell()
        if curpos > 0:
            f.seek(0)
            reader = csv.reader(f)
            fieldnames = next(reader)
            f.seek(curpos)
        elif fieldnames is None:
            raise ValueError("Can't append to an empty file.")
        inst = cls(f, fieldnames, **kwargs)
        if curpos == 0 and writeheader:
            inst.writeheader()
        return inst


class CsvWriter:
    def __init__(self, fileobj):
        self.fileobj = fileobj
        self.writer = None
        self.entered = False

    def writerow(self, row):
        if self.writer is None:
            self.writer = DictWriter.append(self.fileobj, fieldnames=row.keys(), writeheader=True)
        self.writer.writerow(row)

    def writerows(self, rows):
        if self.writer is None:
            rows = iter(rows)
            firstrow = next(rows)
            fieldnames = firstrow.keys()

            self.writer = DictWriter.append(self.fileobj, fieldnames=fieldnames, writeheader=True)
            self.writer.writerow(firstrow)
        self.writer.writerows(rows)

    # backward compatibility
    append_row = writerow
    append_rows = writerows

    def __lshift__(self, new_rows):
        if isinstance(new_rows, dict):
            self.writerow(new_rows)
        else:
            self.writerows(new_rows)

    def __enter__(self):
        self.entered = True
        if hasattr(self.fileobj, 'open'):
            # assume Path object, for backward compatibility
            self.fileobj = self.fileobj.open('w')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.entered:
            self.fileobj.close()
        if exc_type:
            return
