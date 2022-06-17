import random
import math


def generate_otp():
    # storing strings in a list
    digits = [i for i in range(0, 10)]

    # initializing a string
    random_str = ""

    # we can generate any length of string we want
    for i in range(4):
        index = math.floor(random.random() * 10)
        random_str += str(digits[index])
    return random_str


