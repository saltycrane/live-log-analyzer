import re
import textwrap
from pymongo import ASCENDING
from util import safe_divide


class RequestsPerMinuteByType(object):
    def __init__(self, mongo_collection, media):
        self.mongo = mongo_collection
        self.label = 'Media: %s' % media
        self.media = media

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('media', ASCENDING),
                                 ])
        N = self.mongo.find({'time': {'$gt': time_limit[0],
                                      '$lt': time_limit[1]},
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

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('media', ASCENDING),
                                 ('status', ASCENDING)])
        count = self.mongo.find({'time': {'$gt': time_limit[0],
                                          '$lt': time_limit[1]},
                                 'media': self.media,
                                 'status': self.status,
                                 }).count()
        total = self.mongo.find({'time': {'$gt': time_limit[0],
                                          '$lt': time_limit[1]},
                                 'media': self.media,
                                 'status': {'$ne': '-'},
                                 }).count()
        perc = safe_divide(100.0 * count, total)
        self.data = perc


class Upstream5xxStatus(object):
    def __init__(self, mongo_collection):
        self.mongo = mongo_collection
        self.label = '5xx'

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('ups_st', ASCENDING)])
        N = self.mongo.find({'time': {'$gt': time_limit[0],
                                      '$lt': time_limit[1]},
                             'ups_st': re.compile(r'5\d\d'),
                             }).count()
        self.data = N


class AvgUpstreamResponseTimePerServer(object):
    def __init__(self, mongo_collection, server_address):
        self.mongo = mongo_collection
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
                       'ups_ad': self.server_address, },
            initial={'count': 0, 'total': 0},
            reduce=textwrap.dedent('''
                function(doc, out) {
                    out.count++;
                    out.total += parseFloat(doc.ups_rt);
                }'''),
            finalize='function(out) {out.avg = out.total / out.count}',
            )
        if result:
            avg = result[0]['avg']
            self.data = avg
        else:
            self.data = 0.0


class AvgUpstreamResponseTimePerServerLoggedIn(object):
    """This one is the sh**
    """
    data_length = 1

    def __init__(self, mongo_collection, logged_in):
        self.mongo = mongo_collection
        self.logged_in = logged_in
        self.label = 'need to auto-generate'

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('ups_rt', ASCENDING),
                                 ('ups_ad', ASCENDING),
                                 ('wp_login', ASCENDING),
                                 ])
        result = self.mongo.group(
            key=['ups_ad'],
            condition={'time': {'$gt': time_limit[0], '$lt': time_limit[1]},
                       'ups_rt': {'$ne': '-'},
                       'wp_login': re.compile(self.logged_in),
                       },
            initial={'count': 0, 'total': 0},
            reduce=textwrap.dedent('''
                function(doc, out) {
                    out.count++;
                    out.total += parseFloat(doc.ups_rt);
                }'''),
            finalize='function(out) {out.avg = out.total / out.count}',
            )
        result = sorted(result, key=lambda item: item['ups_ad'])
        # debug = [r['ups_ad'] for r in result]
        # print debug
        if result:
            self.data = [r['avg'] for r in result]
            self.data_length = len(self.data)
        else:
            self.data = [0.0] * self.data_length


class WordpressLoggedIn(object):
    def __init__(self, mongo_collection):
        self.mongo = mongo_collection
        self.label = 'Wordpress logged in'

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('wp_login', ASCENDING), ])
        N = self.mongo.find({'time': {'$gt': time_limit[0],
                                      '$lt': time_limit[1]},
                             'wp_login': re.compile(r'wordpress_logged_in_'),
                             }).count()
        self.data = N


class WordpressLoggedInByUser(object):
    def __init__(self, mongo_collection, wp_user):
        self.mongo = mongo_collection
        self.wp_user = wp_user
        self.label = wp_user
        self.pattern = r'wordpress_logged_in_%s' % wp_user

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('wp_login', ASCENDING), ])
        N = self.mongo.find({'time': {'$gt': time_limit[0],
                                      '$lt': time_limit[1]},
                             'wp_login': re.compile(self.pattern),
                             }).count()
        self.data = N


class PhpErrorCountByServer(object):
    def __init__(self, mongo_collection, server):
        self.mongo = mongo_collection
        self.server = server
        self.label = server

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('server', ASCENDING)])
        N = self.mongo.find({'time': {'$gt': time_limit[0],
                                      '$lt': time_limit[1]},
                             'server': self.server,
                             }).count()
        self.data = N


class SyslogCountByServerAndProcess(object):
    def __init__(self, mongo_collection, server, process):
        self.mongo = mongo_collection
        self.server = server
        self.process = process
        self.label = server

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('server', ASCENDING),
                                 ('process', ASCENDING),
                                 ])
        N = self.mongo.find({'time': {'$gt': time_limit[0],
                                      '$lt': time_limit[1]},
                             # 'server': self.server,
                             # 'process': re.compile(self.process),
                             }).count()
        self.data = N


class GenericAverageValueAnalyzer(object):
    def __init__(self, mongo_collection, server, parameter,
                 label='generic avg value'):
        self.mongo = mongo_collection
        self.server = server
        self.parameter = parameter
        self.label = label

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('server', ASCENDING),
                                 ])
        result = self.mongo.group(
            key=None,
            condition={'time': {'$gt': time_limit[0], '$lt': time_limit[1]},
                       'server': self.server,
                       },
            initial={'count': 0, 'total': 0},
            reduce='''function(doc, out) {
                         out.count++;
                         out.total += parseFloat(doc.%s)
                      }''' % self.parameter,
            finalize='function(out) {out.avg = out.total / out.count}',
            )
        if result:
            self.data = result[0]['avg']
        else:
            self.data = 0


class MysqlQuestionsPerSecond(object):
    def __init__(self, mongo_collection, server):
        self.mongo = mongo_collection
        self.label = 'Questions/sec'
        self.server = server  # master or slave (e.g. us-my1 or us-my2)

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('server', ASCENDING),
                                 ('questions_persecond', ASCENDING)])
        result = self.mongo.group(
            key=None,
            condition={'time': {'$gt': time_limit[0], '$lt': time_limit[1]},
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
        self.server = server  # master or slave (e.g. us-my1 or us-my2)

    def run(self, time_limit):
        self.mongo.ensure_index([('time', ASCENDING),
                                 ('server', ASCENDING),
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
