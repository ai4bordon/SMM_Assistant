import logging
import traceback
from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from app.models import User, Post
from app import db
from generators.text_gen import PostGenerator
from generators.image_gen import ImageGenerator
from social_publishers.vk_publisher import VKPublisher
from social_stats.vk_stats import VKStats
from config import openai_key


# Настройка логирования
logger = logging.getLogger(__name__)

smm_bp = Blueprint('smm', __name__)


@smm_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html')


@smm_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    
    # Проверка, что пользователь существует
    if user is None:
        flash('User not found. Please log in again.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        user.vk_access_token = request.form['vk_access_token']
        user.vk_group_id = request.form['vk_group_id']
        db.session.commit()
        flash('Settings saved!', 'success')

    return render_template('settings.html', user=user)


@smm_bp.route('/post-generator', methods=['GET', 'POST'])
def post_generator():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        try:
            tone = request.form['tone']
            topic = request.form['topic']
            generate_image = 'generate_image' in request.form
            auto_post = 'auto_post' in request.form
            
            # Логирование параметров запроса
            logger.info(f"Post generation request received - Tone: {tone}, Topic: {topic}, Generate Image: {generate_image}, Auto Post: {auto_post}")

            user = User.query.get(session['user_id'])
            
            # Проверка, что пользователь существует
            if user is None:
                logger.warning("User not found during post generation")
                flash('User not found. Please log in again.', 'error')
                return redirect(url_for('auth.login'))

            # Генерация текста поста
            logger.info("Starting post text generation")
            post_gen = PostGenerator(openai_key, tone, topic)
            post_content = post_gen.generate_post()
            logger.info("Post text generation completed successfully")

            image_url = None
            image_prompt = None
            if generate_image:
                # Генерация описания изображения и самого изображения
                logger.info("Starting image generation")
                image_gen = ImageGenerator(openai_key)
                image_prompt = post_gen.generate_post_image_description()
                logger.debug(f"Image prompt generated: {image_prompt}")
                image_url = image_gen.generate_image(image_prompt)
                logger.info("Image generation completed successfully")

            if auto_post:
                # Автоматическая публикация в VK
                logger.info("Starting auto-post to VK")
                vk_publisher = VKPublisher(user.vk_access_token, user.vk_group_id)
                vk_publisher.publish_post(post_content, image_url)
                logger.info("Auto-post to VK completed successfully")
                flash('Post published to VK successfully!', 'success')

            # Сохраняем пост в базу данных
            logger.info("Saving post to database")
            new_post = Post(
                content=post_content,
                image_url=image_url,
                topic=topic,
                tone=tone,
                original_image_prompt=image_prompt,
                original_image_url=image_url,
                user_id=user.id
            )
            db.session.add(new_post)
            db.session.commit()
            logger.info("Post saved to database successfully")

            return render_template('post_generator.html', post_content=post_content, image_url=image_url)
        except Exception as e:
            # Логирование ошибки с трассировкой стека
            logger.error(f"Error occurred while generating the post: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            flash(f'An error occurred while generating the post: {str(e)}', 'error')
            return render_template('post_generator.html')

    return render_template('post_generator.html')


@smm_bp.route('/vk-stats', methods=['GET'])
def vk_stats():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    
    # Проверка, что пользователь существует
    if user is None:
        flash('User not found. Please log in again.', 'error')
        return redirect(url_for('auth.login'))

    # Проверка, что учетные данные VK настроены
    if not user.vk_access_token or not user.vk_group_id:
        flash('VK API credentials not configured. Please set them in the settings.', 'error')
        return redirect(url_for('smm.settings'))

    try:
        vk_stats = VKStats(user.vk_access_token, user.vk_group_id)
        followers_count = vk_stats.get_followers()
    except ValueError as e:
        logger.error(f"VKStats initialization error: {str(e)}")
        flash('VK API credentials not configured. Please set them in the settings.', 'error')
        return redirect(url_for('smm.settings'))
    except Exception as e:
        logger.error(f"Error getting VK stats: {str(e)}")
        flash(f'Error getting VK stats: {str(e)}', 'error')
        # Возвращаем пустую статистику в случае ошибки
        stats = {
            "Followers": "Error",
            "Likes": "Error",
            "Comments": "Error",
            "Shares": "Error"
        }
        return render_template('vk_stats.html', stats=stats)

    stats = {
        "Followers": followers_count,
        "Likes": "N/A",
        "Comments": "N/A",
        "Shares": "N/A"
    }

    return render_template('vk_stats.html', stats=stats)


@smm_bp.route('/post-history')
def post_history():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    
    return render_template('post_history.html', posts=posts)

@smm_bp.route('/edit-post/<int:post_id>', methods=['POST'])
def edit_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    post = Post.query.get_or_404(post_id)
    if post.user_id != session['user_id']:
        flash('You are not authorized to edit this post.', 'error')
        return redirect(url_for('smm.post_history'))
    
    new_content = request.form['content']
    post.content = new_content
    db.session.commit()
    
    flash('Post updated successfully!', 'success')
    return redirect(url_for('smm.post_history'))


@smm_bp.route('/regenerate-image/<int:post_id>', methods=['POST'])
def regenerate_image(post_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    post = Post.query.get_or_404(post_id)
    if post.user_id != session['user_id']:
        flash('You are not authorized to regenerate image for this post.', 'error')
        return redirect(url_for('smm.post_history'))
    
    if not post.original_image_prompt:
        flash('Original image prompt not found.', 'error')
        return redirect(url_for('smm.post_history'))
    
    user = User.query.get(session['user_id'])
    image_gen = ImageGenerator(openai_key)
    new_image_url = image_gen.generate_image(post.original_image_prompt)
    
    post.image_url = new_image_url
    post.original_image_url = new_image_url
    db.session.commit()
    
    flash('Image regenerated successfully!', 'success')
    return redirect(url_for('smm.post_history'))


@smm_bp.route('/repost-to-vk/<int:post_id>', methods=['POST'])
def repost_to_vk(post_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    post = Post.query.get_or_404(post_id)
    if post.user_id != session['user_id']:
        flash('You are not authorized to repost this post.', 'error')
        return redirect(url_for('smm.post_history'))
    
    user = User.query.get(session['user_id'])
    
    # Проверка, что пользователь существует
    if user is None:
        flash('User not found. Please log in again.', 'error')
        return redirect(url_for('auth.login'))

    if not user.vk_access_token or not user.vk_group_id:
        flash('VK API credentials not configured.', 'error')
        return redirect(url_for('smm.settings'))
    
    vk_publisher = VKPublisher(user.vk_access_token, user.vk_group_id)
    try:
        vk_publisher.publish_post(post.content, post.image_url)
        flash('Post republished to VK successfully!', 'success')
    except Exception as e:
        logger.error(f"Error publishing to VK: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        flash(f'Error publishing to VK: {str(e)}', 'error')
    
    return redirect(url_for('smm.post_history'))


@smm_bp.route('/delete-post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    post = Post.query.get_or_404(post_id)
    if post.user_id != session['user_id']:
        flash('You are not authorized to delete this post.', 'error')
        return redirect(url_for('smm.post_history'))
    
    db.session.delete(post)
    db.session.commit()
    
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('smm.post_history'))