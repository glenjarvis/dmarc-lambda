import unittest

from file_extraction import *


class EqualAssertion:

    def __init__(self, test_case, value):
        self._test_case = test_case
        self._value = value

    def __call__(self, value):
        self._test_case.assertEqual(self._value, value)


class IntegrationTests(unittest.TestCase):

    def test_gzip_archive_extraction_consumer(self):
        system_under_test = GzipArchiveExtractionConsumer(
            EqualAssertion(
                self,
                './dist/google.com!glenjarvis.com!1501372800!1501459199.xml'
            ),
            './dist'
        )

        system_under_test('./google.com!glenjarvis.com!1501372800!1501459199.xml.gz')
