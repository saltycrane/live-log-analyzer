import time
from subprocess import Popen, PIPE, STDOUT
from debuglogging import error

class SourceBase(object):
    """Subclasses should define instance attributes self.sshparams, self.cmd, self.encoding
    and optionally the instance method self.filter()
    self.sshparams is a dict containing the parameters to pass to the ssh command.
    At a minimum, it should define self.sshparams['hostname']. It may also define
    other ssh options such as 'host', 'user' or 'identityfile'. Option names are
    the same as those used in the ssh config file, except in lowercase. For more
    information see the man page for ssh_config. The 'host' option is used as a
    nickname. If 'host' is not specified, the value for 'hostname' is assigned
    to 'host'.

    Example self.sshparams:

    {'host': 'us-ng1',
     'hostname': '111.111.111.15',
     'identityfile': '/home/saltycrane/sshkeys/myprivatekey',
     'user': 'myusername',
     }
    """
    def start_stream(self):
        if 'host' not in self.sshparams:
            self.sshparams['host'] = self.sshparams['hostname']
        ssh_options = '-o' + ' -o'.join(['='.join([k, v])
                                         for k, v in self.sshparams.iteritems()
                                         if k != 'hostname' and k != 'host'])
        ssh_cmd = ' '.join(['ssh',
                            ssh_options,
                            self.sshparams['hostname'],
                            '"%s"' %  self.cmd,
                            ])
        self.p = Popen(ssh_cmd, shell=True, stdout=PIPE, stderr=STDOUT)

    def get_line(self):
        while True:
            line = self.p.stdout.readline()
            if line == '' and self.p.poll() != None:
                raise Exception('Child process exited for host %s: %s' % (
                        self.sshparams['host'], self.cmd))
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
    def __init__(self, sshparams, filepath, encoding='utf-8'):
        self.sshparams = sshparams
        self.encoding = encoding
        self.cmd = 'tail --follow=name %s' % filepath

class MysqladminExtendedRelativeSource(SourceBase):
    """Get data from mysqladmin extended command (relative)
    """
    def __init__(self, sshparams, encoding='utf-8'):
        self.sshparams = sshparams
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
    def __init__(self, sshparams, encoding='utf-8'):
        self.sshparams = sshparams
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
    def __init__(self, sshparams, encoding='utf-8'):
        self.sshparams = sshparams
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
    def __init__(self, sshparams, filepath, encoding='utf-8'):
        self.sshparams = sshparams
        self.encoding = encoding
        self.cmd = 'while [ 1 ]; do df %s; sleep 60; done' % filepath

    def filter(self, line):
        if line.startswith('Filesystem'):
            return ''
        else:
            return line
