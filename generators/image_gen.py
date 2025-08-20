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

class ImageGenerator:
    def __init__(self, openai_key):
        self.client = OpenAI(api_key=openai_key)

    @retry_on_exception(max_retries=3, delay=1, backoff=2)
    def generate_image(self, prompt):
        try:
            response = self.client.images.generate(
              model="dall-e-3",
              prompt=prompt,
              size="1024x1024",
              quality="standard",
              n=1,
              timeout=60,
            )

            image_url = response.data[0].url
            return image_url
        except RateLimitError as e:
            logger.error(f"OpenAI API rate limit exceeded in image generation: {str(e)}")
            raise Exception("Превышен лимит запросов к OpenAI API. Пожалуйста, попробуйте позже.")
        except AuthenticationError as e:
            logger.error(f"OpenAI API authentication error in image generation: {str(e)}")
            raise Exception("Ошибка аутентификации OpenAI API. Проверьте правильность API ключа.")
        except APIConnectionError as e:
            logger.error(f"OpenAI API connection error in image generation: {str(e)}")
            raise Exception("Ошибка подключения к OpenAI API. Проверьте подключение к интернету.")
        except APIError as e:
            logger.error(f"OpenAI API error in image generation: {str(e)}")
            raise Exception(f"Ошибка OpenAI API: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in generate_image: {str(e)}")
            raise Exception(f"Произошла непредвиденная ошибка при генерации изображения: {str(e)}")
