import unittest
import datetime

import parse_filenames


class MyTest(unittest.TestCase):
    def test(self):
        self.assertEqual(parse_filenames.details_from_filename(
                        'google.com!glenjarvis.com!1501372800!1501459199.zip'),
                        ['google.com', 'glenjarvis.com',
                            datetime.datetime(2017, 7, 30, 0, 0, 0,
                                              tzinfo=datetime.timezone.utc),
                            datetime.datetime(2017, 7, 30, 23, 59, 59,
                                              tzinfo=datetime.timezone.utc)]
        )
