"""
Important note: the name of the mongoDB "collection" is what links a "source"
with an "analyzer". So for an analyzer to use the data from a source, the name
of the collection must be the same in SOURCES_SETTINGS and ANALYSIS_SETTINGS.
"""

from sources import (SourceLog, MysqladminExtendedRelativeSource,
                     MysqladminExtendedAbsoluteSource,
                     )
from parsers import (NginxCacheParser, MysqladminExtendedRelativeParser,
                     MysqladminExtendedAbsoluteParser,
                     )
from analyzers import (CacheStatus, Upstream5xxStatus, AvgUpstreamResponseTimePerServer,
                       RequestsPerMinuteByType, MysqlQuestionsPerSecond,
                       MysqlSlowQueriesPerSecond,
                       )
MONGODB_NAME = 'mydb'
PROCESSED_COLL = 'processed'
PROCESSED_MAX_SIZE = 1 # in megabytes
NG_CACHE_COLL = 'ng_cache'
MYSQL_COLL = 'mysql_extended'
MAX_COLLECTION_SIZE = 50 # in megabytes

SOURCES_SETTINGS = [
    {'collection': NG_CACHE_COLL,
     'source': (SourceLog, {'host': 'us-ng1',
                            'filepath': '/var/log/nginx/cache.log'}),
     'parser': NginxCacheParser,
     },
    {'collection': NG_CACHE_COLL,
     'source': (SourceLog, {'host': 'us-ng1',
                            'filepath': '/var/log/nginx/cache.log'}),
     'parser': NginxCacheParser,
     },
    {'collection': MYSQL_COLL,
     'source': (MysqladminExtendedRelativeSource, {'host': 'us-my1',},),
     'parser': MysqladminExtendedRelativeParser,
     },
    {'collection': MYSQL_COLL,
     'source': (MysqladminExtendedRelativeSource, {'host': 'us-my2',},),
     'parser': MysqladminExtendedRelativeParser,
     },
    ]

ANALYSIS_SETTINGS = {
    'channel_name': '/topic/graph',
    'interval': 60,                 # in seconds
    'history_length': 120,        # number of processed data points to save
    'default_window_length': 65,        # in seconds
    'default_flot_options': {
        'series': {'stack': 0,
                   'bars': {'show': True, 'barWidth': 60*0.8*1000, 'lineWidth': 1,},},
        'xaxis': {'mode': "time",
                  'timeformat': "%H:%M",},
        },
    'groups': {
        'rpm': {
            'label': 'Requests/min',
            'format': '%d',
            'collection': NG_CACHE_COLL,
            'window_length': 120,
            'analyzers': [
                (RequestsPerMinuteByType, {'media': '1'}),
                (RequestsPerMinuteByType, {'media': '0'}),
                ],
            },
        'cache0': {
            'label': 'Cache status (non-media)',
            'format': '%.1f%%',
            'collection': NG_CACHE_COLL,
            'flot_options': {'yaxis': {'max': 100,},},
            'analyzers': [
                (CacheStatus, {'status': 'HIT', 'media': '0'}),
                (CacheStatus, {'status': 'MISS', 'media': '0'}),
                (CacheStatus, {'status': 'EXPIRED', 'media': '0'}),
                (CacheStatus, {'status': 'UPDATING', 'media': '0'}),
                (CacheStatus, {'status': 'STALE', 'media': '0'}),
                ],
            },
        'cache1': {
            'label': 'Cache status (media)',
            'format': '%.1f%%',
            'collection': NG_CACHE_COLL,
            'flot_options': {'yaxis': {'max': 100,},},
            'analyzers': [
                (CacheStatus, {'status': 'HIT', 'media': '1'}),
                (CacheStatus, {'status': 'MISS', 'media': '1'}),
                (CacheStatus, {'status': 'EXPIRED', 'media': '1'}),
                (CacheStatus, {'status': 'UPDATING', 'media': '1'}),
                (CacheStatus, {'status': 'STALE', 'media': '1'}),
                ],
            },
        'http_status': {
            'label': 'HTTP Status',
            'format': '%d',
            'collection': NG_CACHE_COLL,
            'flot_options': {'yaxis': {'min': 0,},},
            'analyzers': [
                (Upstream5xxStatus, {}),
                ],
            },
        'aurt': {
            'label': 'Avg Upstream Resp Time',
            'format': '%.2f',
            'collection': NG_CACHE_COLL,
            'analyzers': [
                (AvgUpstreamResponseTimePerServer, {'server_address': '10.111.111.241:80'}),
                (AvgUpstreamResponseTimePerServer, {'server_address': '10.111.111.210:80'}),
                (AvgUpstreamResponseTimePerServer, {'server_address': '10.111.111.173:80'}),
                ],
            },
        'mysql': {
            'label': 'MySQL Questions/sec',
            'format': '%.1f',
            'collection': MYSQL_COLL,
            'analyzers': [
                (MysqlQuestionsPerSecond, {'server': 'us-my1'}),
                (MysqlQuestionsPerSecond, {'server': 'us-my2'}),
                ],
            },
        },
    }
