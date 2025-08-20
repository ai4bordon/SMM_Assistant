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
        # Безопасное логирование токена (не показываем токен, если он None)
        token_log = vk_access_token[:10] + "..." if vk_access_token else "None"
        logger.debug(f"VKStats initialized with vk_access_token: {token_log} and group_id: {group_id}")

    def get_stats(self, start_date, end_date):
        # Проверка на None для обязательных параметров
        if not self.vk_access_token or not self.group_id:
            raise ValueError("VK access token and group ID must be provided")
            
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
        
        # Проверка на пустой ответ
        if not response:
            raise Exception("Empty response from VK API")
        
        # Проверка на ошибки в ответе
        if 'error' in response:
            error_code = response['error'].get('error_code', 'Unknown')
            error_msg = response['error'].get('error_msg', 'Unknown error')
            raise Exception(f"VK API error {error_code}: {error_msg}")
        
        # Проверка наличия ключа 'response' в ответе
        if 'response' not in response:
            raise Exception("Invalid response format from VK API: missing 'response' key")
        
        # Проверка на пустой массив в response
        if not response['response']:
            return None  # Возвращаем None, если нет данных
        
        return response['response'][0]

    def get_followers(self):
        # Проверка на None для обязательных параметров
        if not self.vk_access_token or not self.group_id:
            raise ValueError("VK access token and group ID must be provided")
            
        url = 'https://api.vk.com/method/groups.getMembers'
        params = {
            'access_token': self.vk_access_token,
            'v': '5.236',
            'group_id': self.group_id
        }
        logger.debug(f"Getting followers with params: {params}")
        response = requests.get(url, params=params).json()
        logger.debug(f"Followers response: {response}")
        
        # Проверка на пустой ответ
        if not response:
            raise Exception("Empty response from VK API")
        
        # Проверка на ошибки в ответе
        if 'error' in response:
            error_code = response['error'].get('error_code', 'Unknown')
            error_msg = response['error'].get('error_msg', 'Unknown error')
            raise Exception(f"VK API error {error_code}: {error_msg}")
        
        # Проверка наличия ключа 'response' в ответе
        if 'response' not in response:
            raise Exception("Invalid response format from VK API: missing 'response' key")
        
        # Проверка наличия ключа 'count' в response
        if 'count' not in response['response']:
            raise Exception("Invalid response format from VK API: missing 'count' key in 'response'")
        
        return response['response']['count']
