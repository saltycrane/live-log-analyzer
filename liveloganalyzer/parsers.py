import re
from datetime import datetime

class BaseParser(object):
    """Base class not to be used directly.
    """
    def __init__(self):
        self.pattern = None
        self.date_format = None
        self.date_ignore_pattern = None
        self.request_pattern = None

    def parse_line(self, line):
        """Parse one line of the log file.
        """
        regex = re.compile(self.pattern)
        m = regex.search(line)
        if m:
            data = m.groupdict()
            if self.request_pattern:
                newdata = self.parse_request_field(data['request'])
                data.update(newdata)
            if self.date_format:
                data['time'] = self.convert_time(data['time'])
            return data
        else:
            return {}

    def subtract_times(self, time1, time2):
        """Subtract time1 - time2. time1 should be later than time2.
        Return delta time in seconds.
        """
        td = self.convert_time(time1) - self.convert_time(time2)
        seconds = 86400*td.days + td.seconds
        return seconds

    def convert_time(self, time_str):
        """Convert date string to datetime object
        """
        time_str = re.sub(self.date_ignore_pattern, '', time_str)
        return datetime.strptime(time_str, self.date_format)

    def parse_request_field(self, req_str):
        """Convert request string into http method and url
        """
        m = re.search(self.request_pattern, req_str)
        if m:
            return m.groupdict()
        else:
            return {}

class NginxCacheParser(BaseParser):
    def __init__(self):
        self.date_format = "%d/%b/%Y:%H:%M:%S"
        self.date_ignore_pattern = r' -\d{4}'
        self.request_pattern = r'(?P<http_method>GET|HEAD|POST) (?P<url>\S+)'
        self.pattern = ' '.join([
                r'\*\*\*(?P<time>\S+ -\d{4})',
                r'\[(?P<ip>[\d\.]+)\]',
                r'(?P<status>HIT|MISS|EXPIRED|UPDATING|STALE|-)',
                r'ups_ad: (?P<ups_ad>\S+)',
                r'ups_st: (?P<ups_st>\S+)',
                r'ups_rt: (?P<ups_rt>\S+)',
                r'Cache-Control: (?P<cc_header>.+)',
                r'Expires: (?P<exp_header>.+)',
                r'(?P<domain>\S+)',
                r'\"(?P<request>.+)\"',
                r'\((?P<http_status>\d{3})\)',
                r'\"(?P<agent>.*)\"',
                r'Args: (?P<args>.*)',
                r'Media: (?P<media>.*)',
                r'Comment author email: (?P<com_email>.*)',
                r'Comment author: (?P<com_author>.*)',
                r'Wordpress logged in: (?P<wp_login>.*)',
                ])

class NginxErrorParser(BaseParser):
    def __init__(self):
        self.date_format = "%Y/%m/%d %H:%M:%S"
        self.pattern = ''.join([
                r'^(?P<time>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) ',
                ])

class ApacheAccessParser(BaseParser):
    def __init__(self):
        self.date_format = "%d/%b/%Y:%H:%M:%S"
        self.date_ignore_pattern = r' -\d{4}'
        self.pattern = ''.join([
                r'^',
                r'(?P<ip>(?:\d+\.){3}\d+) ',
                r'.* ',
                r'.* ',
                r'\[(?P<time>\d+/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} -\d{4})\] ',
                ])
