import unittest
from datetime import datetime
from pprint import pformat
from pathlib import Path
from unittest import mock
import shutil
import tempfile
from getfiles.GetFiles import (
    get_files,
    get_files_iterator,
    get_folder_and_file_count,
    process_file,
    get_folder_size,
    get_folders
)


class TestGetFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.temp_directory_structure = cls.create_temp_directory_structure()

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def mock_stat(self, path, creation_time, modification_time):
        mock_stat = mock.Mock()
        real_stat = path.stat()
        mock_stat.st_ctime = creation_time
        mock_stat.st_mtime = modification_time
        mock_stat.st_size = real_stat.st_size
        mock_stat.st_mode = real_stat.st_mode

        patcher = mock.patch.object(Path, "stat", return_value=mock_stat)
        self.addCleanup(patcher.stop)
        patcher.start()

    @classmethod
    def create_temp_directory_structure(cls):
        temp_dir = Path(cls.temp_dir.name)
        temp_dir.mkdir(exist_ok=True)

        # Create text files
        (temp_dir / "file1.txt").write_text("File 1 content")
        (temp_dir / "file2.txt").write_text("File 2 content")

        # Create files in the root directory with different extensions
        (temp_dir / "file9.md").write_text("# Markdown file")
        (temp_dir / "file10.py").write_text("print('Python file')")
        (temp_dir / "file11.html").write_text(
            "<html><body>HTML file</body></html>"
        )

        # Create a subdirectory and files within it
        sub_dir = temp_dir / "sub_dir"
        sub_dir.mkdir(exist_ok=True)
        (sub_dir / "file3.txt").write_text("File 3 content")
        (sub_dir / "file4.log").write_text("Log file content")
        (sub_dir / "file5.csv").write_text("CSV file content")

        # Create another subdirectory and files within it
        another_sub_dir = temp_dir / "another_sub_dir"
        another_sub_dir.mkdir(exist_ok=True)
        (another_sub_dir / "file6.txt").write_text("File 6 content")
        (another_sub_dir / "file7.json").write_text('{"key": "value"}')
        (another_sub_dir / "file8.xml").write_text(
            "<root><element>Value</element></root>"
        )

        # Create a nested subdirectory and files within it
        nested_sub_dir = another_sub_dir / "nested_sub_dir"
        nested_sub_dir.mkdir(exist_ok=True)
        (nested_sub_dir / "file12.txt").write_text("File 12 content")
        (nested_sub_dir / "file13.js").write_text(
            "console.log('JavaScript file')"
        )
        (nested_sub_dir / "file14.css").write_text(
            "body { background-color: #fff; }"
        )

        return temp_dir

    def test_get_files_string_path(self):
        temp_dir = str(self.temp_directory_structure)
        creation_time = datetime(2021, 1, 1).timestamp()
        modification_time = datetime(2022, 1, 1).timestamp()
        # Mock the stat results for all files
        for file in self.temp_directory_structure.rglob("*"):
            if file.is_file():
                self.mock_stat(file, creation_time, modification_time)

        result = get_files(temp_dir, extensions=[".txt"])

        expected = [
            {"path": Path(temp_dir) / "file1.txt",
             "datetime": "2022-01-01 00:00:00"},
            {"path": Path(temp_dir) / "file2.txt",
             "datetime": "2022-01-01 00:00:00"},
            {"path": Path(temp_dir) / "sub_dir" / "file3.txt",
             "datetime": "2022-01-01 00:00:00"},
            {"path": Path(temp_dir) / "another_sub_dir" /
             "file6.txt", "datetime": "2022-01-01 00:00:00"},
            {"path": Path(temp_dir) / "another_sub_dir" / "nested_sub_dir" /
             "file12.txt", "datetime": "2022-01-01 00:00:00"},
        ]
        result = sorted(result, key=lambda x: x["path"].name)
        print(f'result: {pformat(result, indent=4)}')
        expected = sorted(expected, key=lambda x: x["path"].name)
        for res, exp in zip(result, expected):
            self.assertEqual(res, exp)

    def test_get_files_no_read_permission(self):
        temp_dir = self.temp_directory_structure

        with mock.patch("os.access", return_value=False):
            with self.assertRaises(PermissionError) as context:
                get_files(temp_dir)

            self.assertEqual(
                str(context.exception),
                f"No read permission for directory {temp_dir}."
            )

    def test_get_files_all_files_as_datetime(self):
        temp_dir = self.temp_directory_structure
        creation_time = datetime(2021, 1, 1).timestamp()
        modification_time = datetime(2022, 1, 1).timestamp()

        for file in temp_dir.rglob("*"):
            if file.is_file():
                self.mock_stat(file, creation_time, modification_time)

        result = get_files(
            temp_dir,
            extensions=None,
            subfolders=True,
            time_type="created",
            as_date_time=True,
            str_format="%Y-%m-%d",
            get_size=False,
        )

        expected = [
            {"path": temp_dir / "file1.txt", "datetime": datetime(2021, 1, 1)},
            {"path": temp_dir / "file2.txt", "datetime": datetime(2021, 1, 1)},
            {"path": temp_dir / "sub_dir" / "file3.txt",
             "datetime": datetime(2021, 1, 1)},
            {"path": temp_dir / "sub_dir" / "file4.log",
             "datetime": datetime(2021, 1, 1)},
            {"path": temp_dir / "sub_dir" / "file5.csv",
             "datetime": datetime(2021, 1, 1)},
            {"path": temp_dir / "another_sub_dir" / "file6.txt",
             "datetime": datetime(2021, 1, 1)},
            {"path": temp_dir / "another_sub_dir" / "file7.json",
             "datetime": datetime(2021, 1, 1)},
            {"path": temp_dir / "another_sub_dir" / "file8.xml",
             "datetime": datetime(2021, 1, 1)},
            {"path": temp_dir / "file9.md", "datetime": datetime(2021, 1, 1)},
            {"path": temp_dir / "file10.py", "datetime": datetime(2021, 1, 1)},
            {"path": temp_dir / "file11.html",
             "datetime": datetime(2021, 1, 1)},
            {"path": temp_dir / "another_sub_dir" / "nested_sub_dir" /
                "file12.txt",
             "datetime": datetime(2021, 1, 1)},
            {"path": temp_dir / "another_sub_dir" / "nested_sub_dir" /
                "file13.js",
             "datetime": datetime(2021, 1, 1)},
            {"path": temp_dir / "another_sub_dir" / "nested_sub_dir" /
                "file14.css",
             "datetime": datetime(2021, 1, 1)},
        ]

        result = sorted(result, key=lambda x: x["path"].name)
        expected = sorted(expected, key=lambda x: x["path"].name)
        self.assertEqual(len(result), len(expected))
        for res, exp in zip(result, expected):
            self.assertEqual(res["path"].name, exp["path"].name)
            self.assertEqual(res["datetime"], exp["datetime"])

    def test_get_files_all_files_as_datetime_str(self):
        temp_dir = self.temp_directory_structure
        creation_time = datetime(2021, 1, 1).timestamp()
        modification_time = datetime(2022, 1, 1).timestamp()

        for file in temp_dir.rglob("*"):
            if file.is_file():
                self.mock_stat(file, creation_time, modification_time)

        result = get_files(
            temp_dir,
            extensions=None,
            subfolders=True,
            time_type="modified",
            as_date_time=False,
            str_format="%Y-%m-%d %H:%M:%S",
            get_size=True,
        )

        expected = [
            {"path": temp_dir / "file1.txt", "datetime": "2022-01-01 00:00:00",
                "size": (temp_dir / "file1.txt").stat().st_size},
            {"path": temp_dir / "file2.txt", "datetime": "2022-01-01 00:00:00",
                "size": (temp_dir / "file2.txt").stat().st_size},
            {"path": temp_dir / "sub_dir" / "file3.txt", "datetime": "2022-01-01 00:00:00",
                "size": (temp_dir / "sub_dir" / "file3.txt").stat().st_size},
            {"path": temp_dir / "sub_dir" / "file4.log", "datetime": "2022-01-01 00:00:00",
                "size": (temp_dir / "sub_dir" / "file4.log").stat().st_size},
            {"path": temp_dir / "sub_dir" / "file5.csv", "datetime": "2022-01-01 00:00:00",
                "size": (temp_dir / "sub_dir" / "file5.csv").stat().st_size},
            {"path": temp_dir / "another_sub_dir" / "file6.txt", "datetime": "2022-01-01 00:00:00",
                "size": (temp_dir / "another_sub_dir" / "file6.txt").stat().st_size},
            {"path": temp_dir / "another_sub_dir" / "file7.json", "datetime": "2022-01-01 00:00:00",
                "size": (temp_dir / "another_sub_dir" / "file7.json").stat().st_size},
            {"path": temp_dir / "another_sub_dir" / "file8.xml", "datetime": "2022-01-01 00:00:00",
                "size": (temp_dir / "another_sub_dir" / "file8.xml").stat().st_size},
            {"path": temp_dir / "file9.md", "datetime": "2022-01-01 00:00:00",
                "size": (temp_dir / "file9.md").stat().st_size},
            {"path": temp_dir / "file10.py", "datetime": "2022-01-01 00:00:00",
                "size": (temp_dir / "file10.py").stat().st_size},
            {"path": temp_dir / "file11.html", "datetime": "2022-01-01 00:00:00",
                "size": (temp_dir / "file11.html").stat().st_size},
            {"path": temp_dir / "another_sub_dir" / "nested_sub_dir" / "file12.txt", "datetime": "2022-01-01 00:00:00",
                "size": (temp_dir / "another_sub_dir" / "nested_sub_dir" / "file12.txt").stat().st_size},
            {"path": temp_dir / "another_sub_dir" / "nested_sub_dir" / "file13.js", "datetime": "2022-01-01 00:00:00",
                "size": (temp_dir / "another_sub_dir" / "nested_sub_dir" / "file13.js").stat().st_size},
            {"path": temp_dir / "another_sub_dir" / "nested_sub_dir" / "file14.css", "datetime": "2022-01-01 00:00:00",
                "size": (temp_dir / "another_sub_dir" / "nested_sub_dir" / "file14.css").stat().st_size},
        ]

        result = sorted(result, key=lambda x: x["path"].name)
        expected = sorted(expected, key=lambda x: x["path"].name)
        self.assertEqual(len(result), len(expected))
        for res, exp in zip(result, expected):
            self.assertEqual(res["path"].name, exp["path"].name)
            self.assertEqual(res["datetime"], exp["datetime"])
            self.assertEqual(res["size"], exp["size"])

    def test_get_files_single_extension_string(self):
        temp_dir = self.create_temp_directory_structure()
        creation_time = datetime(2021, 1, 1).timestamp()
        modification_time = datetime(2022, 1, 1).timestamp()

        # Mock the stat results for all files
        for file in temp_dir.rglob("*"):
            if file.is_file():
                self.mock_stat(file, creation_time, modification_time)

        result = get_files(temp_dir, extensions=".txt")

        expected = [
            {"path": temp_dir / "file1.txt", "datetime": "2022-01-01 00:00:00"},
            {"path": temp_dir / "file2.txt", "datetime": "2022-01-01 00:00:00"},
            {"path": temp_dir / "sub_dir" / "file3.txt",
             "datetime": "2022-01-01 00:00:00"},
            {"path": temp_dir / "another_sub_dir" / "file6.txt",
             "datetime": "2022-01-01 00:00:00"},
            {"path": temp_dir / "another_sub_dir" / "nested_sub_dir" /
                "file12.txt",
             "datetime": "2022-01-01 00:00:00"},
        ]

        result = sorted(result, key=lambda x: x["path"].name)
        expected = sorted(expected, key=lambda x: x["path"].name)
        self.assertEqual(len(result), len(expected))
        for res, exp in zip(result, expected):
            self.assertEqual(res, exp)

    def test_get_files_multiple_extensions_string(self):
        temp_dir = self.create_temp_directory_structure()
        creation_time = datetime(2021, 1, 1).timestamp()
        modification_time = datetime(2022, 1, 1).timestamp()

        # Mock the stat results for all files
        for file in temp_dir.rglob("*"):
            if file.is_file():
                self.mock_stat(file, creation_time, modification_time)

        result = get_files(temp_dir, extensions=".txt, .log")

        expected = [
            {"path": temp_dir / "file1.txt", "datetime": "2022-01-01 00:00:00"},
            {"path": temp_dir / "file2.txt", "datetime": "2022-01-01 00:00:00"},
            {"path": temp_dir / "sub_dir" / "file3.txt",
             "datetime": "2022-01-01 00:00:00"},
            {"path": temp_dir / "sub_dir" / "file4.log",
             "datetime": "2022-01-01 00:00:00"},
            {"path": temp_dir / "another_sub_dir" / "file6.txt",
             "datetime": "2022-01-01 00:00:00"},
            {"path": temp_dir / "another_sub_dir" / "nested_sub_dir" /
                "file12.txt",
             "datetime": "2022-01-01 00:00:00"},
        ]

        result = sorted(result, key=lambda x: x["path"].name)
        expected = sorted(expected, key=lambda x: x["path"].name)
        self.assertEqual(len(result), len(expected))
        for res, exp in zip(result, expected):
            self.assertEqual(res, exp)

    def test_get_files_txt_files(self):
        temp_dir = self.temp_directory_structure
        creation_time = datetime(2021, 1, 1).timestamp()
        modification_time = datetime(2022, 1, 1).timestamp()

        # Mock the stat results for all files
        for file in temp_dir.rglob("*"):
            if file.is_file():
                self.mock_stat(file, creation_time, modification_time)

        result = get_files(
            temp_dir,
            extensions=[".txt"],
            subfolders=True,
            time_type="modified",
            as_date_time=False,
            str_format="%Y-%m-%d %H:%M:%S",
            get_size=True,
        )

        expected = [
            {"path": temp_dir / "file1.txt",
             "datetime": "2022-01-01 00:00:00",
             "size": (temp_dir / "file1.txt").stat().st_size},
            {"path": temp_dir / "file2.txt",
             "datetime": "2022-01-01 00:00:00",
             "size": (temp_dir / "file2.txt").stat().st_size},
            {"path": temp_dir / "sub_dir" / "file3.txt",
             "datetime": "2022-01-01 00:00:00",
             "size": (temp_dir / "sub_dir" / "file3.txt").stat().st_size},
            {"path": temp_dir / "another_sub_dir" / "file6.txt",
             "datetime": "2022-01-01 00:00:00",
             "size": (temp_dir / "another_sub_dir" / "file6.txt").stat().st_size
             },
            {"path": temp_dir / "another_sub_dir" / "nested_sub_dir" /
             "file12.txt",
             "datetime": "2022-01-01 00:00:00",
             "size": (temp_dir / "another_sub_dir" / "nested_sub_dir" /
                      "file12.txt").stat().st_size},
        ]

        result = sorted(result, key=lambda x: x["path"].name)
        expected = sorted(expected, key=lambda x: x["path"].name)

        # Debug prints
        print("Result:", result)
        print("Expected:", expected)

        self.assertEqual(len(result), len(expected))
        for res, exp in zip(result, expected):
            self.assertEqual(res["path"].name, exp["path"].name)
            self.assertEqual(res["datetime"], exp["datetime"])
            self.assertEqual(res["size"], exp["size"])

    def test_get_files_csv_files(self):
        temp_dir = self.temp_directory_structure
        creation_time = datetime(2021, 1, 1).timestamp()
        modification_time = datetime(2022, 1, 1).timestamp()

        # Mock the stat results for all files
        for file in temp_dir.rglob("*"):
            if file.is_file():
                self.mock_stat(file, creation_time, modification_time)

        result = get_files(
            temp_dir,
            extensions=[".csv"],
            subfolders=True,
            time_type="modified",
            as_date_time=False,
            str_format="%Y-%m-%d %H:%M:%S",
            get_size=True,
        )

        expected = [
            {"path": temp_dir / "sub_dir" / "file5.csv",
             "datetime": "2022-01-01 00:00:00",
             "size": (temp_dir / "sub_dir" / "file5.csv").stat().st_size},
        ]

        result = sorted(result, key=lambda x: x["path"].name)
        expected = sorted(expected, key=lambda x: x["path"].name)
        self.assertEqual(len(result), len(expected))
        for res, exp in zip(result, expected):
            self.assertEqual(res["path"].name, exp["path"].name)
            self.assertEqual(res["datetime"], exp["datetime"])
            self.assertEqual(res["size"], exp["size"])

    def test_get_files_log_files(self):
        temp_dir = self.temp_directory_structure
        creation_time = datetime(2021, 1, 1).timestamp()
        modification_time = datetime(2022, 1, 1).timestamp()

        for file in temp_dir.rglob("*"):
            if file.is_file():
                self.mock_stat(file, creation_time, modification_time)

        result = get_files(
            temp_dir,
            extensions=[".log"],
            subfolders=True,
            time_type="modified",
            as_date_time=False,
            str_format="%Y-%m-%d %H:%M:%S",
            get_size=True,
        )

        expected = [
            {"path": temp_dir / "sub_dir" / "file4.log",
             "datetime": "2022-01-01 00:00:00",
             "size": (temp_dir / "sub_dir" / "file4.log").stat().st_size},
        ]

        result = sorted(result, key=lambda x: x["path"].name)
        expected = sorted(expected, key=lambda x: x["path"].name)
        self.assertEqual(len(result), len(expected))
        for res, exp in zip(result, expected):
            self.assertEqual(res["path"].name, exp["path"].name)
            self.assertEqual(res["datetime"], exp["datetime"])
            self.assertEqual(res["size"], exp["size"])

    def test_get_files_iterator_file_not_found_error(self):
        with self.assertRaises(FileNotFoundError):
            list(get_files_iterator(
                "/mocked/path",
                extensions=[".txt"],
                subfolders=True,
                time_type="modified",
                as_date_time=False,
                str_format="%Y-%m-%d %H:%M:%S",
                get_size=True
            ))

    def test_get_folder_and_file_count(self):
        folder_count, file_count = get_folder_and_file_count(
            str(self.temp_directory_structure))
        self.assertEqual(folder_count, 3)
        self.assertEqual(file_count, 14)

    def test_process_file(self):
        temp_file = self.temp_directory_structure / "file1.txt"
        creation_time = datetime(2021, 1, 1).timestamp()
        modification_time = datetime(2022, 1, 1).timestamp()

        with mock.patch.object(Path, "stat") as mock_stat:
            real_stat = temp_file.stat()
            mock_stat.return_value.st_ctime = creation_time
            mock_stat.return_value.st_mtime = modification_time
            mock_stat.return_value.st_size = real_stat.st_size

            result = process_file(
                temp_file, "created", True, "%Y-%m-%d", False
            )
            self.assertEqual(result["path"].name, temp_file.name)
            self.assertEqual(result["datetime"], datetime(2021, 1, 1))

    def test_get_folder_size(self):
        base_path = self.temp_directory_structure
        folder_size = get_folder_size(str(base_path))
        expected_size = sum([
            (base_path / "file1.txt").stat().st_size,
            (base_path / "file2.txt").stat().st_size,
            (base_path / "sub_dir" / "file3.txt").stat().st_size,
            (base_path / "sub_dir" / "file4.log").stat().st_size,
            (base_path / "sub_dir" / "file5.csv").stat().st_size,
            (base_path / "another_sub_dir" / "file6.txt").stat().st_size,
            (base_path / "another_sub_dir" / "file7.json").stat().st_size,
            (base_path / "another_sub_dir" / "file8.xml").stat().st_size,
            (base_path / "file9.md").stat().st_size,
            (base_path / "file10.py").stat().st_size,
            (base_path / "file11.html").stat().st_size,
            (base_path / "another_sub_dir" /
             "nested_sub_dir" / "file12.txt").stat().st_size,
            (base_path / "another_sub_dir" /
             "nested_sub_dir" / "file13.js").stat().st_size,
            (base_path / "another_sub_dir" /
             "nested_sub_dir" / "file14.css").stat().st_size
        ])
        self.assertEqual(folder_size, expected_size)

    def test_get_folders(self):
        folders = get_folders(self.temp_directory_structure)
        expected_folders = [
            self.temp_directory_structure / "sub_dir",
            self.temp_directory_structure / "another_sub_dir",
            self.temp_directory_structure / "another_sub_dir" / "nested_sub_dir"
        ]
        self.assertCountEqual(folders, expected_folders)

    def test_get_folders_file_path(self) -> None:
        with self.assertRaises(NotADirectoryError):
            get_folders(self.temp_directory_structure / "file1.txt")
