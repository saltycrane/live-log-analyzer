import time
from collections import defaultdict
from datetime import datetime, timedelta
from settings import NGINX_CACHE_ANALYSIS_SETTINGS

def main():
    Executive(NGINX_CACHE_ANALYSIS_SETTINGS).loop()

class Executive(object):
    def __init__(self, settings):
        self.windows = settings['windows']    # in minutes
        self.interval = settings['interval']  # in seconds
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
        format_category = "%20s"
        print
        print "".join([format_category % "Stats over the last"] +
                      ["%8s" % (str(w) + " min") for w in self.windows])
        print "-" * (20+8*len(self.windows))
        for a in self.analyzer_list:
            line = format_category % a.label
            for d in self.data[a.label]:
                line += a.format % d
            print line

if __name__ == '__main__':
    main()
