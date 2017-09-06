import datetime
import re


def details_from_filename(dmarc_filename):
    """
    splits filename input on the ! character into 4 fields

    dmarc_filename: str

    returns:
    email_provider: str
    domain:         str
    begin_time:     datetime.datetime
    end_time:     datetime.datetime
    """
    tz = datetime.timezone(datetime.timedelta(0))
    dfne = re.sub(r'\.\w+$', '', dmarc_filename)
    fields = dfne.split('!')
    email_provider = fields[0]
    domain = fields[1]
    begin_time = datetime.datetime.fromtimestamp(float(fields[2]), tz)
    end_time = datetime.datetime.fromtimestamp(float(fields[3]), tz)

    return [email_provider, domain, begin_time, end_time]
