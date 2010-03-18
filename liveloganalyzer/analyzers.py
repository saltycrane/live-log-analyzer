import re
from pprint import pprint
from pymongo import Connection, ASCENDING
from util import safe_divide

class RequestsPerMinuteByType(object):
    def __init__(self, mongo_collection, media):
        self.mongo = mongo_collection
        self.label = 'Media: %s' % media
        self.media = media
        self.key = 'rpm%s' % media

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('media', ASCENDING),
                                 ])
        N = self.mongo.find({'time': {'$gt': time_limit[0], '$lt': time_limit[1]},
                             'media': self.media,
                             }).count()
        td = time_limit[1] - time_limit[0]
        self.data = 60.0 * safe_divide(float(N), td.seconds)

class CacheStatus(object):
    def __init__(self, mongo_collection, status, media):
        self.mongo = mongo_collection
        self.status = status
        self.media = media
        self.label = '  %s (media: %s)' % (status, media)
        self.key = '%s%s' % (status, media)

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('media', ASCENDING),
                                 ('status', ASCENDING)])
        count = self.mongo.find({'time': {'$gt': time_limit[0], '$lt': time_limit[1]},
                                 'media': self.media,
                                 'status': self.status,
                                 }).count()
        total = self.mongo.find({'time': {'$gt': time_limit[0], '$lt': time_limit[1]},
                                 'media': self.media,
                                 'status': {'$ne': '-'},
                                 }).count()
        perc = safe_divide(100.0*count, total)
        self.data = perc

class Upstream5xxStatus(object):
    def __init__(self, mongo_collection):
        self.mongo = mongo_collection
        self.label = '5xx'
        self.key = '5xx'

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('ups_st', ASCENDING)])
        N = self.mongo.find({'time': {'$gt': time_limit[0], '$lt': time_limit[1]},
                             'ups_st': re.compile(r'5\d\d'),
                             }).count()
        self.data = N

class AvgUpstreamResponseTimePerServer(object):
    def __init__(self, mongo_collection, server_address):
        self.mongo = mongo_collection
        self.server_address = server_address
        self.label = '  ' + server_address
        self.key = re.sub(r'\.', '-', server_address)
        self.key = re.sub(r':80', '', self.key)

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
            avg = result[0]['avg']
            count = result[0]['count']
            self.data = avg
        else:
            self.data = 0.0

class MysqlQuestionsPerSecond(object):
    def __init__(self, mongo_collection, server):
        self.mongo = mongo_collection
        self.label = 'Questions/sec'
        self.key = 'qps'
        self.server = server # master or slave (e.g. us-my1 or us-my2)

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('questions_persecond', ASCENDING)])
        result = self.mongo.group(
            key=None,
            condition={'time': {'$gt': time_limit[0], '$lt': time_limit[1]},
                       # 'questions_persecond': {'$exists': 'true'}, # this doesnt work
                       'questions_persecond': {'$gt': 0},
                       'server': self.server,
                       },
            initial={'count': 0, 'total': 0},
            reduce='''function(doc, out) {
                         out.count++;
                         out.total += parseFloat(doc.questions_persecond)
                      }''',
            finalize='function(out) {out.avg = out.total / out.count}',
            )
        if result:
            self.data = result[0]['avg']
        else:
            self.data = 0

class MysqlSlowQueriesPerSecond(object):
    def __init__(self, mongo_collection, server):
        self.mongo = mongo_collection
        self.label = 'Slow queries/sec'
        self.key = 'sqps'
        self.server = server # master or slave (e.g. us-my1 or us-my2)

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('slow_queries_persecond', ASCENDING)])
        result = self.mongo.group(
            key=None,
            condition={'time': {'$gt': time_limit[0], '$lt': time_limit[1]},
                       'slow_queries_persecond': {'$gt': 0},
                       'server': self.server,
                       },
            initial={'count': 0, 'total': 0},
            reduce='''function(doc, out) {
                         out.count++;
                         out.total += parseFloat(doc.slow_queries_persecond)
                      }''',
            finalize='function(out) {out.avg = out.total / out.count}',
            )
        if result:
            self.data = result[0]['avg']
        else:
            self.data = 0
