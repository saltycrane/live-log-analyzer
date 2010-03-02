import time
from collections import defaultdict
from datetime import datetime, timedelta
from settings import NGINX_CACHE_ANALYSIS_SETTINGS

def main():
    Executive(NGINX_CACHE_ANALYSIS_SETTINGS).loop()

class Executive(object):
    def __init__(self, settings):
        self.windows = settings['windows']                       # in minutes
        self.interval = settings['interval']                     # in seconds
        self.column_width_data = settings['column_width_data']   # in characters
        self.column_width_label = settings['column_width_label'] # in characters
        self.analyzer_list = settings['analyzers']

    def loop(self):
        while True:
            self.calc_time_windows()
            self.analyze()
            self.print_stats()
            time.sleep(self.interval)

    def calc_time_windows(self):
        now = datetime.now()
        self.time_limits = [now - timedelta(minutes=window) for window in self.windows]

    def analyze(self):
        self.data = defaultdict(list)
        for a in self.analyzer_list:
            for tl in self.time_limits:
                d = a.run(tl)
                self.data[a.label].append(d)

    def print_stats(self):
        format_label = "%%%ds" % self.column_width_label
        format_data = "%%%ds" % self.column_width_data
        print
        print "".join([format_label % "Stats over the last"] +
                      [format_data % (str(w) + " min") for w in self.windows])
        print "-" * (self.column_width_label + self.column_width_data*len(self.windows))
        for a in self.analyzer_list:
            line = format_label % a.label
            for d in self.data[a.label]:
                line += format_data % d
            print line

if __name__ == '__main__':
    main()
