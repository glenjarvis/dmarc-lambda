The sample file in this directory (dmarc.lambda/task3_parse_filenames) is the
type of file that is attached to DMARC emails.

The filename of the file (`google.com!glenjarvis.com!1501372800!1501459199.zip`)
contains four valuable pieces of information:

1. The first field in this filename is the name of the email service provider
   (in this example `google.com`) that received at least one email and applied the
   DMARC policies against it.

2. The second field in this filename is the name of the domain for which the
   DMARC policy was applied (in this example `glenjarvis.com`).

3. The third field in this filename is a Date/Time value represented as an
   integer (number of seconds since Epoch). In this example, this would be
   equivalent to the naive datetime "Sunday, July 30, 2017 00:00:00 AM". This
   represents the beginning date/time of the interval for which the report is
   valid.

4. The fourth and final field in this filename is another Date/Time value
   represented as described above.  In this example, this would be equivalent
   to the naive datetime "Sunday, July 30, 2017 04:59:59 PM". This represents
   the beginning date/time of the interval for which the report is valid.


This task should be a simple function. This skeleton should help describe what
is intended/needed:

```
def details_from_filename(dmarc_filename:str):
    ....
    email_provider = "google.com"  # type: str
    domain = "glenjarvis.com"  # type: str
    begin_time = datetime.datetime(2017, 7, 30, 0, 0, 0)  # type: datetime.datetime
    end_time = datetime.datetime(2017, 7, 30, 16, 59, 59)  # type: datetime.datetime

    return [email_provider, domain, begin_time, end_time]
```


Place keep all files in this directory (dmarc.lambda/task3_parse_filenames)
including any *awesome* pyunit tests you may want to include.
