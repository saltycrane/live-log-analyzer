from subprocess import Popen, PIPE, STDOUT
from util import smart_str

class SourceBase(object):
    """Subclasses should implement "start_stream()" and optionally "filter()"
    "start_stream()" should set "self.stream" to be a file-like object with
    a "readline()" method.
    """
    def get_line(self):
        while True:
            line = self.stream.readline()
            line = smart_str(line)
            line = self.filter(line)
            if line:
                break
        return line

    def filter(self, line):
        """To skip a line return something that evaluates to False.
        Otherwise, return the line.
        """
        return line

class SourceLog(SourceBase):
    """A source log file on a remote host.
    """
    def __init__(self, host, filepath):
        self.host = host
        self.filepath = filepath

    def start_stream(self):
        """Tail -f the remote file.
        Return a file object of the stdout+stderr.
        """
        cmd = 'ssh %s tail --follow=name %s' % (self.host, self.filepath)
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
        self.stream = p.stdout

class MysqladminExtendedRelativeSource(SourceBase):
    """Get data from mysqladmin extended command (relative)
    """
    def __init__(self, host):
        self.host = host

    def start_stream(self):
        mysql_command = "mysqladmin extended -i10 -r"
        cmd = 'ssh %s "%s" ' % (self.host, mysql_command)
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
        self.stream = p.stdout

    def filter(self, line):
        if   ('Questions' in line or
              'Slow_queries' in line
              ):
            return line
        else:
            return None

class MysqladminExtendedAbsoluteSource(SourceBase):
    """Get data from mysqladmin extended command (absolute)
    """
    def __init__(self, host):
        self.host = host

    def start_stream(self):
        mysql_command = "mysqladmin extended"
        cmd = 'ssh %s "%s" ' % (self.host, mysql_command)
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
        self.stream = p.stdout

    def filter(self, line):
        if   ('Slave_running' in line or
              'Threads_connected' in line or
              'Threads_running' in line
              ):
            return line
        else:
            return None
