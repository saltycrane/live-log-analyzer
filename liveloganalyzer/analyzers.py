import re
from pymongo import Connection, ASCENDING
from util import safe_divide

class BaseAnalyzer(object):
    """Base class not to be used directly.
    """
    def __init__(self, mongodb_name, collection):
        # connect to mongodb
        conn = Connection()
        db = conn[mongodb_name]
        self.mongo = db[collection]

class TotalRequests(BaseAnalyzer):
    label = 'Total requests'

    def run(self, time_limit):
        self.mongo.ensure_index('time')
        N_requests = self.mongo.find({'time': {'$gt': time_limit}}).count()

        return '%8d' % N_requests

class CacheStatus(BaseAnalyzer):
    def __init__(self, mongodb_name, collection, status, media):
        super(CacheStatus, self).__init__(mongodb_name, collection)
        self.status = status
        self.media = media
        self.label = 'Cache %s (media: %s)' % (status, media)

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('media', ASCENDING),
                                 ('status', ASCENDING)])
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('media', ASCENDING)])
        count = self.mongo.find({'time': {'$gt': time_limit},
                                 'media': self.media,
                                 'status': self.status,
                                 }).count()
        total = self.mongo.find({'time': {'$gt': time_limit},
                                 'media': self.media,
                                 }).count()
        perc = safe_divide(100.0*count, total)

        return '%.1f%% (%d/%d)' % (perc, count, total)

class CacheStatusAll(BaseAnalyzer):
    """Same as CacheStatus except don't check the media flag
    """
    def __init__(self, mongodb_name, collection, status):
        super(CacheStatusAll, self).__init__(mongodb_name, collection)
        self.status = status
        self.label = 'Cache %s (all)' % status

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('status', ASCENDING)])
        self.mongo.ensure_index('time')
        count = self.mongo.find({'time': {'$gt': time_limit},
                                 'status': self.status,
                                 }).count()
        total = self.mongo.find({'time': {'$gt': time_limit},
                                 }).count()
        perc = safe_divide(100.0*count, total)

        return '%.2f%% (%d/%d)' % (perc, count, total)

class DomainRequests(BaseAnalyzer):
    def __init__(self, mongodb_name, collection, domain):
        super(DomainRequests, self).__init__(mongodb_name, collection)
        self.label = self.domain = domain

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('domain', ASCENDING)])
        hits = self.mongo.find({'time': {'$gt': time_limit},
                                'domain': re.compile(self.domain),
                                }).count()
        return '%d' % hits

class Upstream4xxStatus(BaseAnalyzer):
    label = 'Upstream 4xx status'

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('ups_st', ASCENDING)])
        N = self.mongo.find({'time': {'$gt': time_limit},
                             'ups_st': re.compile(r'4\d\d'),
                             }).count()
        return '%d' % N

class Upstream5xxStatus(BaseAnalyzer):
    label = 'Upstream 5xx status'

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('ups_st', ASCENDING)])
        N = self.mongo.find({'time': {'$gt': time_limit},
                             'ups_st': re.compile(r'5\d\d'),
                             }).count()
        return '%d' % N

class AvgUpstreamResponseTime(BaseAnalyzer):
    label = 'Avg response time'

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('ups_rt', ASCENDING)])
        result = self.mongo.group(
            key=None,
            condition={'time': {'$gt': time_limit},
                       'ups_rt': {'$ne': '-'}},
            initial={'count': 0, 'total': 0},
            reduce='function(doc, out) {out.count++; out.total += parseFloat(doc.ups_rt)}',
            finalize='function(out) {out.avg = out.total / out.count}',
            )
        if result:
            result = '%.3f' % result[0]['avg']
        else:
            result = '-'
        return result
