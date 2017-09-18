"""unit-tests and integration-tests"""

import unittest
import os
import filecmp

import file_extraction


# pylint: disable=unused-argument
# pylint: disable=too-few-public-methods
def return_true(value):

    """Sample predicate for unit-tests"""

    return True


def return_false(value):

    """Sample predicate for unit-tests"""

    return False


def raise_error(value):

    """Sample behavior (procedure) for unit-tests"""

    raise AssertionError


class Success:

    """Sample behavior (procedure) for unit-tests"""

    def __init__(self, test_case):
        self._test_case = test_case

    def __call__(self, value):

        """This procedure indicates success when called."""

        self._test_case.assertTrue(True)


class EqualAssertion:

    """Test Consumer which verifies the value it is passed"""

    def __init__(self, test_case, value):
        self._test_case = test_case
        self._value = value

    def __call__(self, value):
        self._test_case.assertEqual(self._value, value)


class PathOfControlFailure:

    """This policy function generates a test error.

    Such a function is useful for verifying that control did
    not pass through this point.
    """

    def __init__(self, test_case):
        self._test_case = test_case

    def __call__(self, value):
        self._test_case.assertTrue(False)


class DoSomethingIfCalledConsumer:

    """Mock consumer test support"""

    def __init__(self, something):
        self._something = something

    def __call__(self, value):
        self._something(value)


class PathSelectionConsumerUnitTests(unittest.TestCase):

    """Unit-tests for class PathSelectionConsumer"""

    def test_none_match(self):

        """Scenario: no predicate returns True

        (i) control does not pass to any downstream consumer
        (ii) the policy function is invoked
        """

        exploding_consumer = DoSomethingIfCalledConsumer(
            raise_error
        )
        attributes_1 = file_extraction.ConsumerSelectionAttributes(
            predicate=return_false,
            consumer=exploding_consumer
        )
        attributes_2 = file_extraction.ConsumerSelectionAttributes(
            predicate=return_false,
            consumer=exploding_consumer
        )
        attributes_3 = file_extraction.ConsumerSelectionAttributes(
            predicate=return_false,
            consumer=exploding_consumer
        )
        system_under_test = file_extraction.PathSelectionConsumer(
            [attributes_1, attributes_2, attributes_3],
            EqualAssertion(self, 1)
        )
        system_under_test(1)

    def test_first_matches(self):

        """Scenario: only the first predicate returns True

        (i) control passes only to the first downstream consumer
        (ii) the policy function is not invoked
        """

        exploding_consumer = DoSomethingIfCalledConsumer(
            raise_error
        )
        succeeding_consumer = DoSomethingIfCalledConsumer(
            Success(self)
        )
        attributes_1 = file_extraction.ConsumerSelectionAttributes(
            predicate=return_true,
            consumer=succeeding_consumer
        )
        attributes_2 = file_extraction.ConsumerSelectionAttributes(
            predicate=return_false,
            consumer=exploding_consumer
        )
        attributes_3 = file_extraction.ConsumerSelectionAttributes(
            predicate=return_false,
            consumer=exploding_consumer
        )
        system_under_test = file_extraction.PathSelectionConsumer(
            [attributes_1, attributes_2, attributes_3],
            PathOfControlFailure(self)
        )
        system_under_test(2)

    def test_last_matches(self):

        """Scenario: only the last predicate returns True

        (i) control passes only to the last downstream consumer
        (ii) the policy function is not invoked
        """

        exploding_consumer = DoSomethingIfCalledConsumer(
            raise_error
        )
        succeeding_consumer = DoSomethingIfCalledConsumer(
            Success(self)
        )
        attributes_1 = file_extraction.ConsumerSelectionAttributes(
            predicate=return_false,
            consumer=exploding_consumer
        )
        attributes_2 = file_extraction.ConsumerSelectionAttributes(
            predicate=return_false,
            consumer=exploding_consumer
        )
        attributes_3 = file_extraction.ConsumerSelectionAttributes(
            predicate=return_true,
            consumer=succeeding_consumer
        )
        system_under_test = file_extraction.PathSelectionConsumer(
            [attributes_1, attributes_2, attributes_3],
            PathOfControlFailure(self)
        )
        system_under_test(3)

    def test_control(self):

        """Scenario: all of the predicates return True

        (i) control passes only to the first downstream consumer
        (ii) the policy function is not invoked"""

        exploding_consumer = DoSomethingIfCalledConsumer(
            raise_error
        )
        succeeding_consumer = DoSomethingIfCalledConsumer(
            Success(self)
        )
        attributes_1 = file_extraction.ConsumerSelectionAttributes(
            predicate=return_true,
            consumer=succeeding_consumer
        )
        attributes_2 = file_extraction.ConsumerSelectionAttributes(
            predicate=return_true,
            consumer=exploding_consumer
        )
        attributes_3 = file_extraction.ConsumerSelectionAttributes(
            predicate=return_true,
            consumer=exploding_consumer
        )
        system_under_test = file_extraction.PathSelectionConsumer(
            [attributes_1, attributes_2, attributes_3],
            PathOfControlFailure(self)
        )
        system_under_test(4)


def integration_test_clean_up():

    """This function is used to keep the test directory clean"""

    try:
        os.remove(
            './test/google.com!glenjarvis.com!1501372800!1501459199.xml'
        )
    except FileNotFoundError:
        pass

    try:
        os.remove(
            './test/google.com!glenjarvis.com!1501372800!1501459199.xml.gz'
        )
    except FileNotFoundError:
        pass

    try:
        os.remove(
            './test/google.com!glenjarvis.com!1501372800!1501459199.zip'
        )
    except FileNotFoundError:
        pass


class GzipArchiveExtractionConsumerIntegrationTests(unittest.TestCase):

    """Integration-tests for class GzipArchiveExtractionConsumer"""

    def setUp(self):
        integration_test_clean_up()

    def tearDown(self):
        integration_test_clean_up()

    def test_file_generation(self):

        """Verifies file generation of GzipArchiveExtractionConsumer"""

        system_under_test = file_extraction.GzipArchiveExtractionConsumer(
            EqualAssertion(
                self,
                './test/google.com!glenjarvis.com!1501372800!1501459199.xml'
            ),
            './test'
        )

        self.assertFalse(
            os.path.isfile(
                './test/google.com!glenjarvis.com!1501372800!1501459199.xml'
            )
        )

        system_under_test(
            './google.com!glenjarvis.com!1501372800!1501459199.xml.gz'
        )

        self.assertTrue(
            os.path.isfile(
                './test/google.com!glenjarvis.com!1501372800!1501459199.xml'
            )
        )

        self.assertTrue(
            filecmp.cmp(
                './google.com!glenjarvis.com!1501372800!1501459199.xml',
                './test/google.com!glenjarvis.com!1501372800!1501459199.xml',
                shallow=False
            )
        )


class ApiIntegrationTests(unittest.TestCase):

    """Integration-tests for the API"""

    def setUp(self):
        integration_test_clean_up()

    def tearDown(self):
        integration_test_clean_up()

    def test_api(self):

        """This test verifies the file generation capability of the API."""

        self.assertFalse(
            os.path.isfile(
                './test/google.com!glenjarvis.com!1501372800!1501459199.xml'
            )
        )

        system_under_test = file_extraction.DmarcFileExtractor('./test')
        actual_result = system_under_test.process(
            './tcq88aasf2uj5r4dknkpmp641bloic79f8399ag1'
        )

        # verification of function result
        self.assertEqual(1, len(actual_result))

        self.assertEqual(
            './test/google.com!glenjarvis.com!1501372800!1501459199.xml',
            actual_result[0]
        )

        # verification of side effects
        self.assertTrue(
            os.path.isfile(
                './test/google.com!glenjarvis.com!1501372800!1501459199.xml'
            )
        )

        self.assertTrue(
            filecmp.cmp(
                './google.com!glenjarvis.com!1501372800!1501459199.xml',
                './test/google.com!glenjarvis.com!1501372800!1501459199.xml',
                shallow=False
            )
        )
