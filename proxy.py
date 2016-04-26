#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 mapleray <zhiwuliao#gmail.com>
#
# Distributed under terms of the MIT license.

import base64
import requests
from multiprocessing.dummy import Pool as ThreadPool


class Proxy(object):
    def __init__(self, max_page=1):
        self.max_page = max_page
        self.proxies = []
        self.checked_proxies = []
        self.s = requests.Session()
        self.headers = {
            'Host': 'proxy.peuland.com',
            'Origin': 'https://proxy.peuland.com',
            'Referer': 'https://proxy.peuland.com/proxy_list_by_category.htm',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2692.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'Cookie': 'peuland_id=35fefe23fedc52da9283ac5ed131cbab;PHPSESSID=pkm7b65es5ojb8oerc7a9i0q31; peuland_md5=ca1f57155f5638ade3c28a900fbdbd55;w_h=800; w_w=1280; w_cd=24; w_a_h=773; w_a_w=1280; php_id=1792520643'
        }
        self.s.headers.update(self.headers)
        self.url = 'https://proxy.peuland.com/proxy/search_proxy.php'

    def _parse_proxy(self):
        i = 1
        while (i <= self.max_page):
            payload = {
                'type': '',
                'country_code': 'CN',
                'is_clusters': '',
                'is_https': '',
                'level_type': 'anonymous',
                'search_type': 'all',
                'page': str(i),
            }
            r = self.s.post(self.url, data=payload)
            data = r.json()['data']
            for line in data:
                rate = int(base64.b64decode(line['time_downloadspeed']))
                if rate <= 7:
                    continue
                proxy_type = base64.b64decode(line['type'])
                ip = base64.b64decode(line['ip'])
                port = base64.b64decode(line['port'])
                self.proxies.append({proxy_type: ip + ':' + port})
            i = i + 1

    def _check_proxy(self, proxy, anonymous=False):

        try:
            r = requests.get('http://httpbin.org/ip', proxies=proxy, timeout=10)
            data = r.json()
            # 高匿检测
            if anonymous:
                if data['origin'] == proxy.values()[0].split(':')[0]:
                    self.checked_proxies.append(proxy)
            self.checked_proxies.append(proxy)
        except Exception as e:
            print e

    def get_proxy(self):
        self._parse_proxy()
        pool = ThreadPool(8)
        pool.map(self._check_proxy, self.proxies)
        pool.close()
        pool.join()
        return self.checked_proxies


if __name__ == '__main__':
    ins = Proxy()
    print ins.get_proxy()
