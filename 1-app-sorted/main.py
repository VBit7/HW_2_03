import sys
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor


def process_files(directory, file_list):
    destination_base_dir = Path(directory) / 'processed_files'

    try:
        if not destination_base_dir.is_dir():
            destination_base_dir.mkdir(exist_ok=True, parents=True)

        for file in file_list:
            file_extension = file.suffix[1:].lower()
            category_dir = destination_base_dir / file_extension

            if not category_dir.is_dir():
                category_dir.mkdir(exist_ok=True, parents=True)

            destination_path = category_dir / file.name
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


def main():
    if len(sys.argv) != 2:
        print('Please provide a folder path as a command-line argument.')
        print('Example usage: python main.py C:\\path\\to\\directory')
    else:
        directory_path = sys.argv[1]
        print(f"The entered folder path is: {directory_path}")

        file_list = list(Path(directory_path).rglob('*'))
        file_list = [file for file in file_list if file.is_file()]

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_files, directory_path, [file]) for file in file_list]

            results = [future.result() for future in futures]

            if any(result != -1 for result in results):
                print("Error processing files.")
                return

            print('Done...')


if __name__ == '__main__':
    main()
