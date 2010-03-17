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
        self.interval = settings['interval']
        self.channel_name = settings['channel_name']
        self.report_generator = FlotReportGenerator(settings)

    def recv_connected(self, msg):
        print 'Connected; producing data'
        self.timer = LoopingCall(self.loop)
        self.timer.start(self.interval)

    def loop(self):
        self.generate_data()
        self.send_data()

    def generate_data(self):
        self.data = self.report_generator.run()

    def send_data(self):
        jsondata = json.dumps(self.data)
        self.send(self.channel_name, jsondata)

if __name__ == '__main__':
    start_analyzer()
