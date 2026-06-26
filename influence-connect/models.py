from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=True, index=True)
    mobile = db.Column(db.String(20), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, brand, influencer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    brand_profile = db.relationship(
        "BrandProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    influencer_profile = db.relationship(
        "InfluencerProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    icon = db.Column(db.String(10), nullable=False)
    color = db.Column(db.String(20), nullable=False, default="#6366f1")

    influencers = db.relationship("InfluencerProfile", back_populates="category")


class BrandProfile(db.Model):
    __tablename__ = "brand_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    company_name = db.Column(db.String(120), nullable=False)
    industry = db.Column(db.String(80))
    website = db.Column(db.String(200))
    description = db.Column(db.Text)
    contact_email = db.Column(db.String(120))

    user = db.relationship("User", back_populates="brand_profile")


class InfluencerProfile(db.Model):
    __tablename__ = "influencer_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    instagram_handle = db.Column(db.String(80), nullable=False)
    instagram_url = db.Column(db.String(200))
    followers = db.Column(db.String(30), default="—")
    monthly_reach = db.Column(db.String(30), default="—")
    reel_pricing = db.Column(db.Float, nullable=False, default=0)
    story_pricing = db.Column(db.Float, nullable=False, default=0)
    post_pricing = db.Column(db.Float, nullable=False, default=0)
    bio = db.Column(db.Text)

    user = db.relationship("User", back_populates="influencer_profile")
    category = db.relationship("Category", back_populates="influencers")

    @property
    def profile_url(self) -> str:
        from utils.instagram import instagram_profile_url

        return self.instagram_url or instagram_profile_url(self.instagram_handle)
