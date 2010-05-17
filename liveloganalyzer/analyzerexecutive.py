from pprint import pprint
import simplejson as json
from stompservice import StompClientFactory
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from settings import ANALYSIS_SETTINGS
from reportgenerators import FlotReportGenerator


def start_analyzer():
    ae = AnalyzerExecutive(ANALYSIS_SETTINGS)
    reactor.connectTCP('localhost', 61613, ae)
    reactor.run()


class AnalyzerExecutive(StompClientFactory):
    def __init__(self, settings):
        self.channel_name = settings['channel_name']
        self.time_periods = settings['time_periods']
        self.intervals = []
        self.report_generators = []
        self.instantiate_report_generators()

    def instantiate_report_generators(self):
        """Do this once for each report generator because we want to connect
        to mongoDB only once
        """
        for i, settings in enumerate(self.time_periods):
            processed_collection = 'processed_%d' % i
            rg = FlotReportGenerator(settings, i, processed_collection)
            self.intervals.append(settings['interval'])
            self.report_generators.append(rg)

    def recv_connected(self, msg):
        """Start infinite loops for each of the time periods
        """
        for i in range(len(self.report_generators)):
            self.timer = LoopingCall(self.generate_and_send_data, i)
            self.timer.start(self.intervals[i])

    def generate_and_send_data(self, i):
        """This is called every loop
        """
        self.report_generators[i].run()
        jsondata = json.dumps(self.report_generators[i].out)
        self.send(self.channel_name, jsondata)


if __name__ == '__main__':
    start_analyzer()
