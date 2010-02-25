from subprocess import Popen, PIPE, STDOUT
from threading import Thread
from pymongo import Connection
from pymongo.errors import CollectionInvalid
from settings import MONGODB_NAME, MAX_COLLECTION_SIZE, LOGS
from util import smart_str

def main():
    for params in LOGS:
        t = Thread(target=run_one, args=params)
        t.start()

def run_one(*params):
    s = SourceLog(*params)
    s.start()

class SourceLog(object):
    """A source log file on a remote host.
    """
    def __init__(self, host, filepath, parser, collection):
        self.host = host
        self.filepath = filepath
        self.parser = parser
        self.coll = collection

    def start(self):
        self.connect_to_mongo()
        self.get_stream()
        self.store_data()

    def connect_to_mongo(self):
        conn = Connection()
        db = conn[MONGODB_NAME]
        try:
            self.mongo = db.create_collection(
                self.coll, {'capped': True, 'size': MAX_COLLECTION_SIZE,})
        except CollectionInvalid:
            self.mongo = db[self.coll]

    def get_stream(self):
        """Tail -f the remote file.
        Sets self.stream, a file object of the stdout+stderr.
        """
        cmd = 'ssh -f %s tail -f %s' % (self.host, self.filepath)
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
        self.stream = p.stdout

    def store_data(self):
        while True:
            line = self.stream.readline()
            # line = unicode(line).encode('utf-8')
            line = smart_str(line)
            data = self.parser.parse_line(line)
            if data:
                data['server'] = self.host
                if 'url' not in data:
                    data['url'] = '-'
                print data['server'], data['time'], data['url']
                self.mongo.insert(data)
            else:
                raise Exception(line)

if __name__ == '__main__':
    main()
