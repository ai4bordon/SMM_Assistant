import requests
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class VKPublisher:
    def __init__(self, vk_api_key, group_id):
        self.vk_api_key = vk_api_key
        self.group_id = group_id
        logger.debug(f"VKPublisher initialized with vk_api_key: {vk_api_key[:10]}... and group_id: {group_id}")

    def upload_photo(self, image_url):
        logger.debug(f"Uploading photo from URL: {image_url}")
        upload_url_response = requests.get(
            'https://api.vk.com/method/photos.getWallUploadServer',
            params={
                'access_token': self.vk_api_key,
                'v': '5.236',
                'group_id': self.group_id
            }
        )
        
        logger.debug(f"Upload URL response status: {upload_url_response.status_code}")
        logger.debug(f"Upload URL response text: {upload_url_response.text[:200]}...")
        
        # Проверка корректности JSON для upload_url_response
        try:
            upload_url_response_json = upload_url_response.json()
        except ValueError as e:
            print(f"Invalid JSON response in upload_photo (upload_url_response): {upload_url_response.text}")
            raise Exception(f"Invalid JSON response from VK API in upload_photo: {upload_url_response.text}") from e

        if 'error' in upload_url_response_json:
            raise Exception(upload_url_response_json['error']['error_msg'])
        else:
            upload_url = upload_url_response_json['response']['upload_url']
            image_data = requests.get(image_url).content
            upload_response = requests.post(upload_url, files={'photo': ('image.jpg', image_data)})
            
            logger.debug(f"Upload response status: {upload_response.status_code}")
            logger.debug(f"Upload response text: {upload_response.text[:200]}...")
            
            # Проверка корректности JSON для upload_response
            try:
                upload_response_json = upload_response.json()
            except ValueError as e:
                print(f"Invalid JSON response in upload_photo (upload_response): {upload_response.text}")
                raise Exception(f"Invalid JSON response from VK API in upload_photo: {upload_response.text}") from e

            save_response = requests.get(
                'https://api.vk.com/method/photos.saveWallPhoto',
                params={
                    'access_token': self.vk_api_key,
                    'v': '5.236',
                    'group_id': self.group_id,
                    'photo': upload_response_json['photo'],
                    'server': upload_response_json['server'],
                    'hash': upload_response_json['hash']
                }
            )
            
            logger.debug(f"Save response status: {save_response.status_code}")
            logger.debug(f"Save response text: {save_response.text[:200]}...")
            
            # Проверка корректности JSON для save_response
            try:
                save_response_json = save_response.json()
            except ValueError as e:
                print(f"Invalid JSON response in upload_photo (save_response): {save_response.text}")
                raise Exception(f"Invalid JSON response from VK API in upload_photo: {save_response.text}") from e

            photo_id = save_response_json['response'][0]['id']
            owner_id = save_response_json['response'][0]['owner_id']

            return f'photo{owner_id}_{photo_id}'

    def publish_post(self, content, image_url=None):
        # Проверка на пустые параметры
        if not self.vk_api_key or not self.group_id:
            raise ValueError("vk_api_key and group_id must be provided and not empty")
        
        logger.debug(f"Publishing post with content: {content[:50]}...")
        params = {
            'access_token': self.vk_api_key,
            'from_group': 1,
            'v': '5.236',
            'owner_id': f'-{self.group_id}',
            'message': content
        }
        if image_url:
            attachment = self.upload_photo(image_url)
            params['attachments'] = attachment

        response = requests.post('https://api.vk.com/method/wall.post', data=params)
        
        logger.debug(f"Post response status: {response.status_code}")
        logger.debug(f"Post response text: {response.text[:200]}...")
        
        # Проверка, что ответ является корректным JSON
        try:
            response_json = response.json()
        except ValueError as e:
            # Вывод содержимого ответа для отладки
            print(f"Invalid JSON response: {response.text}")
            raise Exception(f"Invalid JSON response from VK API: {response.text}") from e
        
        # Проверка на ошибки в ответе API
        if 'error' in response_json:
            logger.error(f"VK API error: {response_json['error']['error_msg']}")
            raise Exception(response_json['error']['error_msg'])
        
        return response_json
