import time
import concurrent.futures
from multiprocessing import Pool, cpu_count


def factorize(numbers: list) -> list:
    """
    Factorize a list of numbers and return a list of lists containing their factors.

    Args:
        numbers (list): List of integers to be factorized.

    Returns:
        list: A list of lists where each inner list contains the factors of the corresponding number in the input list.
    """
    result_list = []
    for el in numbers:
        tmp_list = []
        for num in range(1, el + 1):
            if el % num == 0:
                tmp_list.append(num)
        result_list.append(tmp_list)
    return result_list


def factorize_multi(number: int) -> list:
    """
    Factorize a single number and return a list of its factors.

    Args:
        number (int): The integer to be factorized.

    Returns:
        list: A list of integers representing the factors of the input number.
    """
    result_list = []
    for num in range(1, number + 1):
        if number % num == 0:
            result_list.append(num)
    return result_list


if __name__ == '__main__':

    lst = [128, 255, 99999, 10651060]

    start_time = time.time()
    a, b, c, d, *_ = factorize(lst)
    end_time = time.time()

    assert a == [1, 2, 4, 8, 16, 32, 64, 128]
    assert b == [1, 3, 5, 15, 17, 51, 85, 255]
    assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 304316, 380395, 532553, 760790, 1065106,
                 1521580, 2130212, 2662765, 5325530, 10651060]

    print(f"Sync time: {end_time - start_time}")
    print("Done sync...\n")

    cores_count = cpu_count() - 1
    if cores_count == 0:
        cores_count = 1

    # multiprocessing
    start_time_multi = time.time()
    with Pool(processes=cores_count) as pool:
        pool.map(factorize_multi, lst)
    end_time_multi = time.time()

    print(f"Multi 1 time (Pool): {end_time_multi - start_time_multi}")
    print("Done multi 1 (Pool)...\n")

    # concurrent
    start_time_multi2 = time.time()
    with concurrent.futures.ProcessPoolExecutor(cores_count) as executor:
        executor.map(factorize_multi, lst)
    end_time_multi2 = time.time()

    print(f"Multi 2 time (concurrent): {end_time_multi2 - start_time_multi2}")
    print("Done multi 2 (concurrent)...")
