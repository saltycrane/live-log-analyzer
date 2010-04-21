import time
from subprocess import Popen, PIPE, STDOUT
from pytz import timezone

def backtick(cmd):
    """Like Perl's backtick. Run a shell command and return the output as a string.
    """
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
    return p.stdout.read()

def transpose_list_of_lists(lol):
    return [list(newinner) for newinner in map(None, *lol)]

def convert_time_for_flot(dt_obj):
    """Given datetime object, return a timestamp required for the jquery flot library
    """
    dt_obj_utc_fake = dt_obj.replace(tzinfo=timezone('UTC'))
    dt_obj_pacific_fake = dt_obj_utc_fake.astimezone(timezone('US/Pacific'))
    timestamp = 1000.0 * time.mktime(dt_obj_pacific_fake.timetuple())
    return timestamp

def safe_divide(dividend, divisor, dbz=0):
    if divisor == 0:
        return dbz
    else:
        return dividend/divisor

def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Modified from http://code.djangoproject.com/browser/django/tags/releases/1.1.1/django/utils/encoding.py

    Returns a bytestring version of 's', encoded as specified in 'encoding'.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s
    elif not isinstance(s, basestring):
        try:
            return str(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return ' '.join([smart_str(arg, encoding, strings_only,
                        errors) for arg in s])
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s

def force_unicode(s, encoding='utf-8', errors='strict'):
    """
    Modified from http://code.djangoproject.com/browser/django/tags/releases/1.1.1/django/utils/encoding.py
    """
    if not isinstance(s, basestring,):
        if hasattr(s, '__unicode__'):
            s = unicode(s)
        else:
            try:
                s = unicode(str(s), encoding, errors)
            except UnicodeEncodeError:
                if not isinstance(s, Exception):
                    raise
                # If we get to here, the caller has passed in an Exception
                # subclass populated with non-ASCII data without special
                # handling to display as a string. We need to handle this
                # without raising a further exception. We do an
                # approximation to what the Exception's standard str()
                # output should be.
                s = ' '.join([force_unicode(arg, encoding, strings_only,
                        errors) for arg in s])
    elif not isinstance(s, unicode):
        # Note: We use .decode() here, instead of unicode(s, encoding,
        # errors), so that if s is a SafeString, it ends up being a
        # SafeUnicode at the end.
        s = s.decode(encoding, errors)
