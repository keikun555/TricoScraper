"""
Kei Imada
20180815
Scraper for trico.haverford.edu
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
    req = requests.get(TRICO_URL, params=params)
    soup = bs4.BeautifulSoup(req.text, 'html.parser')
    table = soup.find('table',
                      {'width': '100%', 'border': '2'})
    a_elements = table.findChildren('a')
    links = [TRICO_PREFIX+a['href'] for a in a_elements]
    return links


def _TricoScraper_get_course(url):
    req = requests.get(url)
    soup = bs4.BeautifulSoup(req.text, 'html.parser')
    course = {}
    rows = soup.findChild('table').findChildren('tr')
    for row in rows:
        [key, value] = [t.text for t in row.findChildren('td')]
        course[key] = value
    return course


class TricoScraper(object):
    def __init__(self, num_threads=multi.cpu_count(), ssl=True):
        self._pool = multi.Pool(num_threads)
        if ssl:
            self._http = urllib.PoolManager(cert_reqs='CERT_REQUIRED',
                                            ca_certs=certifi.where())
        else:
            self._http = urllib.PoolManager()

    def _get_num_links(self, params):
        req = requests.get(TRICO_URL, params=params)
        soup = bs4.BeautifulSoup(req.text, 'html.parser')
        return int(soup.find('font').findChild('b').string.split(' ')[-1])

    def search(self,
               campus=None,
               crsnum=".",
               dept=None,
               instr=".",
               meetday=".",
               smstr=None,
               srch_frz="."):
        if None in [smstr, campus, dept]:
            ti = TricoInfo()
        if smstr is None:
            smstr = ti.semesters
        if campus is None:
            campus = ti.campuses
        if dept is None:
            dept = ti.departments
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
        num_links = self._get_num_links(params)
        paramss = [params[:]+[("run_tot", str(i))] for i in
                   range(0, num_links, 50)]
        linkss = self._pool.map(_TricoScraper_get_links, paramss)
        links = list(itertools.chain.from_iterable(linkss))
        courses = self._pool.map(_TricoScraper_get_course, links)
        return courses


def main():
    ts = TricoScraper()
    ts.search(smstr=['Fall_2018'], campus=['Swarthmore'])


if __name__ == '__main__':
    main()
