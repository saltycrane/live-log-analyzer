import re
from datetime import datetime

class BaseParser(object):
    """Base class not to be used directly.
    """
    pattern = None
    date_format = None
    date_ignore_pattern = None
    request_pattern = None

    @classmethod
    def parse_line(cls, line):
        """Parse one line of the log file.
        """
        regex = re.compile(cls.pattern)
        m = regex.search(line)
        if m:
            data = m.groupdict()
            if cls.request_pattern:
                newdata = cls.parse_request_field(data['request'])
                data.update(newdata)
            if cls.date_format:
                data['time'] = cls.convert_time(data['time'])
            return data
        else:
            return {}

    @classmethod
    def convert_time(cls, time_str):
        """Convert date string to datetime object
        """
        time_str = re.sub(cls.date_ignore_pattern, '', time_str)
        return datetime.strptime(time_str, cls.date_format)

    @classmethod
    def parse_request_field(cls, req_str):
        """Convert request string into http method and url
        """
        m = re.search(cls.request_pattern, req_str)
        if m:
            return m.groupdict()
        else:
            return {}

class NginxCacheParser(BaseParser):
    """Used to parse the following Nginx log format:

    log_format cache '***$time_local '
                     '[$remote_addr] '
                     '$upstream_cache_status '
                     'ups_ad: $upstream_addr '
                     'ups_st: $upstream_status '
                     'ups_rt: $upstream_response_time '
                     'Cache-Control: $upstream_http_cache_control '
                     'Expires: $upstream_http_expires '
                     '$host '
                     '"$request" ($status) '
                     '"$http_user_agent" '
                     'Args: $args '
                     'Media: $media_flag '
                     'Comment author email: $comment_author_email '
                     'Comment author: $comment_author '
                     'Wordpress logged in: $wordpress_logged_in '
                     ;
    """
    date_format = "%d/%b/%Y:%H:%M:%S"
    date_ignore_pattern = r' -\d{4}'
    request_pattern = r'(?P<http_method>GET|HEAD|POST) (?P<url>\S+)'
    pattern = ' '.join([
            r'\*\*\*(?P<time>\S+ -\d{4})',
            r'\[(?P<ip>[\d\.]+)\]',
            r'(?P<status>HIT|MISS|EXPIRED|UPDATING|STALE|-)',
            r'ups_ad: (?P<ups_ad>\S+)',
            r'ups_st: (?P<ups_st>\S+)',
            r'ups_rt: (?P<ups_rt>\S+)',
            r'Cache-Control: (?P<cc_header>.+)',
            r'Expires: (?P<exp_header>.+)',
            r'(?P<domain>\S+)',
            r'\"(?P<request>.*)\"',
            r'\((?P<http_status>\d{3})\)',
            r'\"(?P<agent>.*)\"',
            r'Args: (?P<args>.*)',
            r'Media: (?P<media>.*)',
            r'Comment author email: (?P<com_email>.*)',
            r'Comment author: (?P<com_author>.*)',
            r'Wordpress logged in: (?P<wp_login>.*)',
            ])

class NginxErrorParser(BaseParser):
    date_format = "%Y/%m/%d %H:%M:%S"
    pattern = ''.join([
            r'^(?P<time>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) ',
            ])

class ApacheAccessParser(BaseParser):
    date_format = "%d/%b/%Y:%H:%M:%S"
    date_ignore_pattern = r' -\d{4}'
    pattern = ''.join([
            r'^',
            r'(?P<ip>(?:\d+\.){3}\d+) ',
            r'.* ',
            r'.* ',
            r'\[(?P<time>\d+/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} -\d{4})\] ',
            ])
