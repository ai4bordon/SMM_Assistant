# SMM Assistant

SMM Assistant - это веб-приложение на Flask, которое помогает автоматизировать создание и публикацию постов в социальных сетях.

## Функционал

*   **Генерация постов:** Автоматическая генерация текстового контента для постов с помощью OpenAI.
*   **Генерация изображений:** Автоматическая генерация изображений для постов с помощью OpenAI (DALL-E).
*   **Публикация в VK:** Автоматическая публикация сгенерированных постов в VK.
*   **История постов:** Просмотр истории сгенерированных и опубликованных постов.
*   **Статистика VK:** Просмотр статистики по подписчикам в VK.
*   **Современный интерфейс:** Стильный и интерактивный интерфейс с эффектом стекла, неоморфизмом и анимированным фоном.

## Технологии

*   **Backend:** Flask, SQLAlchemy, Bcrypt, WTForms
*   **Frontend:** HTML, CSS, Bootstrap, JavaScript, tsParticles
*   **API:** OpenAI, VK API
*   **База данных:** PostgreSQL (в Docker), SQLite (для локальной разработки)
*   **Деплой:** Docker, Gunicorn

## Установка и запуск

### Локальный запуск

1.  **Клонируйте репозиторий:**
    ```
    git clone https://github.com/ai4bordon/SMM_Assistant.git
    cd SMM_Assistant
    ```
2.  **Создайте и активируйте виртуальное окружение:**
    ```
    python -m venv env
    source env/bin/activate  # для Linux/macOS
    env\Scripts\activate  # для Windows
    ```
3.  **Установите зависимости:**
    ```
    pip install -r requirements.txt
    ```
4.  **Создайте файл `.env`** и заполните его:
    ```
    SECRET_KEY=your_secret_key
    DATABASE_URL=sqlite:///instance/site.db
    OPENAI_KEY=your_openai_key
    VK_API_KEY=your_vk_api_key
    VK_GROUP_ID=your_vk_group_id
    ```
5.  **Запустите приложение:**
    ```
    flask run
    ```

### Запуск через Docker

1.  **Установите Docker и Docker Compose.**
2.  **Создайте файл `.env`** и заполните его:
    ```
    SECRET_KEY=your_production_secret_key
    DATABASE_URL=postgresql://user:password@db:5432/mydatabase
    OPENAI_KEY=your_openai_key
    VK_API_KEY=your_vk_api_key
    VK_GROUP_ID=your_vk_group_id
    POSTGRES_USER=user
    POSTGRES_PASSWORD=password
    POSTGRES_DB=mydatabase
    ```
3.  **Запустите приложение:**
    ```
    docker-compose up --build -d
    ```
4.  **Выполните миграции базы данных:**
    ```
    docker-compose exec web flask db init
    docker-compose exec web flask db migrate -m "Initial migration."
    docker-compose exec web flask db upgrade