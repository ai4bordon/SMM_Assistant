import requests
import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class VKStats:
    def __init__(self, vk_access_token, group_id):
        self.vk_access_token = vk_access_token
        self.group_id = group_id
        logger.debug(f"VKStats initialized with vk_access_token: {vk_access_token[:10]}... and group_id: {group_id}")

    def get_stats(self, start_date, end_date):
        url = 'https://api.vk.com/method/stats.get'
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        start_date = start_date.replace(tzinfo=datetime.timezone.utc)
        end_date = end_date.replace(tzinfo=datetime.timezone.utc)

        start_unix_time = start_date.timestamp()
        end_unix_time = end_date.timestamp()

        params = {
            'access_token': self.vk_access_token,
            'v': '5.236',
            'group_id': self.group_id,
            'timestamp_from': start_unix_time,
            'timestamp_to': end_unix_time
        }
        logger.debug(f"Getting stats with params: {params}")
        response = requests.get(url, params=params).json()
        logger.debug(f"Stats response: {response}")
        if 'error' in response:
            raise Exception(response['error']['error_msg'])
        else:
            return response['response'][0]

    def get_followers(self):
        url = 'https://api.vk.com/method/groups.getMembers'
        params = {
            'access_token': self.vk_access_token,
            'v': '5.236',
            'group_id': self.group_id
        }
        logger.debug(f"Getting followers with params: {params}")
        response = requests.get(url, params=params).json()
        logger.debug(f"Followers response: {response}")
        if 'error' in response:
            raise Exception(response['error']['error_msg'])
        else:
            return response['response']['count']
