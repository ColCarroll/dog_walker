import json
import logging
import re

from bs4 import BeautifulSoup
from pete import BasicSQLiteTask, BasicEmailBroadcaster
import requests

from config import DATABASE, FLAG_TABLE, EMAIL_CONFIG


BASE = "https://www.whitehouse.gov/"
INDEX = "briefing-room/presidential-actions/proclamations"

logger = logging.getLogger(__name__)


def urljoin(*pieces):
    return "/".join(s.strip("/") for s in pieces)


def get_html(url):
    logger.info('Fetching {}'.format(url))
    r = requests.get(url)
    r.raise_for_status()
    return r.content


def get_soup(url, client=None):
    """Reads the presidential proclamation index

    Args:
        client: a function that fetches html given a url

    Returns:
        beautifulsoup parsed html
    """
    if client is None:
        client = get_html
    return BeautifulSoup(client(url), "html.parser")


def get_index_links(client=None):
    soup = get_soup(urljoin(BASE, INDEX), client)
    links = []
    for anchor in soup.find_all('a'):
        link = anchor.get('href')
        if link.startswith('/the-press-office'):
            links.append(urljoin(BASE, link))
    return links


def get_flag_data(soup):
    """Get data about the flag flying at half staff

    Args:
        soup: a beautifulsoup object

    Returns:
        data from first paragraph to match the `when_ptrn`, or an empty dict
    """
    why_ptrn = r"(.*), by the authority vested in me"
    when_ptrn = r"the flag of the United States shall be flown at half-staff.*until (.*)\. "
    flag_data = {}
    for p in soup.find_all('p'):
        when = re.search(when_ptrn, p.text)
        if when:
            why = re.search(why_ptrn, p.text)
            if why:
                flag_data["why"] = why.group(1).strip()
            else:
                flag_data["why"] = ""
            flag_data["until"] = when.group(1).title()
            flag_data["full_text"] = p.text.strip()
            return flag_data
    return flag_data


class FlagBroadcaster(BasicEmailBroadcaster):
    name = 'email flag broadcaster'
    email_config_filename = EMAIL_CONFIG
    subject_formatter = 'Flag at Half-Staff Until {until}'
    message_formatter = '{full_text}'


class FlagTask(BasicSQLiteTask):
    name = 'Why is the flag at half mast task'
    database = DATABASE
    table = FLAG_TABLE

    def __init__(self, timeout, client=None):
        super().__init__()
        self.timeout = timeout
        self.client = client

    def should_run(self):
        return self.time_since_last_message() > self.timeout

    def run(self):
        messages = []
        for url in get_index_links(self.client):
            flag_data = json.dumps(get_flag_data(get_soup(url, self.client)))
            if flag_data != '{}' and self.is_message_new(flag_data):
                self.register_message(flag_data)
                messages.append(flag_data)
        return messages[-1::-1]
