import argparse

from taro.utils import print_hi

def main():
    parser = argparse.ArgumentParser(
                    prog='Taro',
                    description='Taro is a program',
                    epilog='Text at the bottom of help')
    parser.add_argument('-s', '--say_hi', action='store_true')
    args = parser.parse_args()
    if args.say_hi:
        print_hi()
    else:
        print("I will say hi if you add -s")