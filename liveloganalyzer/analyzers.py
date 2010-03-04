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

class Heading(object):
    def __init__(self, heading):
        self.label = heading

    def run(self, dum):
        return ''

class GenericCount(BaseAnalyzer):
    def __init__(self, mongodb_name, collection, label):
        super(GenericCount, self).__init__(mongodb_name, collection)
        self.label = '  ' + label

    def run(self, time_limit):
        self.mongo.ensure_index('time')
        N = self.mongo.find({'time': {'$gt': time_limit[0], '$lt': time_limit[1]}}
                            ).count()

        return '%d' % N

class CacheStatus(BaseAnalyzer):
    def __init__(self, mongodb_name, collection, status, media):
        super(CacheStatus, self).__init__(mongodb_name, collection)
        self.status = status
        self.media = media
        self.label = '  %s (media: %s)' % (status, media)

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('media', ASCENDING),
                                 ('status', ASCENDING)])
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('media', ASCENDING)])
        count = self.mongo.find({'time': {'$gt': time_limit[0], '$lt': time_limit[1]},
                                 'media': self.media,
                                 'status': self.status,
                                 }).count()
        total = self.mongo.find({'time': {'$gt': time_limit[0], '$lt': time_limit[1]},
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
        self.label = '  %s (all)' % status

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('status', ASCENDING)])
        self.mongo.ensure_index('time')
        count = self.mongo.find({'time': {'$gt': time_limit[0], '$lt': time_limit[1]},
                                 'status': self.status,
                                 }).count()
        total = self.mongo.find({'time': {'$gt': time_limit[0], '$lt': time_limit[1]},
                                 }).count()
        perc = safe_divide(100.0*count, total)

        return '%.2f%% (%d/%d)' % (perc, count, total)

class DomainRequests(BaseAnalyzer):
    def __init__(self, mongodb_name, collection, domain):
        super(DomainRequests, self).__init__(mongodb_name, collection)
        self.domain = domain
        self.label = '  ' + domain

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('domain', ASCENDING)])
        hits = self.mongo.find({'time': {'$gt': time_limit[0], '$lt': time_limit[1]},
                                'domain': re.compile(self.domain),
                                }).count()
        return '%d' % hits

class Upstream4xxStatus(BaseAnalyzer):
    label = '  4xx status'

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('ups_st', ASCENDING)])
        N = self.mongo.find({'time': {'$gt': time_limit[0], '$lt': time_limit[1]},
                             'ups_st': re.compile(r'4\d\d'),
                             }).count()
        return '%d' % N

class Upstream5xxStatus(BaseAnalyzer):
    label = '  5xx status'

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('ups_st', ASCENDING)])
        N = self.mongo.find({'time': {'$gt': time_limit[0], '$lt': time_limit[1]},
                             'ups_st': re.compile(r'5\d\d'),
                             }).count()
        return '%d' % N

class AvgUpstreamResponseTime(BaseAnalyzer):
    label = '  All backends'

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('ups_rt', ASCENDING)])
        result = self.mongo.group(
            key=None,
            condition={'time': {'$gt': time_limit[0], '$lt': time_limit[1]},
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

class AvgUpstreamResponseTimePerServer(BaseAnalyzer):
    def __init__(self, mongodb_name, collection, server_address):
        super(AvgUpstreamResponseTimePerServer, self).__init__(mongodb_name, collection)
        self.server_address = server_address
        self.label = '  ' + server_address

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('ups_rt', ASCENDING),
                                 ('ups_ad', ASCENDING)])
        result = self.mongo.group(
            key=None,
            condition={'time': {'$gt': time_limit[0], '$lt': time_limit[1]},
                       'ups_rt': {'$ne': '-'},
                       'ups_ad': self.server_address,},
            initial={'count': 0, 'total': 0},
            reduce='function(doc, out) {out.count++; out.total += parseFloat(doc.ups_rt)}',
            finalize='function(out) {out.avg = out.total / out.count}',
            )
        if result:
            result = '%.3f (%d)' % (result[0]['avg'], result[0]['count'])
        else:
            result = '-'
        return result

