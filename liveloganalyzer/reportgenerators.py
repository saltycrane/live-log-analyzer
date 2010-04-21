import copy
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pprint import pprint
from pymongo import Connection, ASCENDING, DESCENDING
from pymongo.errors import CollectionInvalid, InvalidStringData
from debuglogging import error
from settings import MONGODB_NAME, PROCESSED_MAX_SIZE
from util import smart_str, convert_time_for_flot, transpose_list_of_lists

class FlotReportGenerator(object):
    """
    Example data structures:

    MYCOMPANY_ANALYSIS_SETTINGS = {
        'interval': 2,
        'window_length': 30,
        'history_length': 5,
        'groups': {
            'rpm': {
                'label': 'Requests/min',
                'collection': NG_CACHE_COLL,
                'analyzers': [
                    (RequestsPerMinuteByType, {'media': '1'}),
                    (RequestsPerMinuteByType, {'media': '0'}),
                    ],
                },
            'cache0': {
                'label': 'Cache status (non-media)',
                'collection': NG_CACHE_COLL,
                'analyzers': [
                    (CacheStatus, {'status': 'HIT', 'media': '0'}),
                    (CacheStatus, {'status': 'MISS', 'media': '0'}),
                    (CacheStatus, {'status': 'EXPIRED', 'media': '0'}),
                    (CacheStatus, {'status': 'UPDATING', 'media': '0'}),
                    (CacheStatus, {'status': 'STALE', 'media': '0'}),
                    ],
                },
            'http_status': {
                'label': 'HTTP Status',
                'collection': NG_CACHE_COLL,
                'analyzers': [
                    (Upstream5xxStatus, {}),
                    ],
                },
            'aurt': {
                'label': 'Avg Upstream Resp Time',
                'collection': NG_CACHE_COLL,
                'analyzers': [
                    (AvgUpstreamResponseTimePerServer, {'server_address': '10.242.19.241:80'}),
                    (AvgUpstreamResponseTimePerServer, {'server_address': '10.242.15.210:80'}),
                    (AvgUpstreamResponseTimePerServer, {'server_address': '10.244.109.173:80'}),
                    ],
                },
            },
        }
    self.labels = {'aurt': 'Avg Upstream Resp Time',
                   'cache0': 'Cache status (non-media)',
                   'cache1': 'Cache status (media)',
                   'http_status': 'HTTP Status',
                   'rpm': 'Requests/min',
                   }
    self.datapoint = {'aurt': [(1268674519000.0, 0.90570588235294125),
                               (1268674519000.0, 0.77833333333333332),
                               (1268674519000.0, 1.3899444444444446)],
                      'cache0': [(1268674519000.0, 46.511627906976742),
                                 (1268674519000.0, 22.093023255813954),
                                 (1268674519000.0, 30.232558139534884),
                                 (1268674519000.0, 1.1627906976744187),
                                 (1268674519000.0, 0.0)],
                      'http_status': [(1268674519000.0, 0)],
                      'rpm': [(1268674519000.0, 142.0), (1268674519000.0, 422.0)]
                      }
    self.history = {u'aurt': [[[1268674511000.0, 1.0144782608695653],
                               [1268674513000.0, 1.0745217391304347],
                               [1268674515000.0, 1.0416666666666667],
                               [1268674517000.0, 0.94589999999999996],
                               [1268674519000.0, 0.90570588235294125]],
                              [[1268674511000.0, 0.78129166666666638],
                               [1268674513000.0, 0.75104347826086959],
                               [1268674515000.0, 0.71394999999999986],
                               [1268674517000.0, 0.73719999999999997],
                               [1268674519000.0, 0.77833333333333332]],
                              [[1268674511000.0, 1.0567826086956524],
                               [1268674513000.0, 1.0523181818181819],
                               [1268674515000.0, 1.0310526315789474],
                               [1268674517000.0, 1.3911578947368421],
                               [1268674519000.0, 1.3899444444444446]]],
                    u'cache0': [[[1268674511000.0, 35.416666666666664],
                                 [1268674513000.0, 40.0],
                                 [1268674515000.0, 42.391304347826086],
                                 [1268674517000.0, 42.045454545454547],
                                 [1268674519000.0, 46.511627906976742]],
                                [[1268674511000.0, 28.125],
                                 [1268674513000.0, 26.0],
                                 [1268674515000.0, 26.086956521739129],
                                 [1268674517000.0, 22.727272727272727],
                                 [1268674519000.0, 22.093023255813954]],
                                [[1268674511000.0, 34.375],
                                 [1268674513000.0, 33.0],
                                 [1268674515000.0, 30.434782608695652],
                                 [1268674517000.0, 34.090909090909093],
                                 [1268674519000.0, 30.232558139534884]],
                                [[1268674511000.0, 2.0833333333333335],
                                 [1268674513000.0, 1.0],
                                 [1268674515000.0, 1.0869565217391304],
                                 [1268674517000.0, 1.1363636363636365],
                                 [1268674519000.0, 1.1627906976744187]],
                                [[1268674511000.0, 0.0],
                                 [1268674513000.0, 0.0],
                                 [1268674515000.0, 0.0],
                                 [1268674517000.0, 0.0],
                                 [1268674519000.0, 0.0]]],
                    u'http_status': [[[1268674511000.0, 0],
                                      [1268674513000.0, 0],
                                      [1268674515000.0, 0],
                                      [1268674517000.0, 0],
                                      [1268674519000.0, 0]]],
                    u'rpm': [[[1268674511000.0, 222.0],
                              [1268674513000.0, 222.0],
                              [1268674515000.0, 188.0],
                              [1268674517000.0, 152.0],
                              [1268674519000.0, 142.0]],
                             [[1268674511000.0, 404.0],
                              [1268674513000.0, 434.0],
                              [1268674515000.0, 442.0],
                              [1268674517000.0, 440.0],
                              [1268674519000.0, 422.0]]]
                    }
    self.out = {'history_length': 5,
                'window_length': 30,
                'current_value': {'rpm': '4', 'HIT0': '4.0',},
                'labels': <self.labels>
                'history': <self.history>
                }
    """
    def __init__(self, settings, index, processed_collection):
        self.history_length = settings['history_length']                # N to save
        self.default_window_length = settings['default_window_length']  # in seconds
        self.default_flot_options = settings['default_flot_options']
        self.groups = settings['groups']
        self.index = index
        self.processed_collection = processed_collection
        self.mongo_raw = {}
        self.history = {}
        self.out = {}
        self.connect_to_mongo()

    def connect_to_mongo(self):
        """Connect to the mongoDB collection for storing history data
        """
        conn = Connection()
        db = conn[MONGODB_NAME]

        # get mongodb processed collection
        # db.drop_collection(self.processed_collection)
        try:
            self.mongo_processed = db.create_collection(
                self.processed_collection,
                {'capped': True, 'size': PROCESSED_MAX_SIZE*1048576,},
                )
        except CollectionInvalid:
            self.mongo_processed = db[self.processed_collection]

        # get mongodb raw collections
        for groupname, groupdata in self.groups.iteritems():
            self.mongo_raw[groupname] = db[groupdata['collection']]

    def run(self):
        """Generate all the data to be passed to flot
        """
        self.create_metadata()
        self.calc_window_endpoints()
        self.run_analyzers_for_all_groups()
        self.write_datapoint_to_mongodb()
        self.get_and_assemble_history_data_for_flot()
        self.assemble_current_datapoints()
        self.prepare_output_data()

    def create_metadata(self):
        """Assemble metadata data structures to send to the web frontend
        """
        self.labels = dict([
                (groupname, groupdata['label'])
                for groupname, groupdata in self.groups.iteritems()
                ])
        def get_flot_options():
            default = copy.deepcopy(self.default_flot_options)
            if 'flot_options' in groupdata:
                default.update(groupdata['flot_options'])
            return default
        self.flot_options = dict([
                (groupname, get_flot_options())
                 for groupname, groupdata in self.groups.iteritems()
                 ])

    def calc_window_endpoints(self):
        """Calculate the window start and end points to be passed to each analyzer
        """
        window_end = datetime.now()

        def calc_window_endpoints_single():
            window_length = self.default_window_length
            if 'window_length' in groupdata:
                window_length = groupdata['window_length']
            window_start = window_end - timedelta(seconds=window_length)
            return (window_start, window_end)
        self.window_endpoints = dict([
                (groupname, calc_window_endpoints_single())
                for groupname, groupdata in self.groups.iteritems()
                ])
        self.flot_timestamp = dict([
                (groupname, convert_time_for_flot(self.window_endpoints[groupname][0]))
                for groupname, groupdata in self.groups.iteritems()
                ])

    def run_analyzers_for_all_groups(self):
        """Loop through the list of groups (plots) to create and generate datapoints
        """
        def run_list_of_analyzers(analyzers_and_kwargs):
            """Given a list of tuples (analyzer classes, kwargs), run each analyzer,
            and return a list of the datapoints of each analyzer (for a single point
            in time)
            """
            def run_analyzer(analyzer, kwargs):
                """Instantiate the given analyzer, passing it the mongodb collection
                object and kwargs, run it, and return a datapoint as a tuple
                (timestamp, data) or (timestamp, [data1, data2, ...])
                """
                a = analyzer(self.mongo_raw[groupname], **kwargs)
                a.run(self.window_endpoints[groupname])
                return (self.flot_timestamp[groupname], a.data)
            def flatten(subpoint):
                """
                If subpoint is of the form:
                    (timestamp, [data1, data2, ...])
                    Return: [(timstamp, data1), (timestamp, data2), ...]
                Elif subpoint is of the form:
                    (timestamp, data)
                    Return: [(timestamp, data)]
                """
                if isinstance(subpoint[1], list):
                    return [(subpoint[0], d) for d in subpoint[1]]
                else:
                    return [subpoint]

            unflattened = [run_analyzer(aclass, kwargs)
                           for aclass, kwargs in analyzers_and_kwargs]
            flattened_step1 = [flatten(uf) for uf in unflattened]
            flattened_step2 = [f2
                               for f1 in flattened_step1
                               for f2 in f1]
            return flattened_step2
            # return [run_analyzer(aclass, kwargs)
            #         for aclass, kwargs in analyzers_and_kwargs]
            # toreturn = []
            # for aclass, kwargs in analyzers_and_kwargs:
            #     unflattened = run_analyzer(aclass, kwargs)
            #     flattened = flatten(unflattened)
            #     for f in flattened:
            #         toreturn.append(f)
            # return f

        self.datapoint = dict([
                (groupname, run_list_of_analyzers(groupdata['analyzers']))
                for groupname, groupdata in self.groups.iteritems()
                ])

    def write_datapoint_to_mongodb(self):
        """Write datapoint data structure to mongoDB
        """
        try:
            self.mongo_processed.insert(self.datapoint)
        except InvalidStringData, e:
            error('%s\n%s' % (str(e), line))

    def get_and_assemble_history_data_for_flot(self):
        """Get history data from mongoDB and assemble it for transmission to a flot
        stacked bar chart
        """
        def remove_id_keys(datapoint):
            del datapoint['_id']
            return datapoint

        def transpose_history_data(history_data):
            return dict([
                    (k, transpose_list_of_lists(lol))
                    for k, lol in history_data.iteritems()
                    ])

        datapoints = self.mongo_processed.find().sort('$natural', DESCENDING).limit(self.history_length)
        datapoints = [remove_id_keys(dp) for dp in datapoints]

        self.history = defaultdict(list)
        for datapoint in reversed(list(datapoints)):
            for k, v in datapoint.iteritems():
                self.history[k].append(v)
        self.history = transpose_history_data(self.history)

    def assemble_current_datapoints(self):
        """Assemble a data structure of all the data points for the current time
        formatted according to self.groups[groupname]['format']
        """
        self.current_data = dict([
                (groupname, [groupdata['format'] % point[1]
                             for point in self.datapoint[groupname]])
                for groupname, groupdata in self.groups.iteritems()
                ])

    def prepare_output_data(self):
        self.out['index'] = self.index
        self.out['history_length'] = self.history_length
        self.out['labels'] = self.labels
        self.out['current_data'] = self.current_data
        self.out['flot_options'] = self.flot_options
        self.out['history'] = self.history
