import re
from pymongo import Connection, ASCENDING
from settings import MONGODB_NAME
from util import safe_divide

class BaseAnalyzer(object):
    """Base class not to be used directly.
    """
    def __init__(self, collection):
        self.coll = collection
        self.connect_to_mongo()

    def connect_to_mongo(self):
        conn = Connection()
        db = conn[MONGODB_NAME]
        self.mongo = db[self.coll]

class TotalRequests(BaseAnalyzer):
    label = 'Total Requests'
    format = '%8d'

    def run(self, time_limit):
        self.mongo.ensure_index('time')
        N_requests = self.mongo.find({'time': {'$gt': time_limit}}).count()
        return N_requests

class CacheHitRate(BaseAnalyzer):
    label = 'Cache hit rate'
    format = '%8.1f'

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('media', ASCENDING),
                                 ('status', ASCENDING)])
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('media', ASCENDING)])
        hits = self.mongo.find({'time': {'$gt': time_limit},
                                'media': '0',
                                'status': 'HIT',
                                }).count()
        total = self.mongo.find({'time': {'$gt': time_limit},
                                 'media': '0',
                                 }).count()
        hit_rate = safe_divide(100.0*hits, total)
        return hit_rate

class DomainRequests(BaseAnalyzer):
    format = '%8d'

    def __init__(self, collection, domain):
        super(DomainRequests, self).__init__(collection)
        self.label = self.domain = domain

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('domain', ASCENDING)])
        hits = self.mongo.find({'time': {'$gt': time_limit},
                                'domain': re.compile(self.domain),
                                }).count()
        return hits
