import os
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Open AI
openai_key = os.environ.get('OPENAI_KEY')

# Проверка наличия API ключа OpenAI
if not openai_key:
    error_msg = "OPENAI_KEY environment variable is not set. Please set it in your .env file or environment variables."
    logger.error(error_msg)
    raise ValueError(error_msg)