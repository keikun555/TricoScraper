"""
Kei Imada
20180815
Scraper for trico.haverford.edu
"""
import bs4
import certifi
import urllib3 as urllib
from tricoglobals import TRICO_URL


class TricoInfo(object):
    def __init__(self, trico_url=TRICO_URL, ssl=True):
        if ssl:
            http = urllib.PoolManager(cert_reqs='CERT_REQUIRED',
                                      ca_certs=certifi.where())
        else:
            http = urllib.PoolManager()
        self._req = http.request('GET', trico_url)
        self._soup = bs4.BeautifulSoup(self._req.data, 'html.parser')
        # semesters
        self.semesters = [e['value'] for e in
                          (self._soup.find_all('input',
                                               {'name': 'smstr'}))]
        # campuses
        self.campuses = [e['value'] for e in
                         (self._soup.find_all('input',
                                              {'name': 'campus'}))]
        # departments
        dept_select_element = self._soup.find('select',
                                              {'name': 'dept'})
        self.departments = [e['value'] for e in
                            dept_select_element.findChildren('option')]
        # meetdays
        meetday_select_element = self._soup.find('select',
                                                 {'name': 'meetday'})
        self.meetdays = [e['value'] for e in
                         meetday_select_element.findChildren('option')]
        # meettimes
        meettime_select_element = self._soup.find('select',
                                                  {'name': 'meettime'})
        self.meettimes = [e['value'] for e in
                          meettime_select_element.findChildren('option')]


def main():
    ti = TricoInfo()
    print(ti.semesters)
    print(ti.campuses)
    print(ti.departments)
    print(ti.meetdays)
    print(ti.meettimes)


if __name__ == '__main__':
    main()
