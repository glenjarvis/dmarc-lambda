import unittest

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


class ConsumerTests(unittest.TestCase):

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
