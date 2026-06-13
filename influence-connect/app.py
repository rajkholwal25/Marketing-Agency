from flask import Flask

from config import Config
from extensions import db, login_manager
from models import User


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from routes.admin import admin_bp
    from routes.auth import auth_bp
    from routes.brand import brand_bp
    from routes.influencer import influencer_bp
    from routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(brand_bp)
    app.register_blueprint(influencer_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()
        _seed_data()

    return app


def _seed_data():
    from models import BrandProfile, Category, InfluencerProfile

    if Category.query.first():
        return

    categories = [
        Category(name="Sports", slug="sports", icon="⚽", color="#ef4444"),
        Category(name="Study", slug="study", icon="📚", color="#3b82f6"),
        Category(name="Makeup", slug="makeup", icon="💄", color="#ec4899"),
        Category(name="Fashion", slug="fashion", icon="👗", color="#a855f7"),
        Category(name="Tech", slug="tech", icon="💻", color="#06b6d4"),
        Category(name="Food", slug="food", icon="🍔", color="#f59e0b"),
        Category(name="Travel", slug="travel", icon="✈️", color="#10b981"),
        Category(name="Fitness", slug="fitness", icon="💪", color="#f97316"),
    ]
    db.session.add_all(categories)
    db.session.flush()

    admin = User(email="admin@influence.com", role="admin")
    admin.set_password("admin123")
    db.session.add(admin)

    # Demo brand
    brand_user = User(email="brand@demo.com", role="brand")
    brand_user.set_password("demo123")
    db.session.add(brand_user)
    db.session.flush()
    db.session.add(
        BrandProfile(
            user_id=brand_user.id,
            company_name="Glow Cosmetics",
            industry="Beauty",
            website="https://glowcosmetics.com",
            description="Premium beauty brand looking for authentic creators.",
            contact_email="brand@demo.com",
        )
    )

    # Demo influencers
    demo_influencers = [
        ("sports", "Rahul Sharma", "rahul_fitness", 125000, 450000, 25000),
        ("sports", "Priya Athlete", "priya_runs", 89000, 320000, 18000),
        ("study", "Study With Arjun", "arjun_studies", 210000, 780000, 35000),
        ("study", "Neha Educates", "neha_edu", 156000, 520000, 28000),
        ("makeup", "Glam by Kavya", "kavya_glam", 340000, 1200000, 55000),
        ("makeup", "Beauty Rituals", "beauty_rituals", 275000, 950000, 42000),
        ("fashion", "Style Diaries", "style_diaries", 198000, 680000, 32000),
        ("tech", "Tech Talk India", "techtalk_in", 420000, 1500000, 75000),
    ]

    cat_map = {c.slug: c.id for c in categories}
    for slug, name, insta, followers, reach, price in demo_influencers:
        user = User(email=f"{insta}@demo.com", role="influencer")
        user.set_password("demo123")
        db.session.add(user)
        db.session.flush()
        db.session.add(
            InfluencerProfile(
                user_id=user.id,
                full_name=name,
                category_id=cat_map[slug],
                instagram_handle=insta,
                followers=followers,
                monthly_reach=reach,
                monthly_pricing=price,
                bio=f"Content creator specializing in {slug}. Available for brand collaborations.",
            )
        )

    db.session.commit()
