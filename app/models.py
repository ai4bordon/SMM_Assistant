from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    vk_access_token = db.Column(db.String(250), nullable=True)
    vk_group_id = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f"User('{self.username}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(250), nullable=True)
    topic = db.Column(db.String(250), nullable=True)
    tone = db.Column(db.String(100), nullable=True)
    original_image_prompt = db.Column(db.Text, nullable=True)
    original_image_url = db.Column(db.String(250), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    user = db.relationship('User', backref=db.backref('posts', lazy=True))
    def __repr__(self):
        return f"Post('{self.id}', '{self.created_at}')"
