The two sample files in this directory (dmarc.lambda/task4_parse_file_contents)
are both examples of DMARC "reports" that are sent from vendors. There are two
different types of compression (`zip` and `gz`) used. Both are represented by
these real examples.

If uncompressed, these files would both be an XML file of a particular format.

This task has already been tackled (possibly successfully) by Julien Vehent:
https://github.com/jvehent/dmarc-parser/blob/master/dmarc-parser.py

To complete this task, both files should be read and parsed row contents output
(via STDOUT is sufficient).

This will eventually run in an AWS `Lambda` so should have the least number of
external library dependencies as possible (Julien appears to also have taken
that approach). All files for this task should be limited to this directory.

Julien's repository does not specify a License, however. So, one could write it
(without copying or pasting) from scratch in a "clean room" and the Apache 2.0
license for this project would apply.

All work should be constrained to this (dmarc.lambda/task4_parse_file_contents)
directory.
