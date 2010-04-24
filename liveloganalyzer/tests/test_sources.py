from nose.tools import with_setup
from liveloganalyzer.sources import SourceLog

PATH_TEST_LOG = '/tmp/lla_testfile'
LINES_TEST_LOG = [
    'line1',
    'line2',
    'line3',
    ]

def create_test_log():
    fh = open(PATH_TEST_LOG, 'w')
    [fh.write(line+'\n') for line in LINES_TEST_LOG]
    fh.close()

class DummyProcess(object):
    def __init__(self):
        self.stdout = open(PATH_TEST_LOG, 'r')

@with_setup(create_test_log)
def test__assemble_ssh_command1():
    sl = SourceLog(ssh_params={'hostname': 'localhost',
                               },
                   filepath=PATH_TEST_LOG,
                   )
    sl._assemble_ssh_command()
    assert sl.ssh_params['host'] == 'localhost'
    assert sl.ssh_cmd == 'ssh  localhost "tail --follow=name %s"' % PATH_TEST_LOG

@with_setup(create_test_log)
def test__assemble_ssh_command2():
    sl = SourceLog(ssh_params={'hostname': 'localhost',
                               'host': 'local',
                               'identityfile': '/home/smithers/.ssh/id_rsa',
                               },
                   filepath=PATH_TEST_LOG,
                   )
    sl._assemble_ssh_command()
    assert sl.ssh_params['host'] == 'local'
    assert sl.ssh_cmd == 'ssh -oidentityfile=/home/smithers/.ssh/id_rsa localhost "tail --follow=name %s"' % PATH_TEST_LOG

@with_setup(create_test_log)
def test_get_line():
    sl = SourceLog(ssh_params={'hostname': 'localhost',
                               },
                   filepath=PATH_TEST_LOG,
                   )
    sl.p = DummyProcess()
    line = sl.get_line().rstrip()
    assert line == 'line1'
