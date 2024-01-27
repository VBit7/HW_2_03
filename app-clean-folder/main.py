import re
import sys
import shutil
from . import scandir
from pathlib import Path

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

TRANS = {}

for c, t in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = t
    TRANS[ord(c.upper())] = t.upper()


def normalize(file_path: Path, destination_dir: Path) -> Path:
    """
    Normalize a file name for safe use in a destination directory.

    Args:
        - file_path (Path): The original file path.
        - destination_dir (Path): The destination directory.

    Returns:
        - Path: A normalized Path object for the file's new location in the destination directory.

    This function normalizes the file name by transliterating Cyrillic characters to their Latin equivalents,
    replacing non-word characters with underscores, and ensuring it is unique in the destination directory.
    It returns a Path object representing the normalized file path in the destination directory.
    """    
    base_name, extension = file_path.name.rsplit('.', 1)
    normal_name = re.sub(r'\W', '_', base_name.translate(TRANS))
    normalize_name = f'{normal_name}.{extension}'
    counter = 1

    while (destination_dir / normalize_name).exists():
        new_name = f"{normal_name}_{counter}.{extension}"
        normalize_name = file_path.with_name(new_name)
        counter += 1

    return destination_dir / normalize_name


def move_files(base_dir: str, file_dict: dict) -> int:
    """
    Move files from the provided dictionary to their corresponding directories.

    Args:
        - base_dir (str): The base directory where files will be moved.
        - file_dict (dict): A dictionary with directory names as keys and lists of files as values.

    Returns:
        - int: Returns -1 if the operation is successful. Returns an error code if any issues occur.

    This function takes a base directory and a dictionary that maps directory names to lists of files.
    It moves each file to its corresponding directory within the base directory. If the destination
    directory does not exist, it is created. The function handles possible errors such as file not
    found, file already exists in the destination directory, or insufficient permissions to write to
    the destination directory. It returns -1 if the operation is successful, or an error code indicating
    the type of error encountered.
    """    
    base_dir = Path(base_dir).resolve()

    for directory, files in file_dict.items():
        destination_dir = base_dir / Path(directory)

        try:
            if not destination_dir.is_dir():
                destination_dir.mkdir(exist_ok=True, parents=True)

            for file in files:
                destination_path = destination_dir / file.name
                destination_path = normalize(destination_path, destination_dir)
                shutil.move(str(file), str(destination_path))
        except FileNotFoundError as e:
            print(f"Error: {e} - File not found.")
            return 1
        except FileExistsError as e:
            print(f"Error: {e} - A file with the same name already exists in the destination directory.")
            return 2
        except PermissionError as e:
            print(f"Error: {e} - Insufficient permissions to write to the destination directory.")
            return 3

    return -1


def remove_dir(dir_list: list) -> int:
    """
    Remove directories from the provided list.

    Args:
        - dir_list (list): A list of directories to be removed.

    Returns:
        - int: Returns -1 if the operation is successful. Returns an error code if any issues occur.

    This function takes a list of directories and removes them. The directories are sorted in descending order
    of their string length, ensuring that nested directories are removed before their parent directories.
    The function handles possible errors such as directory not found or any other OSError while trying to
    delete the directory. It returns -1 if the operation is successful, or an error code indicating the type
    of error encountered.
    """
    sorted_dir_list = sorted(dir_list, key=lambda x: len(str(x)), reverse=True)
    
    for dir in sorted_dir_list:
        try:
            shutil.rmtree(dir)
        except FileNotFoundError:
            print(f"Error: Directory {dir} not found.")
            return 1
        except OSError as e:
            print(f"Error: {e} - Failed to delete the directory {dir}.")
            return 2

    return -1


def unpack_dir(dir_path):
    """
    Unpack archives in the specified directory.

    Args:
        - dir_path (Path): The path to the directory containing archives to be unpacked.

    Returns:
        - int: Returns -1 if the operation is successful. Returns an error code if any issues occur.

    This function iterates through the files in the specified directory. If a file is an archive with a supported
    extension, it unpacks the archive into a subdirectory with the same name as the base name of the file.
    The function handles possible errors, such as a failed archive extraction, insufficient permissions, or a missing file.
    It returns -1 if the operation is successful or an error code indicating the type of error encountered.
    """    
    try:
        for item in dir_path.iterdir():
            
            if item.is_file():
                base_name, extension = item.name.rsplit('.', 1)

                if extension in scandir.FILE_CATEGORIES['archives']:
                    destination_dir = dir_path / base_name
                    
                    if not destination_dir.is_dir():
                        destination_dir.mkdir(exist_ok=True, parents=True)

                        try:
                            shutil.unpack_archive(str(item.absolute()), str(destination_dir.absolute()))
                            # os.remove(str(item.absolute()))   # to delete the file, if necessary
                        except (shutil.ReadError, PermissionError, FileNotFoundError) as e:
                            print(f"Error: {e} - Failed to unpack the archive {item}.")
                            return 3
                    
    except FileNotFoundError as e:
        print(f"Error: {e} - File not found.")
        return 1
    except PermissionError as e:
        print(f"Error: {e} - Permission denied to create a directory.")
        return 2

    return -1


def main():
    if len(sys.argv) != 2:
        print('Please provide a folder path as a command-line argument.')
    else:
        directory_path = sys.argv[1]
        print(f"The entered folder path is: {directory_path}")

        categorized_files, subdir_list = scandir.file_lister(directory_path)

        if move_files(directory_path, categorized_files) == -1:
            remove_dir(subdir_list)
            unpack_dir(Path(directory_path) / 'archives')
            print('Done...')


if __name__ == '__main__':
    main()
