"""Global variables for scheduler scraper

Written by Kei Imada

Last modified on 20180815

Attributes:
    TRICO_URL (string): url for trico.haverford.edu homepage
    TRICO_PREFIX (string): url stub for getting course descriptions

"""


TRICO_URL = ("https://trico.haverford.edu/"
             "cgi-bin/courseguide/cgi-bin/search.cgi")

TRICO_PREFIX = ("https://trico.haverford.edu/"
                "cgi-bin/courseguide/cgi-bin/")


def main():
    print('this file contains global variables for the scheduler scraper')


if __name__ == '__main__':
    main()
