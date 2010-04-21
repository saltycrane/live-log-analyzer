import re
from datetime import datetime
from pprint import pprint

class BaseParser(object):
    """Base class not to be used directly.
    """
    pattern = None
    date_format = None
    date_ignore_pattern = None

    @classmethod
    def parse_line(cls, line):
        """Parse one line of the log file.
        """
        regex = re.compile(cls.pattern)
        m = regex.search(line)
        if m:
            data = m.groupdict()
            data = cls.post_process(data)
            if cls.date_format:
                data['time'] = cls.convert_time(data['time'])
            else:
                data['time'] = datetime.now()
            return data
        else:
            return {}

    @classmethod
    def convert_time(cls, time_str):
        """Convert date string to datetime object
        """
        if cls.date_ignore_pattern:
            time_str = re.sub(cls.date_ignore_pattern, '', time_str)
        return datetime.strptime(time_str, cls.date_format)

    @classmethod
    def post_process(cls, data):
        """Implement this in the subclass. Accept/return parsed data structure.
        """
        return data

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
                     'Backend: $mybackend '
                     ;
    """
    date_format = "%d/%b/%Y:%H:%M:%S"
    date_ignore_pattern = r' -\d{4}'
    pattern = ' '.join([
            r'\*\*\*(?P<time>\S+ -\d{4})',
            r'\[(?P<ip>[\d\.]+)\]',
            r'(?P<status>HIT|MISS|EXPIRED|UPDATING|STALE|-)',
            r'ups_ad: (?P<ups_ad>.*)',
            r'ups_st: (?P<ups_st>.*)',
            r'ups_rt: (?P<ups_rt>.*)',
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
            r'Backend: (?P<backend>.*)',
            ])

    @classmethod
    def post_process(cls, data):
        """Convert request string into http method and url
        """
        request_string = data['request']
        request_pattern = r'(?P<http_method>GET|HEAD|POST) (?P<url>\S+)'
        m = re.search(request_pattern, request_string)
        if m:
            newdata = m.groupdict()
            data.update(newdata)
        return data

class NginxErrorParser(BaseParser):
    date_format = "%Y/%m/%d %H:%M:%S"
    pattern = ' '.join([
            r'^(?P<time>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})',
            r'\[(?P<level>.*)\]',
            ])

class PhpErrorParser(BaseParser):
    date_format = "%d-%b-%Y %H:%M:%S"
    pattern = ' '.join([
            r'^\[(?P<time>.*)\]',
            r'(?P<therest>.*)',
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

class SyslogParser(BaseParser):
    date_format = "%Y %b %d %H:%M:%S"
    pattern = ' '.join([
            r'(?P<time>\S+ \d\d \d\d\:\d\d\:\d\d)',
            r'(?P<hostname>\S+)',
            r'(?P<process>\S+):',
            r'(?P<therest>.*)',
            ])

    @classmethod
    def post_process(cls, data):
        data['time'] = '%d %s' % (datetime.now().year, data['time'])
        return data

class MysqladminExtendedRelativeParser(BaseParser):
    """For use with MysqladminExtendedRelativeSource
    Assumes -i parameter is 10
    Return data in counts per second
    """
    pattern = ' '.join([
            r'(',
            r'.*Questions\s*\|\s*(?P<questions_persecond>\d+).*',
            r'|',
            r'.*Slow_queries\s*\|\s*(?P<slow_queries_persecond>\d+).*',
            r')',
            ])

    @classmethod
    def post_process(cls, data):
        """Divide counts by uptime to get counts per second
        """
        # TODO: don't hardcode UPTIME to 10.0
        # This parameter is tied to the -i parameter in MysqladminExtendedRelativeSource
        # Maybe need to combine "sources" and "parsers" classes
        UPTIME = 10.0
        data = dict([(k, v) for k, v in data.iteritems() if v])
        return dict([
                (k, int(v)/UPTIME)
                for k, v in data.iteritems()
                if '_persecond' in k
                ])

class MysqladminExtendedAbsoluteParser(BaseParser):
    """For use with MysqladminExtendedAbsoluteSource
    """
    pattern = ' '.join([
            r'(',
            r'.*Slave_running\s*\|\s*(?P<slave_running>\S+).*',
            r'|',
            r'.*Threads_connected\s*\|\s*(?P<threads_connected>\d+).*',
            r'|',
            r'.*Threads_running\s*\|\s*(?P<threads_running>\d+).*',
            r')',
            ])

    @classmethod
    def post_process(cls, data):
        """Remove empty values
        """
        return dict([(k, v) for k, v in data.iteritems() if v])

class VmstatParser(BaseParser):
    """Parses vmstat output
    """
    pattern = r'\s+'.join([
            r'(?P<r>\d+)',
            r'(?P<b>\d+)',
            r'(?P<swpd>\d+)',
            r'(?P<free>\d+)',
            r'(?P<buff>\d+)',
            r'(?P<cache>\d+)',
            r'(?P<si>\d+)',
            r'(?P<so>\d+)',
            r'(?P<bi>\d+)',
            r'(?P<bo>\d+)',
            r'(?P<in>\d+)',
            r'(?P<cs>\d+)',
            r'(?P<us>\d+)',
            r'(?P<sy>\d+)',
            r'(?P<id>\d+)',
            r'(?P<wa>\d+)',
            ])

class DfParser(BaseParser):
    """Parses df output
    """
    pattern = r'\s+'.join([
            r'(?P<df_filesystem>\S+)',
            r'(?P<df_blocks>\d+)',
            r'(?P<df_used>\d+)',
            r'(?P<df_available>\d+)',
            r'(?P<df_use_percent>\S+)',
            r'(?P<df_mounted_on>\S+)',
            ])

    @classmethod
    def post_process(cls, data):
        """Removed the percent character from df_use_percent
        """
        def remove_percent(k, v):
            if k == 'df_use_percent':
                v = v.rstrip('%')
            return (k, v)
        return dict([remove_percent(k, v) for k, v in data.iteritems()])
