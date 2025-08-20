import logging
import time
import random
from functools import wraps
from openai import OpenAI, RateLimitError, APIConnectionError, APIError, AuthenticationError

# Настройка логирования
logger = logging.getLogger(__name__)

def retry_on_exception(max_retries=3, delay=1, backoff=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except (RateLimitError, APIConnectionError, APIError) as e:
                    retries += 1
                    if retries >= max_retries:
                        raise e
                    logger.warning(f"Exception occurred: {str(e)}. Retrying in {current_delay} seconds...")
                    time.sleep(current_delay)
                    current_delay *= backoff
                except Exception as e:
                    raise e
        return wrapper
    return decorator

class PostGenerator:
    def __init__(self, openai_key, tone, topic):
        self.client = OpenAI(api_key=openai_key)
        self.tone = tone
        self.topic = topic

    @retry_on_exception(max_retries=3, delay=1, backoff=2)
    def generate_post(self):
        try:
            response = self.client.chat.completions.create(
              model="gpt-5-nano",
              messages=[
                {"role": "system", "content": "Ты высококвалифицированный SMM специалист, который будет помогать в генерации текста для постов с заданной теме тематикой и заданным тоном."},
                {"role": "user", "content": f"Сгенерируй пост для соцсетей с темой {self.topic}, используя тон: {self.tone}"}
              ],
              timeout=60,
            )
            return response.choices[0].message.content
        except RateLimitError as e:
            logger.error(f"OpenAI API rate limit exceeded: {str(e)}")
            raise Exception("Превышен лимит запросов к OpenAI API. Пожалуйста, попробуйте позже.")
        except AuthenticationError as e:
            logger.error(f"OpenAI API authentication error: {str(e)}")
            raise Exception("Ошибка аутентификации OpenAI API. Проверьте правильность API ключа.")
        except APIConnectionError as e:
            logger.error(f"OpenAI API connection error: {str(e)}")
            raise Exception("Ошибка подключения к OpenAI API. Проверьте подключение к интернету.")
        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"Ошибка OpenAI API: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in generate_post: {str(e)}")
            raise Exception(f"Произошла непредвиденная ошибка при генерации поста: {str(e)}")

    @retry_on_exception(max_retries=3, delay=1, backoff=2)
    def generate_post_image_description(self):
        try:
            response = self.client.chat.completions.create(
              model="gpt-5-nano",
              messages=[
                {"role": "system", "content": "Ты ассистент, который составит промпт для нейросети, которая будет генерировать изображения. Ты должен составлять промпт на заданную тематику."},
                {"role": "user", "content": f"Составь подробный текстовый промпт для генерации изображения для соцсетей с темой {self.topic}. Промпт должен быть на английском языке, содержать детальное описание визуальных элементов, настроения и стиля изображения и быть длиной не более 10 символов."}
              ],
              timeout=60,
            )
            return response.choices[0].message.content
        except RateLimitError as e:
            logger.error(f"OpenAI API rate limit exceeded in image description generation: {str(e)}")
            raise Exception("Превышен лимит запросов к OpenAI API. Пожалуйста, попробуйте позже.")
        except AuthenticationError as e:
            logger.error(f"OpenAI API authentication error in image description generation: {str(e)}")
            raise Exception("Ошибка аутентификации OpenAI API. Проверьте правильность API ключа.")
        except APIConnectionError as e:
            logger.error(f"OpenAI API connection error in image description generation: {str(e)}")
            raise Exception("Ошибка подключения к OpenAI API. Проверьте подключение к интернету.")
        except APIError as e:
            logger.error(f"OpenAI API error in image description generation: {str(e)}")
            raise Exception(f"Ошибка OpenAI API: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in generate_post_image_description: {str(e)}")
            raise Exception(f"Произошла непредвиденная ошибка при генерации описания изображения: {str(e)}")
