from collections.abc import Generator
from datetime import datetime as dt
import os
from pathlib import Path
from typing import List, Literal, Union


def get_files(
    path: Path | str,
    extensions: str | list[str] = None,
    subfolders: bool = True,
    time_type: Literal["created", "modified", None] = "modified",
    as_date_time: bool = False,
    str_format: str = "%Y-%m-%d %H:%M:%S",
    get_size: bool = False
) -> list[dict] | list[str]:
    """
    Returns a list of files in the given path with optional additional
    information.

    Args:
        path (str | Path): The path to search for files.
        extensions (str | list[str], optional): The file extensions to include.
            If a string is provided, it can be a single extension or multiple
            extensions separated by commas. Defaults to None, which includes
            all files.
        subfolders (bool, optional): Whether to include files in subfolders.
            Defaults to True.
        time_type (Literal["created", "modified", None], optional): The type of
            time to return. If None, will not return the time.
        as_date_time (bool, optional): Whether to return the time as a datetime
            object. If False, the time is returned as a string formatted
            according to `str_format`. Defaults to False.
        str_format (str, optional): The format to use for the date time string
            if `as_date_time` is False. Defaults to "%Y-%m-%d %H:%M:%S".
        get_size (bool, optional): Whether to return the size of the files.
            Defaults to False.

    Returns:
        list[dict | str]: A list of files in the given path. If `as_date_time`
            or `size` is True, each file is represented as a dictionary
            with the file path and the requested additional information.
            Otherwise, each file is represented as a string with the file path.
    """
    if isinstance(path, str):
        path = Path(path)

    if not os.access(path, os.R_OK):
        raise PermissionError(f"No read permission for directory {path}.")

    if isinstance(extensions, str):
        extensions = (extensions,) if "," not in extensions else \
            tuple([ext.strip() for ext in extensions.split(",")])

    return list(
        get_files_iterator(
            path, extensions, subfolders, time_type, as_date_time, str_format,
            get_size
        )
    )


def get_files_iterator(
    path: Path | str,
    extensions: str | list[str],
    subfolders: bool,
    time_type: Literal["created", "modified", None],
    as_date_time: bool,
    str_format: str,
    get_size: bool
) -> Generator[Path | dict]:
    """
    Returns a generator that yields files in the given path.

    Args:
        path (str | Path): The path to search for files.
        extensions (str | list[str], optional): The file extensions to include.
        subfolders (bool, optional): Whether to include subfolders.
        time_type (Literal["created", "modified", None], optional): The type of
            time to return. If None, will not return the time.
        as_date_time (bool, optional): Whether to return the time as a datetime
            object.
        str_format (str, optional): The format to use for the date time string.
        get_size (bool, optional): Whether to return the size of the files.

    Yields:
        Generator[str | dict[str]]: A generator that yields files in the given
            Path or dict[str] given, the choices. If only the path is chosen, a
            Path will be returned.
    """
    try:
        with os.scandir(path) as iterator:
            for file in iterator:
                if file.is_dir(follow_symlinks=False) and subfolders:
                    yield from get_files_iterator(
                        Path(file), extensions, subfolders, time_type,
                        as_date_time, str_format, get_size
                    )
                elif extensions is None or \
                        file.name.lower().endswith(tuple(extensions)):
                    yield process_file(
                        Path(file), time_type, as_date_time, str_format,
                        get_size

                    )
    except FileNotFoundError:
        raise FileNotFoundError(f"Directory {path} does not exist.")


def get_folder_and_file_count(path: str) -> tuple[int, int]:
    """
    Returns the number of folders and files in the given path.

    Args:
        path (str): The path to count the folders and files in.

    Returns:
        tuple[int, int]: A tuple where the first element is the number of
            folders and the second element is the number of files.
    """
    num_folders = 0
    num_files = 0

    def scan_directory(path: str):
        nonlocal num_folders, num_files
        with os.scandir(path) as iterator:
            for entry in iterator:
                if entry.is_dir(follow_symlinks=False):
                    num_folders += 1
                    scan_directory(entry.path)
                elif entry.is_file(follow_symlinks=False):
                    num_files += 1

    scan_directory(path)

    return num_folders, num_files


def get_folder_size(path: str) -> int:
    """
    Returns the size of a folder in bytes.

    Args:
        path (str): The path to the folder.

    Returns:
        int: The size of the folder in bytes.
    """
    total_size = 0

    def scan_directory(path: str):
        nonlocal total_size
        with os.scandir(path) as iterator:
            for entry in iterator:
                if entry.is_dir(follow_symlinks=False):
                    scan_directory(entry.path)
                elif entry.is_file(follow_symlinks=False):
                    total_size += entry.stat(follow_symlinks=False).st_size

    scan_directory(path)

    return total_size


def get_folders(path: Union[str, Path]) -> List[Path]:
    """
    Returns a list of folders in the given path.

    Args:
        path (str): The path to search for folders.

    Returns:
        list[str]: A list of folders in the given path.
    """
    path = Path(path)
    if not path.is_dir():
        raise NotADirectoryError(f"{path} is not a directory.")

    folders = []

    def scan_directory(path: Path) -> None:
        nonlocal folders
        with os.scandir(path) as iterator:
            for entry in iterator:
                if entry.is_dir(follow_symlinks=False):
                    folders.append(Path(entry.path))
                    scan_directory(entry.path)

    scan_directory(path)

    return folders


def process_file(
    path: Path,
    time_type: Literal["created", "modified", None],
    as_date_time: bool,
    str_format: str,
    get_size: bool
) -> Path | dict:
    """Processes a file and returns its information.

    Args:
        path (Path): The file to process.
        time_type (Literal["created", "modified", None], optional): The type of
            time to return. If None, will not return the time.
        as_date_time (bool): If True, returns the time as a datetime object.
            If False, returns the time as a string formatted according to
            `str_format`.
        str_format (str, optional): The format to use for the date time string
            if `as_date_time` is False.
        get_size (bool): If True, includes the size of the file in the returned
            information.

    Returns:
        Path | dict: A dictionary containing the information of the file. The
            dictionary includes the path of the file, the specified time (either
            'modified' or 'created'), and optionally the size of the file. If no
            additional information is requested (`as_date_time` and `get_size`
            are both False), the function returns the path.
    """
    info = {"path": path}

    if time_type is not None:
        if time_type == "modified":
            file_time = dt.fromtimestamp(
                path.stat(follow_symlinks=False).st_mtime
            )
        else:
            file_time = dt.fromtimestamp(
                path.stat(follow_symlinks=False).st_ctime
            )
        if as_date_time:
            info["datetime"] = file_time
        else:
            info["datetime"] = file_time.strftime(str_format)

    if get_size:
        info["size"] = path.stat(follow_symlinks=False).st_size

    return info if len(info.keys()) > 1 else path
