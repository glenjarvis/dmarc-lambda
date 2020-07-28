# dmarc.lambda
AWS Lambda Application that receives, parses and processes DMARC summary reports

Spam email has been a problem since the mid-nineties. There have been technological advances that let the owner of a domain (e.g., `google.com` or `scs.lbl.gov` or `glenjarvis.com`) absolutely control if an email from that domain really belongs to them:

- https://en.wikipedia.org/wiki/Sender_Policy_Framework
- https://en.wikipedia.org/wiki/DomainKeys_Identified_Mail

Even more recently, however, is the technological advance that ties both `Sender Policy Framework` (`SPF`) and `DomainKeys Identified Mail` (`DKIM`) linked above into a system that can also set policies. That means that if I, as the owner of `glenjarvis.com`, want to say "reject all mail that isn't sent from this `SPF` address with these keys," I can do so. 

I can also specify where to send reports when the bad actors pretend to be from `glenjarvis.com` but really aren't. This technology is called `Domain-based Message Authentication, Reporting and Conformance` (`DMARC`):

- https://en.wikipedia.org/wiki/DMARC

This OpenSource project is a framework that collects those reports, parses them, and stores them in a way where one can query and make meaningful reports.

The specific technology used in this project uses `Amazon Web Services` (AWS) heavily in a serverless stack. These are the services that are used:

1. Reports are sent from email agents (`google.com`, `yahoo.com`, `aol.com`, etc.) via email. The AWS service that receives email is `Simple Email Service` (`SES`)
1. Contents of these emails are stored in an AWS service called `Simple Storage Service` (`S3`).
1. Code is needed to parse that email and extract the attached file. This code runs serverless in an AWS `Lambda` service. Once the attachment is parsed from the email (that is still stored in `S3`), the attachment will be also be stored in *another* `S3` location. Lambda log output will be stored in the AWS CloudWatch service.
1. Code is needed to parse the previously attached `DMARC` compressed reports (`xml` compressed as either `zip` or `gz`). This will also run as a serverless `Lambda`.
1. Finally, the parsed data needs stored. The simplest place to store this data is in the AWS service called `DynamoDB`. One can convert that data to a Relational Database format of their choice.
1. Meaningful reports from the previously collected data can then be generated

# Easy to Contribute to this OpenSource Project

You may think "I don't even know what this project does" even after reading its summary description above. That is reasonable because:

1. You may not be familiar with the subject matter (How Email works, `DNS`, `SPF`, `DKIM` and `DMARC`), and/or
2. You may not be familiar with the technological components (`Route53`, `SES`, `S3`, `Lambda` and `CloudWatch`).

However, I guarantee, you can easily contribute to this project at this stage. The tasks that need completed are broken down in into very discrete and simple tasks:

1. Task 1 ("readme_polishing"): Documentation is important. Typos add confusion. Read this README.md and other files that it refers to. Are the instructions easy to understand? Are there typos? You can make a PR to fix them directly yourself.

1. Task 2 ("extract_attachment"): Given the `tcq88aasf2uj5r4dknkpmp641bloic79f8399ag1` raw email file, extract the zip attachment from the file. Instructions are included at `dmarc.lambda/task2_extract_attachment/README.md`.

1. Task 3 ("parse_filenames"): Parse a filename into four variables of the correct type. Detailed instructions are included at `dmarc.lambda/task3_parse_filenames/README.md`.

1. Task 4 ("parse_file_contents"): Given compressed XML files, parse the files for relevant information. Instructions are included at `dmarc.lambda/task4_parse_file_contents/README.md`.

# Project Guidelines

In this initial build phase of the project, the above four listed tasks will not be connected. However, we should all still follow the same project guidelines.

1. All code submitted should be PEP8 (and the new style PEP) compliant. This is very simple to validate with https://pypi.python.org/pypi/pep8.
1. All code submitted should pass PyLint (https://pypi.python.org/pypi/pylint) with default settings with 100% rating. This means there will be times that PyLint needs to be disabled with inline comments such as `# pylint: disable=multiple-statements`
1. Functions and methods should be as short as possible, breaking concepts into smaller functions/methods within the same file.
1. Git messages should written in the imperative: https://chris.beams.io/posts/git-commit/
1. Use GitFlow when making your pull request: http://nvie.com/posts/a-successful-git-branching-model/
1. Because this will eventually run as small "functions in the cloud" as an AWS `Lambda`:
    - Each component should be within a single file if possible
    - We should limit dependencies to external libraries as much as possible.
1. This will run in a Python3 `Lambda`. Python2 compatibility is not necessary.

## Copyright
Copyright 2017 Glen Jarvis, LLC

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this repository except in compliance with the License.  You may obtain a copy of the
License at

https://github.com/glenjarvis/dmarc.lambda/blob/main/LICENSE

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied.  See the License for the
specific language governing permissions and limitations under the License.

