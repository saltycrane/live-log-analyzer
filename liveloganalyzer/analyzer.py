import re
import time
from datetime import datetime, timedelta
from pymongo import Connection
from settings import MONGODB_NAME, NG_CACHE_COLL, DOMAINS

def main():
    a = NginxCacheAnalyzer()
    a.loop()

class BaseAnalyzer(object):
    def connect_to_mongo(self):
        conn = Connection()
        db = conn[MONGODB_NAME]
        self.mongo = db[self.coll]

class NginxCacheAnalyzer(BaseAnalyzer):
    def __init__(self):
        self.coll = NG_CACHE_COLL
        self.connect_to_mongo()

    def loop(self):
        while True:
            time_span = 60
            print
            print 'Stats over last %d seconds:' % time_span
            self.get_requests_per(time_span)
            self.cache_hit_rate(time_span)
            self.domains(time_span)
            time.sleep(2)

    def get_requests_per(self, time_span):
        """Get the number of requests in the last "time_span_seconds" seconds
        """
        d = datetime.now() - timedelta(seconds=time_span)
        N_requests = self.mongo.find({'time': {'$gt': d}}).count()
        print '   Total requests: %d' % N_requests

    def cache_hit_rate(self, time_span):
        d = datetime.now() - timedelta(seconds=time_span)
        hits = self.mongo.find({'time': {'$gt': d},
                                'media': '0',
                                'status': 'HIT',
                                }).count()
        total = self.mongo.find({'time': {'$gt': d},
                                 'media': '0',
                                 }).count()
        hit_rate = safe_divide(100.0*hits, total)
        print '   Cache hit rate: %.1f%%' % hit_rate

    def domains(self, time_span):
        d = datetime.now() - timedelta(seconds=time_span)
        hits = {}
        for domain in DOMAINS:
            hits[domain] = self.mongo.find({'time': {'$gt': d},
                                            'domain': re.compile(domain),
                                            }).count()
            print '   %s: %d' % (domain, hits[domain])

def safe_divide(dividend, divisor, dbz=0):
    if divisor == 0:
        return dbz
    else:
        return dividend/divisor

if __name__ == '__main__':
    main()
