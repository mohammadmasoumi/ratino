import string
import random


def gen_random_str(size=10):
    """
    Generates a random string of specified size.

    Parameters:
        size (int): The length of the random string to be generated. Default is 10.

    Returns:
        str: A random string of the specified size.
    """
    return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=size))
