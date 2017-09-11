import unittest
import os
import filecmp

from file_extraction import *


def return_true(x):
    return True


def return_false(x):
    return False


class EqualAssertion:

    def __init__(self, test_case, value):
        self._test_case = test_case
        self._value = value

    def __call__(self, value):
        self._test_case.assertEqual(self._value, value)


class PathOfControlFailure:

    def __init__(self, test_case):
        self._test_case = test_case

    def __call__(self, value):
        self._test_case.assertTrue(False)


class DoSomethingIfCalledConsumer:

    def __init__(self, something):
        self._something = something

    def __call__(self, value):
        self._something(value)


class UnitTests(unittest.TestCase):

    def test_path_selection_consumer_none_match(self):

        def raise_error(value):
            raise AssertionError

        exploding_consumer = DoSomethingIfCalledConsumer(
            raise_error
        )
        attributes_1 = ConsumerSelectionAttributes(
            predicate=return_false,
            consumer=exploding_consumer
        )
        attributes_2 = ConsumerSelectionAttributes(
            predicate=return_false,
            consumer=exploding_consumer
        )
        attributes_3 = ConsumerSelectionAttributes(
            predicate=return_false,
            consumer=exploding_consumer
        )
        system_under_test = PathSelectionConsumer(
            [attributes_1, attributes_2, attributes_3],
            EqualAssertion(self, 1)
        )
        system_under_test(1)

    def test_path_selection_consumer_first_matches(self):

        def raise_error(value):
            raise AssertionError

        def succeed(value):
            self.assertTrue(True)

        exploding_consumer = DoSomethingIfCalledConsumer(
            raise_error
        )
        succeeding_consumer = DoSomethingIfCalledConsumer(
            succeed
        )
        attributes_1 = ConsumerSelectionAttributes(
            predicate=return_true,
            consumer=succeeding_consumer
        )
        attributes_2 = ConsumerSelectionAttributes(
            predicate=return_false,
            consumer=exploding_consumer
        )
        attributes_3 = ConsumerSelectionAttributes(
            predicate=return_false,
            consumer=exploding_consumer
        )
        system_under_test = PathSelectionConsumer(
            [attributes_1, attributes_2, attributes_3],
            PathOfControlFailure(self)
        )
        system_under_test(2)

    def test_path_selection_consumer_last_matches(self):

        def raise_error(value):
            raise AssertionError

        def succeed(value):
            self.assertTrue(True)

        exploding_consumer = DoSomethingIfCalledConsumer(
            raise_error
        )
        succeeding_consumer = DoSomethingIfCalledConsumer(
            succeed
        )
        attributes_1 = ConsumerSelectionAttributes(
            predicate=return_false,
            consumer=exploding_consumer
        )
        attributes_2 = ConsumerSelectionAttributes(
            predicate=return_false,
            consumer=exploding_consumer
        )
        attributes_3 = ConsumerSelectionAttributes(
            predicate=return_true,
            consumer=succeeding_consumer
        )
        system_under_test = PathSelectionConsumer(
            [attributes_1, attributes_2, attributes_3],
            PathOfControlFailure(self)
        )
        system_under_test(3)


class IntegrationTests(unittest.TestCase):

    def clean_up(self):
        try:
            os.remove('./dist/google.com!glenjarvis.com!1501372800!1501459199.xml')
        except FileNotFoundError:
            pass

        try:
            os.remove('./dist/google.com!glenjarvis.com!1501372800!1501459199.xml.gz')
        except FileNotFoundError:
            pass

        try:
            os.remove('./dist/google.com!glenjarvis.com!1501372800!1501459199.zip')
        except FileNotFoundError:
            pass

    def setUp(self):
        self.clean_up()

    def tearDown(self):
        self.clean_up()

    def test_gzip_archive_extraction_consumer(self):
        system_under_test = GzipArchiveExtractionConsumer(
            EqualAssertion(
                self,
                './dist/google.com!glenjarvis.com!1501372800!1501459199.xml'
            ),
            './dist'
        )

        self.assertFalse(
            os.path.isfile(
                './dist/google.com!glenjarvis.com!1501372800!1501459199.xml'
            )
        )

        system_under_test('./google.com!glenjarvis.com!1501372800!1501459199.xml.gz')

        self.assertTrue(
            os.path.isfile(
                './dist/google.com!glenjarvis.com!1501372800!1501459199.xml'
            )
        )

        self.assertTrue(
            filecmp.cmp(
                './google.com!glenjarvis.com!1501372800!1501459199.xml',
                './dist/google.com!glenjarvis.com!1501372800!1501459199.xml',
                shallow=False
            )
        )

    def test_api(self):

        self.assertFalse(
            os.path.isfile(
                './dist/google.com!glenjarvis.com!1501372800!1501459199.xml'
            )
        )

        extract_files(
            './tcq88aasf2uj5r4dknkpmp641bloic79f8399ag1',
            './dist'
        )

        self.assertTrue(
            os.path.isfile(
                './dist/google.com!glenjarvis.com!1501372800!1501459199.xml'
            )
        )

        self.assertTrue(
            filecmp.cmp(
                './google.com!glenjarvis.com!1501372800!1501459199.xml',
                './dist/google.com!glenjarvis.com!1501372800!1501459199.xml',
                shallow=False
            )
        )
