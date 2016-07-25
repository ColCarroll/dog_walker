import json
import os
import time
import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup
from get_flag import BASE, INDEX, get_index_links, get_soup, get_flag_data, FlagTask

from config import TEST_DATA_DIR, TEST_DATABASE

TEST_INDEX = os.path.join(TEST_DATA_DIR, 'index.html')
TEST_FLAG = os.path.join(TEST_DATA_DIR, 'dallas_flag.html')
TEST_NO_FLAG = os.path.join(TEST_DATA_DIR, 'flag_day.html')


def mock_client(url):
    if url == os.path.join(BASE, INDEX) or 'index' in url:
        return open(TEST_INDEX).read()
    elif 'flag' in url:
        return open(TEST_FLAG).read()
    else:
        return open(TEST_NO_FLAG).read()

MockFlagTask = FlagTask
MockFlagTask.database = TEST_DATABASE


class TestGetFlag(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.flag_soup = get_soup('flag', mock_client)
        self.not_flag_soup = get_soup('nonsense', mock_client)

    def test_get_soup(self):
        self.assertIsInstance(get_soup('index', mock_client), BeautifulSoup)
        self.assertIsInstance(get_soup('flag', mock_client), BeautifulSoup)

    def test_get_all_links(self):
        self.assertEqual(len(get_index_links(mock_client)), 10)

    def test_get_flag_data(self):
        self.assertDictEqual(
            get_flag_data(self.flag_soup),
            {u'until': u'Sunset, July 12, 2016',
             u'why': u'As a mark of respect for the victims of the attack on police officers perpetrated on Thursday, July 7, 2016, in Dallas, Texas',  # noqa
             u'full_text': u'As a mark of respect for the victims of the attack on police officers perpetrated on Thursday, July 7, 2016, in Dallas, Texas, by the authority vested in me as President of the United States by the Constitution and the laws of the United States of America, I hereby order that the flag of the United States shall be flown at half-staff at the White House and upon all public buildings and grounds, at all military posts and naval stations, and on all naval vessels of the Federal Government in the District of Columbia and throughout the United States and its Territories and possessions until sunset, July 12, 2016. I also direct that the flag shall be flown at half-staff for the same length of time at all United States embassies, legations, consular offices, and other facilities abroad, including all military facilities and naval vessels and stations.'  # noqa
             })

    def test_ignore_non_flag_data(self):
        self.assertEqual(get_flag_data(self.not_flag_soup), {})


class TestFlagTask(unittest.TestCase):
    def setUp(self):
        self.timeout = 60
        self.task = MockFlagTask(timeout=self.timeout, client=mock_client)

    def tearDown(self):
        if os.path.exists(self.task.database):
            os.remove(self.task.database)

    def test_correct_output(self):
        # There is only one article about half staff flags
        self.assertListEqual([json.loads(message) for message in self.task.run()],
                             [get_flag_data(get_soup('flag', mock_client))])

    def test_only_runs_once(self):
        # Should remember that it has already seen a message
        self.assertEqual(len(self.task.run()), 1)
        self.assertEqual(len(self.task.run()), 0)

    def test_only_runs_after_timeout(self):
        current_time = time.time()
        self.assertTrue(self.task.should_run())
        self.task.run()
        self.assertFalse(self.task.should_run())
        with patch('time.time') as mock_time:
            mock_time.return_value = current_time + self.timeout - 1  # less than timeout!
            self.assertFalse(self.task.should_run())
            mock_time.return_value = current_time + self.timeout * 2  # more than timeout!
            self.assertTrue(self.task.should_run())
