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
            error_msg = f"Invalid JSON response in upload_photo (upload_url_response): {upload_url_response.text}"
            logger.error(error_msg)
            raise Exception(f"Ошибка при получении URL для загрузки фото: Неверный формат ответа от VK API") from e

        # Проверка на ошибки в ответе API
        if 'error' in upload_url_response_json:
            error_code = upload_url_response_json['error'].get('error_code', 'unknown')
            error_msg = upload_url_response_json['error'].get('error_msg', 'Неизвестная ошибка')
            
            # Обработка специфичных кодов ошибок VK
            if error_code == 5:
                logger.error(f"VK API authentication error: {error_msg}")
                raise Exception("Ошибка аутентификации VK API: Неверный ключ доступа. Проверьте настройки.")
            elif error_code == 500:
                logger.error(f"VK API server error: {error_msg}")
                raise Exception("Ошибка сервера VK API. Попробуйте повторить позже.")
            elif error_code == 100:
                logger.error(f"VK API validation error: {error_msg}")
                raise Exception("Ошибка валидации параметров запроса VK API.")
            else:
                logger.error(f"VK API error (code {error_code}): {error_msg}")
                raise Exception(f"Ошибка VK API при получении URL для загрузки фото: {error_msg}")
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
                error_msg = f"Invalid JSON response in upload_photo (upload_response): {upload_response.text}"
                logger.error(error_msg)
                raise Exception(f"Ошибка при загрузке фото: Неверный формат ответа от VK API") from e

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
                error_msg = f"Invalid JSON response in upload_photo (save_response): {save_response.text}"
                logger.error(error_msg)
                raise Exception(f"Ошибка при сохранении фото: Неверный формат ответа от VK API") from e

            # Проверка на ошибки в ответе API при сохранении фото
            if 'error' in save_response_json:
                error_code = save_response_json['error'].get('error_code', 'unknown')
                error_msg = save_response_json['error'].get('error_msg', 'Неизвестная ошибка')
                
                # Обработка специфичных кодов ошибок VK
                if error_code == 5:
                    logger.error(f"VK API authentication error during photo save: {error_msg}")
                    raise Exception("Ошибка аутентификации VK API при сохранении фото: Неверный ключ доступа.")
                elif error_code == 500:
                    logger.error(f"VK API server error during photo save: {error_msg}")
                    raise Exception("Ошибка сервера VK API при сохранении фото. Попробуйте повторить позже.")
                elif error_code == 100:
                    logger.error(f"VK API validation error during photo save: {error_msg}")
                    raise Exception("Ошибка валидации параметров запроса VK API при сохранении фото.")
                else:
                    logger.error(f"VK API error during photo save (code {error_code}): {error_msg}")
                    raise Exception(f"Ошибка VK API при сохранении фото: {error_msg}")
            
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
            error_msg = f"Invalid JSON response: {response.text}"
            logger.error(error_msg)
            raise Exception(f"Ошибка при публикации поста: Неверный формат ответа от VK API") from e
        
        # Проверка на ошибки в ответе API
        if 'error' in response_json:
            error_code = response_json['error'].get('error_code', 'unknown')
            error_msg = response_json['error'].get('error_msg', 'Неизвестная ошибка')
            
            # Обработка специфичных кодов ошибок VK
            if error_code == 5:
                logger.error(f"VK API authentication error during post publishing: {error_msg}")
                raise Exception("Ошибка аутентификации VK API при публикации поста: Неверный ключ доступа.")
            elif error_code == 500:
                logger.error(f"VK API server error during post publishing: {error_msg}")
                raise Exception("Ошибка сервера VK API при публикации поста. Попробуйте повторить позже.")
            elif error_code == 100:
                logger.error(f"VK API validation error during post publishing: {error_msg}")
                raise Exception("Ошибка валидации параметров запроса VK API при публикации поста.")
            elif error_code == 214:
                logger.error(f"VK API access error during post publishing: {error_msg}")
                raise Exception("Ошибка доступа VK API при публикации поста: Нет прав на публикацию.")
            else:
                logger.error(f"VK API error during post publishing (code {error_code}): {error_msg}")
                raise Exception(f"Ошибка VK API при публикации поста: {error_msg}")
        
        return response_json
