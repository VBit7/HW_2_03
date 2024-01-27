from pathlib import Path
from collections import OrderedDict

# The 'FILE_CATEGORIES' dictionary is used for categorizing files based on their extensions.
# It defines a set of categories where each category corresponds to specific file extensions.
# Files will be categorized into these predefined categories, and any files with extensions
# not listed here will be categorized under the 'other' category.
FILE_CATEGORIES = OrderedDict([
    ('images', ['jpeg', 'png', 'jpg', 'svg']),
    ('documents', ['doc', 'docx', 'txt', 'pdf', 'xlsx', 'pptx']),
    ('audio', ['mp3', 'ogg', 'wav', 'amr']),
    ('video', ['avi', 'mp4', 'mov', 'mkv']),
    ('archives', ['zip', 'gz', 'tar']),
    ('other', []) # The 'other' category for unspecified or unrecognized file extensions.
    # Note: 'other' should be the last entry in the dictionary, and its list should remain empty.
])


def scan_directory(directory_path: str) -> list:
    """
    Scans the contents of a directory and returns a list of files and subdirectories.

    Args:
        - directory_path (str): The path to the directory to be scanned.

    Returns:
        - tuple: A tuple containing two lists. The first list contains Path objects representing the files in the directory,
          and the second list contains Path objects representing the subdirectories.

    This function scans the contents of the specified directory and returns a tuple of two lists. The first list contains
    Path objects representing the files in the directory, and the second list contains Path objects representing the
    subdirectories. It recursively explores subdirectories within the given directory.
    """
    file_list = []
    subdir_list = []

    for item in Path(directory_path).iterdir():
        if item.is_file():
            file_list.append(item)
        elif item.name not in FILE_CATEGORIES:
            subdir_list.append(item)
            files, dirs = scan_directory(item)
            file_list.extend(files)
            subdir_list.extend(dirs)

    return file_list, subdir_list


def file_lister(directory_path: str) -> dict:
    """
    Lists and categorizes files and subdirectories in the specified directory.

    Args:
        - directory_path (str): The path to the directory to be scanned and categorized.

    Returns:
        - tuple: A tuple containing two dictionaries. The first dictionary categorizes files
          into predefined categories, and the second dictionary categorizes subdirectories.
          Keys represent categories, and values are lists of Path objects.

    This function scans the specified directory using the 'scan_directory' function
    and categorizes files into predefined categories based on their extensions.
    It also categorizes subdirectories in a separate dictionary.
    It returns a tuple of two dictionaries where each key represents a category, and the corresponding
    value is a list of Path objects representing files or subdirectories in that category.

    The 'FILE_CATEGORIES' dictionary is used for file categorization,
    and any files with extensions not listed in 'FILE_CATEGORIES' will be categorized under the 'other' category.
    """
    file_list, subdir_list = scan_directory(directory_path)
    categorized_files = {category: [] for category in FILE_CATEGORIES}
    last_category, extensions = FILE_CATEGORIES.popitem(last=True)

    for item in file_list:
        file_extension = Path(item).suffix[1:].lower()
        category_found = False

        for category, extensions in FILE_CATEGORIES.items():
            if file_extension in extensions:
                categorized_files[category].append(item)
                category_found = True
                break

        if not category_found:
            categorized_files[last_category].append(item)

    return categorized_files, subdir_list


if __name__ == '__main__':
    
    directory_path = 'c:\\Temp'
    
    categorized_files, subdir_list = file_lister(directory_path)

    for category, files in categorized_files.items():
        print(f'{category}: {files}')

    for subdir in subdir_list:
        print(f'subdir:  {subdir}')
