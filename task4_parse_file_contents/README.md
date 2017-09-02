The two sample files in this directory (dmarc.lambda/task4_parse_file_contents)
are both examples of DMARC "reports" that are sent from vendors. There are two
different types of compression (`zip` and `gz`) used. Both are represented by
these real examples.

If uncompressed, these files would both be an XML file of a particular format.

To complete this task, both files should be read and parsed row contents output
(via STDOUT is sufficient).

This will eventually run in an AWS `Lambda` so should have the least number of
external library dependencies as possible (Julien appears to also have taken
that approach). All files for this task should be limited to this directory.

I have made a trial version of this to help clarify specification. The filename
is dmarc.lambda/task4_parse_file_contents/parse.py.

This trail version has been run against a much larger data set to find and
handle real life data problems. This produces the data that we are looking for:

```
filename        report_id       org_name        human_date      begin_epoch_sec end_epoch_sec   source_ip       disposition     DKIM    SPF
comcast.net!glenjarvis.com!1503792000!1503878400.xml    v1-1503901485-glenjarvis.com    comcast.net     2017-08-27      1503792000      1503878400      185.70.40.22    none    pass    pass
google.com!glenjarvis.com!1501372800!1501459199.xml     5713213590119692620     google.com      2017-07-30      1501372800      1501459199      185.70.40.22    none    pass    pass
```

However, there are several weaknesses (including the fact that this code isn't
yet to the standards specified in the top level README). Most importantly,
however, there is a conflict that we must address.

I wish to use the least number of external libraries as possible. I wish to
especially avoid external libraries that are not pure python. However, the
approach listed above has security vulnarabilities (especially quadratic blowup
and billion laughs):

https://docs.python.org/3/library/xml.html#xml-vulnerabilities

This data is retrieved from an outside source that could be compromised.

Consider this problem a specification program more than a product.
