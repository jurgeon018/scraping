from csvwriter import DictWriter, CsvWriter
try:
    # Python 2
    from StringIO import StringIO
except:
    # Python 3
    from io import StringIO
import csv
import pytest


def test_dictwriter_append():
    fileobj = StringIO()
    writer1 = DictWriter(fileobj, fieldnames=["f1", "f2", "f3"])
    writer1.writeheader()
    assert fileobj.getvalue() == "f1,f2,f3\r\n"
    writer1.writerow({"f1": 1, "f2": "abc", "f3": "f"})
    assert fileobj.getvalue() == "f1,f2,f3\r\n1,abc,f\r\n"

    writer2 = DictWriter.append(fileobj)
    writer2.writerow({"f1": 2, "f2": 5, "f3": "xyz"})
    assert fileobj.getvalue() == "f1,f2,f3\r\n1,abc,f\r\n2,5,xyz\r\n"


def test_dictwriter_append_header_only():
    fileobj = StringIO()
    writer1 = DictWriter(fileobj, fieldnames=["f1", "f2", "f3"])
    writer1.writeheader()
    assert fileobj.getvalue() == "f1,f2,f3\r\n"

    writer2 = DictWriter.append(fileobj)
    writer2.writerow({"f1": 2, "f2": 5, "f3": "xyz"})
    assert fileobj.getvalue() == "f1,f2,f3\r\n2,5,xyz\r\n"


def test_dictwriter_append_empty():
    fileobj = StringIO()
    with pytest.raises(ValueError):
        writer = DictWriter.append(fileobj)


def test_dictwriter_append_empty_fieldnames():
    fileobj = StringIO()
    writer = DictWriter.append(fileobj, fieldnames=["f1", "f2", "f3"])
    writer.writeheader()
    writer.writerow({"f1": 2, "f2": 5, "f3": "xyz"})
    assert fileobj.getvalue() == "f1,f2,f3\r\n2,5,xyz\r\n"


def test_csvwriter_write():
    fileobj = StringIO()
    writer = CsvWriter(fileobj)
    writer.writerow({"f1": 2, "f2": 5, "f3": "xyz"})

    reader = csv.DictReader(StringIO(fileobj.getvalue()))
    assert list(reader) == [{"f1": '2', "f2": '5', "f3": "xyz"}]


def test_csvwriter_lshift():
    fileobj = StringIO()
    writer = CsvWriter(fileobj)
    writer << [{"f1": 2, "f2": 5, "f3": "xyz"}, {"f1": 1, "f2": "abc", "f3": "f"}]
    writer << {"f1": 2, "f2": 5, "f3": "xyz"}

    reader = csv.DictReader(StringIO(fileobj.getvalue()))
    assert list(reader) == [{"f1": '2', "f2": '5', "f3": "xyz"},
                            {"f1": '1', "f2": "abc", "f3": "f"},
                            {"f1": '2', "f2": '5', "f3": "xyz"}]


def test_csvwriter_append():
    fileobj = StringIO()
    writer1 = CsvWriter(fileobj)
    writer1 << [{"f1": 2, "f2": 5, "f3": "xyz"}, {"f1": 1, "f2": "abc", "f3": "f"}]

    writer2 = CsvWriter(fileobj)
    writer2 << {"f1": 2, "f2": 5, "f3": "xyz"}

    reader = csv.DictReader(StringIO(fileobj.getvalue()))
    assert list(reader) == [{"f1": '2', "f2": '5', "f3": "xyz"},
                            {"f1": '1', "f2": "abc", "f3": "f"},
                            {"f1": '2', "f2": '5', "f3": "xyz"}]


def test_csvwriter_doesnt_close():
    fileobj = StringIO()
    writer = CsvWriter(fileobj)
    writer << {"f1": 2, "f2": 5, "f3": "xyz"}
    assert not fileobj.closed


def test_csvwriter_with_closes():
    fileobj = StringIO()
    with CsvWriter(fileobj) as writer:
        writer << {"f1": 2, "f2": 5, "f3": "xyz"}
    assert fileobj.closed
