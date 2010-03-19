"""
Important note: the name of the mongoDB "collection" is what links a "source"
with an "analyzer". So for an analyzer to use the data from a source, the name
of the collection must be the same in SOURCES_SETTINGS and ANALYSIS_SETTINGS.
"""

from sources import (SourceLog, MysqladminExtendedRelativeSource,
                     MysqladminExtendedAbsoluteSource,
                     )
from parsers import (NginxCacheParser, MysqladminExtendedRelativeParser,
                     MysqladminExtendedAbsoluteParser, PhpErrorParser, SyslogParser,
                     )
from analyzers import (CacheStatus, Upstream5xxStatus, AvgUpstreamResponseTimePerServer,
                       RequestsPerMinuteByType, MysqlQuestionsPerSecond,
                       MysqlSlowQueriesPerSecond, WordpressLoggedIn, PhpErrorCountByServer,
                       SyslogCountByServerAndProcess,
                       )
MONGODB_NAME = 'mydb'
PROCESSED_MAX_SIZE = 1 # in megabytes
MAX_COLLECTION_SIZE = 50 # in megabytes
NG_CACHE_COLL = 'ng_cache'
SYSLOG_COLL = 'syslog'
PHP_ERROR_COLL = 'php_error'
MYSQL_COLL = 'mysql_extended'

SOURCES_SETTINGS = [
    {'source': (SourceLog, {'host': 'us-ng1', 'filepath': '/var/log/nginx/cache.log'}),
     'parser': NginxCacheParser,
     'collection': NG_CACHE_COLL,
     },
    {'source': (SourceLog, {'host': 'us-ng1', 'filepath': '/var/log/nginx/cache.log'}),
     'parser': NginxCacheParser,
     'collection': NG_CACHE_COLL,
     },
    {'source': (SourceLog, {'host': 'us-apa1', 'filepath': '/var/log/syslog'}),
     'parser': SyslogParser,
     'collection': SYSLOG_COLL,
     },
    {'source': (SourceLog, {'host': 'us-apa2', 'filepath': '/var/log/syslog'}),
     'parser': SyslogParser,
     'collection': SYSLOG_COLL,
     },
    {'source': (SourceLog, {'host': 'us-apa3', 'filepath': '/var/log/syslog'}),
     'parser': SyslogParser,
     'collection': SYSLOG_COLL,
     },
    {'source': (SourceLog, {'host': 'us-apa1', 'filepath': '/var/log/PHP_errors.log'}),
     'parser': PhpErrorParser,
     'collection': PHP_ERROR_COLL,
     },
    {'source': (SourceLog, {'host': 'us-apa2', 'filepath': '/var/log/PHP_errors.log'}),
     'parser': PhpErrorParser,
     'collection': PHP_ERROR_COLL,
     },
    {'source': (SourceLog, {'host': 'us-apa3', 'filepath': '/var/log/PHP_errors.log'}),
     'parser': PhpErrorParser,
     'collection': PHP_ERROR_COLL,
     },
    {'source': (MysqladminExtendedRelativeSource, {'host': 'us-my1',},),
     'parser': MysqladminExtendedRelativeParser,
     'collection': MYSQL_COLL,
     },
    {'source': (MysqladminExtendedRelativeSource, {'host': 'us-my2',},),
     'parser': MysqladminExtendedRelativeParser,
     'collection': MYSQL_COLL,
     },

    # {'collection': MYSQL_COLL,
    #  'source': (MysqladminExtendedAbsoluteSource, {'host': 'us-my1',},),
    #  'parser': MysqladminExtendedAbsoluteParser,
    #  },
    # {'collection': MYSQL_COLL,
    #  'source': (MysqladminExtendedAbsoluteSource, {'host': 'us-my2',},),
    #  'parser': MysqladminExtendedAbsoluteParser,
    #  },
    ]

PLOT_SET = {
    'rpm': {
        'label': 'Requests/min',
        'format': '%d',
        'collection': NG_CACHE_COLL,
        # 'window_length': 120,
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
        'flot_options': {'yaxis': {'min': 50, 'max': 100,},},
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
    'wp_login': {
        'label': 'WP logged in',
        'format': '%d',
        'collection': NG_CACHE_COLL,
        'flot_options': {'yaxis': {'min': 0,},},
        'analyzers': [
            (WordpressLoggedIn, {}),
            ],
        },
    'php_error': {
        'label': 'PHP error count',
        'format': '%d',
        'collection': PHP_ERROR_COLL,
        'flot_options': {'yaxis': {'min': 0,},},
        'analyzers': [
            (PhpErrorCountByServer, {'server': 'us-apa1'}),
            (PhpErrorCountByServer, {'server': 'us-apa2'}),
            (PhpErrorCountByServer, {'server': 'us-apa3'}),
            ],
        },
    's3fs': {
        'label': 's3fs count',
        'format': '%d',
        'collection': SYSLOG_COLL,
        'flot_options': {'yaxis': {'min': 0,},},
        'analyzers': [
            (SyslogCountByServerAndProcess, {'server': 'us-apa1', 'process': 's3fs'}),
            (SyslogCountByServerAndProcess, {'server': 'us-apa2', 'process': 's3fs'}),
            (SyslogCountByServerAndProcess, {'server': 'us-apa3', 'process': 's3fs'}),
            ],
        },
    'aurt': {
        'label': 'Avg Upstream Resp Time',
        'format': '%.2f',
        'collection': NG_CACHE_COLL,
        'analyzers': [
            (AvgUpstreamResponseTimePerServer, {'server_address': '10.111.111.241:80'}),
            (AvgUpstreamResponseTimePerServer, {'server_address': '10.111.111.173:80'}),
            (AvgUpstreamResponseTimePerServer, {'server_address': '10.111.111.210:80'}),
            ],
        },
    'mysql': {
        'label': 'MySQL Questions/sec',
        'format': '%.1f',
        'collection': MYSQL_COLL,
        'flot_options': {'yaxis': {'max': 1100,},},
        'analyzers': [
            (MysqlQuestionsPerSecond, {'server': 'us-my1'}),
            (MysqlQuestionsPerSecond, {'server': 'us-my2'}),
            ],
        },
    }

ANALYSIS_SETTINGS = {
    'channel_name': '/topic/graph',
    'time_periods': [
        {'interval': 5*60,                 # in seconds
         'history_length': 144,        # number of processed data points to save
         'default_window_length': 5*60+5,        # in seconds
         'default_flot_options': {
                'series': {'stack': 0,
                           'bars': {'show': True, 'barWidth': (5*60)*(0.8*1000), 'lineWidth': 1,},},
                'xaxis': {'mode': "time",
                          'timeformat': "%H:%M",
                          'labelWidth': 20,
                          'labelHeight': 8,
                          },
                },
         'groups': PLOT_SET,
         },
        {'interval': 5,                 # in seconds
         'history_length': 60,        # number of processed data points to save
         'default_window_length': 29,        # in seconds
         'default_flot_options': {
                'series': {'stack': 0,
                           'bars': {'show': True, 'barWidth': (5)*(0.8*1000), 'lineWidth': 1,},},
                'xaxis': {'mode': "time",
                          'timeformat': ":%M",
                          'labelWidth': 20,
                          'labelHeight': 8,
                          },
                },
         'groups': PLOT_SET,
         },
        ],
    }
