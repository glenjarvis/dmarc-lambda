The sample file (`tcq88aasf2uj5r4dknkpmp641bloic79f8399ag1`) in this directory
(`dmarc.lambda/task2_extract_attachment`) is the type of file that is created
when an email is delievered through AWS `Simple Email Service` (`SES`) and
stored in a `Simple Storage Service` (`S3`) bucket.

Within this email file is an attachment. In this case:
`google.com!glenjarvis.com!1501372800!1501459199.zip`.

This task is to use the built-in Python email library
(https://docs.python.org/3/library/email.html) to extract the file from the raw email.

This needs to run inside of AWS `Lambda`, so I do not wish to use any external
libraries. The code for this task should be contained within a single Python
file.

Please keep all code samples and tests within this directory
(`dmarc.lambda/task2_extract_attachment`).
