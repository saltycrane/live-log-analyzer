import time
from subprocess import Popen, PIPE, STDOUT
from debuglogging import error

class SourceBase(object):
    """Subclasses should define instance attributes self.host, self.cmd, self.encoding
    and optionally the instance method self.filter()
    """
    def start_stream(self):
        sshcmd = 'ssh %s "%s"' % (self.host, self.cmd)
        self.p = Popen(sshcmd, shell=True, stdout=PIPE, stderr=STDOUT)

    def get_line(self):
        while True:
            line = self.p.stdout.readline()
            if line == '' and self.p.poll() != None:
                raise Exception('Child process exited for host %s: %s' % (self.host, self.cmd))
            line = unicode(line, encoding=self.encoding, errors='replace')
            line = self.filter(line)
            if line:
                break
        return line

    def filter(self, line):
        """To skip a line return an empty string ('')
        Otherwise, return the line.
        """
        return line

class SourceLog(SourceBase):
    """A source log file on a remote host.
    """
    def __init__(self, host, filepath, encoding='utf-8'):
        self.host = host
        self.encoding = encoding
        self.cmd = 'tail --follow=name %s' % filepath

class MysqladminExtendedRelativeSource(SourceBase):
    """Get data from mysqladmin extended command (relative)
    """
    def __init__(self, host, encoding='utf-8'):
        self.host = host
        self.encoding = encoding
        self.cmd = 'mysqladmin extended -i10 -r'

    def filter(self, line):
        if   ('Questions' in line or
              'Slow_queries' in line
              ):
            return line
        else:
            return ''

class MysqladminExtendedAbsoluteSource(SourceBase):
    """Get data from mysqladmin extended command (absolute)
    """
    def __init__(self, host, encoding='utf-8'):
        self.host = host
        self.encoding = encoding
        self.cmd = 'mysqladmin extended'

    def filter(self, line):
        if   ('Slave_running' in line or
              'Threads_connected' in line or
              'Threads_running' in line
              ):
            return line
        else:
            return ''

class VmstatSource(SourceBase):
    """Get data from vmstat
    """
    def __init__(self, host, encoding='utf-8'):
        self.host = host
        self.encoding = encoding
        self.cmd = 'vmstat 5'

    def filter(self, line):
        if   (line.startswith('procs') or
              line.startswith(' r')
              ):
            return ''
        else:
            return line

class DfSource(SourceBase):
    """Get data from "df"
    """
    def __init__(self, host, filepath, encoding='utf-8'):
        self.host = host
        self.encoding = encoding
        self.cmd = 'while [ 1 ]; do df %s; sleep 60; done' % filepath

    def filter(self, line):
        if line.startswith('Filesystem'):
            return ''
        else:
            return line
