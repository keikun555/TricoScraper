"""Scraper for trico.haverford.edu

Written by Kei Imada

Last updated on 20180815

Todo:
    * ssl connections for the scraping?

"""


import bs4
import certifi
import requests
import itertools
import urllib3 as urllib
import multiprocessing as multi

from tricoinfo import TricoInfo
from tricoglobals import TRICO_URL, TRICO_PREFIX


def _TricoScraper_get_links(params):
    """Gets list of links given the parameters for the GET request.

    Args:
        params (list of tuples of strings): the parameters for the GET request
                                            header.

    Returns:
        list of strings: links.

    """
    req = requests.get(TRICO_URL, params=params)
    soup = bs4.BeautifulSoup(req.text, 'html.parser')
    table = soup.find('table',
                      {'width': '100%', 'border': '2'})
    a_elements = table.findChildren('a')
    links = [TRICO_PREFIX+a['href'] for a in a_elements]
    return links


def _TricoScraper_get_course(url):
    """Given url, return dictionary containing course descriptions.

    Args:
        url (string): the url to the course page.

    Returns:
        dictionary: the course description.

    """
    req = requests.get(url)
    soup = bs4.BeautifulSoup(req.text, 'html.parser')
    course = {}
    rows = soup.findChild('table').findChildren('tr')
    for row in rows:
        for br in row.find_all('br'):
            br.replace_with("\n")
        [key, value] = [t.text for t in row.findChildren('td')]
        course[key.strip()] = value.strip()
    return course


class TricoScraper(object):
    """The scraper for trico.haverford.edu."""

    def __init__(self, num_threads=multi.cpu_count(), ssl=True):
        """Creates a TricoScraper Object.

        Args:
            num_threads (int): The number of worker threads. Defaults to number
                               of cores.
            ssl (bool): Whether or not to use secure connection. Defaults to
                        True (use ssl).

        """
        self._pool = multi.Pool(num_threads)
        if ssl:
            self._http = urllib.PoolManager(cert_reqs='CERT_REQUIRED',
                                            ca_certs=certifi.where())
        else:
            self._http = urllib.PoolManager()

    def _get_num_links(self, params):
        """Gets number of classes the search parameter hit.

        Args:
            params (list of tuples of strings): The search parameters.

        Returns:
            int: the number of classes the search parameter hit.

        """
        req = requests.get(TRICO_URL, params=params)
        soup = bs4.BeautifulSoup(req.text, 'html.parser')
        return int(soup.find('font').findChild('b').string.split(' ')[-1])

    def search(self,
               campus=None,
               crsnum=".",
               dept=None,
               instr=".",
               meetday=".",
               meettime=None,
               smstr=None,
               srch_frz="."):
        """Searches the trico.haverford.edu website for courses.

        Args:
            campus (list of strings): Campuses the courses are in. Defaults to
                                      None (all campuses).
            crsnum (string): Course number for a course. Defaults to "." (any
                             course number).
            dept (list of strings): Departments the courses are in. Defaults to
                                    None (all departments).
            instr (string): The instructor for the course. Defaults to "." (any
                            instructor).
            meetday (string): The days the courses are met. Defaults to "."
                              (any day).
            meettime (string): The times the courses are met. Defaults to None
                               (any time).
            smstr (list of strings): The semesters the courses are in. Defaults
                                     to None (all semesters).
            srch_frz (string): I don't know what this is. Defaults to "."

        Returns:
            list of dictionaries: list of course descriptions

        """
        # Input processing
        if None in [smstr, campus, dept]:
            ti = TricoInfo()
        if smstr is None:
            smstr = ti.semesters
        if campus is None:
            campus = ti.campuses
        if dept is None:
            dept = ti.departments

        # Creating the search parameters
        params = [
            (".cgifields", "campus,dept,smstr,meettime"),
            ("Search", "Search"),
            ("crsnum", crsnum),
            ("instr", instr),
            ("meetday", meetday),
            ("srch_frz", srch_frz)
        ]
        params += [("smstr", s) for s in smstr]
        params += [("campus", c) for c in campus]
        params += [("dept", d) for d in dept]
        if meettime is not None:
            params += [("meettime", m) for m in meettime]

        # Get course page links
        num_links = self._get_num_links(params)
        paramss = [params[:]+[("run_tot", str(i))] for i in
                   range(0, num_links, 50)]
        linkss = self._pool.map(_TricoScraper_get_links, paramss)
        links = list(itertools.chain.from_iterable(linkss))

        # Get course descriptions
        courses = self._pool.map(_TricoScraper_get_course, links)
        return courses


def main():
    import json
    from time import time
    ts1 = TricoScraper(num_threads=1)
    tsa = TricoScraper()
    one_start = time()
    ts1.search()
    one_duration = time() - one_start
    all_start = time()
    tsa.search()
    all_duration = time() - all_start
    print(one_duration, 'vs', all_duration)


if __name__ == '__main__':
    main()
