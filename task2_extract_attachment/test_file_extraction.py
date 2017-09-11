import unittest

from file_extraction import *


class ConsumerTests(unittest.TestCase):

    def test_path_selection_consumer_none_match(self):

        def return_false(x):
            return False

        class EqualAssertion:

            def __init__(self, test_case, value):
                self._test_case = test_case
                self._value = value

            def __call__(self, value):
                self._test_case.assertEqual(self._value, value)

        class ExplodeIfCalledConsumer:

            def __call__(self, value):
                raise AssertionError

        exploding_consumer = ExplodeIfCalledConsumer()
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
            EqualAssertion(self, 3)
        )
        system_under_test(3)
