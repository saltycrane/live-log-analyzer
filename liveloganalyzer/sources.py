from subprocess import Popen, PIPE, STDOUT

class SourceLog(object):
    """A source log file on a remote host.
    """
    def __init__(self, host, filepath):
        self.host = host
        self.filepath = filepath

    def get_stream(self):
        """Tail -f the remote file.
        Return a file object of the stdout+stderr.
        """
        cmd = 'ssh -f %s tail --follow=name %s' % (self.host, self.filepath)
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
        return p.stdout
