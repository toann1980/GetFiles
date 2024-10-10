# GetFiles

## Description

GetFiles simplifies retrieving files from a directory. GetFiles will return all
files as a python dictionary or a list of pathlib.Path objects, depending on the
arguments that are used.


## Installation

To install GetFiles, you need to have Python 3.10 or higher installed on your
system. You can then install the project using pip:

```sh
pip install git+https://github.com/toann1980/GetFiles.git
```

## Usage
After installation, you can import the `get_files` function from the `getfiles` package:

```python
from getfiles import get_files
```


```python
# Get all .txt and .csv files from a directory with size information
files = get_files('/path/to/directory', extensions=['txt', 'csv'], get_size=True)

# Output:
[
    {
        'path': '/path/to/directory/file1.txt',
        'datetime': '2022-01-01 12:00:00',
        'size': 1024
    },
    {
        'path': '/path/to/directory/file2.csv',
        'datetime': '2022-01-02 12:00:00',
        'size': 2048
    },
    {
        'path': '/path/to/directory/subdirectory/file3.txt',
        'datetime': '2022-01-03 12:00:00',
        'size': 3072
    }
]
```

Get all .txt and .csv files from a directory with datetime as datetime objects and size information

```python
files = get_files('/path/to/directory', extensions=['txt', 'csv'], as_date_time=True, get_size=True)

# Output:
[
    {
        'path': '/path/to/directory/file1.txt',
        'datetime': datetime.datetime(2022, 1, 1, 12, 0, 0),
        'size': 1024
    },
    ...
]
```


Get all .txt and .csv files from a directory without time information
```python
from getfiles import get_files

files = get_files('/path/to/directory', extensions=['txt', 'csv'], as_date_time=None)

# Output:
[
    '/path/to/directory/file1.txt',
    '/path/to/directory/file2.csv',
    '/path/to/directory/subdirectory/file3.txt'
]


```

These are the `get_files` arguments:

```python
def get_files(
    path: str | Path,
    time_type: Literal["created", "modified"] = "modified",
    extensions: str | list[str] = None,
    as_date_time: bool = False,
    get_size: bool = False,
    str_format: str = "%Y-%m-%d %H:%M:%S",
    subfolders: bool = True
) -> list[dict] | list[str]:
```

| Argument | Type | Default | Description |
| --- | --- | --- | --- |
| `path` | `str` or `Path` | - | The path to the directory to get files from. |
| `extensions` | `str` or `list[str]` | `None` | The file extensions to filter by. If `None`, all file extensions are included. |
| `subfolders` | `bool` | `True` | Whether to also include files from subfolders of the specified directory. |
| `time_type` | `"created"`, `"modified"`, or `None` | `"modified"` | The type of time to retrieve for each file. If None, then no time will be returned. |
| `as_date_time` | `bool` | `False` | Whether to return the file times as `datetime` objects. If `False`, they are returned as strings. |
| `str_format` | `str` | `"%Y-%m-%d %H:%M:%S"` | The format to use when returning file times as strings. |
| `get_size` | `bool` | `False` | Whether to also return the size of each file. |



# License
GetFiles is licensed under the MIT License. See the LICENSE file for more details.

