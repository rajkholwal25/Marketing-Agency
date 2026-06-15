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
        try:
            db.create_all()
            _migrate_pricing_columns()
            _migrate_profile_stats()
            _seed_data()
        except Exception as exc:
            if app.config.get("SQLALCHEMY_DATABASE_URI", "").startswith("sqlite"):
                raise
            print(
                "\n[!] Supabase connection failed - check DATABASE_URL password in .env\n"
                f"   Error: {exc}\n"
            )
            raise SystemExit(1) from exc

    return app


def _migrate_pricing_columns():
    """Add reel/story/post pricing columns; migrate from old monthly_pricing if present."""
    from sqlalchemy import inspect, text

    insp = inspect(db.engine)
    if "influencer_profiles" not in insp.get_table_names():
        return

    cols = {c["name"] for c in insp.get_columns("influencer_profiles")}
    if "reel_pricing" in cols:
        return

    stmts = [
        "ALTER TABLE influencer_profiles ADD COLUMN reel_pricing DOUBLE PRECISION DEFAULT 0",
        "ALTER TABLE influencer_profiles ADD COLUMN story_pricing DOUBLE PRECISION DEFAULT 0",
        "ALTER TABLE influencer_profiles ADD COLUMN post_pricing DOUBLE PRECISION DEFAULT 0",
    ]
    if "monthly_pricing" in cols:
        stmts.append(
            "UPDATE influencer_profiles SET reel_pricing = monthly_pricing, "
            "story_pricing = ROUND(monthly_pricing * 0.35), "
            "post_pricing = ROUND(monthly_pricing * 0.5)"
        )

    with db.engine.begin() as conn:
        for sql in stmts:
            conn.execute(text(sql))


def _format_int_stat(value) -> str:
    try:
        n = int(value)
    except (TypeError, ValueError):
        return str(value) if value else "—"
    if n <= 0:
        return "—"
    if n >= 1_000_000_000:
        s = f"{n / 1_000_000_000:.1f}B"
    elif n >= 1_000_000:
        s = f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        s = f"{n / 1_000:.1f}K"
    else:
        return str(n)
    return s.replace(".0K", "K").replace(".0M", "M").replace(".0B", "B")


def _migrate_profile_stats():
    """Convert followers/reach to text (1.1M, 125K); add instagram_url column."""
    from sqlalchemy import inspect, text

    insp = inspect(db.engine)
    if "influencer_profiles" not in insp.get_table_names():
        return

    cols = {c["name"] for c in insp.get_columns("influencer_profiles")}

    if "instagram_url" not in cols:
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE influencer_profiles ADD COLUMN instagram_url VARCHAR(200)"))

    if "postgresql" not in str(db.engine.url):
        return

    with db.engine.connect() as conn:
        types = {
            row[0]: row[1]
            for row in conn.execute(text(
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_name = 'influencer_profiles' "
                "AND column_name IN ('followers', 'monthly_reach')"
            ))
        }

    if types.get("followers") != "integer":
        return

    stat_case = """
        CASE
            WHEN {col} >= 1000000000 THEN TRIM(TRAILING '.0' FROM ROUND({col}::numeric / 1000000000, 1)::text) || 'B'
            WHEN {col} >= 1000000 THEN TRIM(TRAILING '.0' FROM ROUND({col}::numeric / 1000000, 1)::text) || 'M'
            WHEN {col} >= 1000 THEN TRIM(TRAILING '.0' FROM ROUND({col}::numeric / 1000, 1)::text) || 'K'
            ELSE {col}::text
        END
    """

    with db.engine.begin() as conn:
        conn.execute(text(
            f"ALTER TABLE influencer_profiles ALTER COLUMN followers TYPE VARCHAR(30) "
            f"USING ({stat_case.format(col='followers')})"
        ))
        conn.execute(text(
            f"ALTER TABLE influencer_profiles ALTER COLUMN monthly_reach TYPE VARCHAR(30) "
            f"USING ({stat_case.format(col='monthly_reach')})"
        ))
        conn.execute(text(
            "UPDATE influencer_profiles SET instagram_url = 'https://instagram.com/' || instagram_handle "
            "WHERE instagram_url IS NULL OR instagram_url = ''"
        ))


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

    # Demo: slug, name, insta, followers, reach, reel, story, post (stats as strings)
    demo_influencers = [
        ("sports", "Rahul Sharma", "rahul_fitness", "125K", "450K", 15000, 5000, 8000),
        ("sports", "Priya Athlete", "priya_runs", "89K", "320K", 12000, 4000, 6000),
        ("study", "Study With Arjun", "arjun_studies", "210K", "780K", 25000, 8000, 12000),
        ("study", "Neha Educates", "neha_edu", "156K", "520K", 18000, 6000, 10000),
        ("makeup", "Glam by Kavya", "kavya_glam", "340K", "1.2M", 45000, 15000, 25000),
        ("makeup", "Beauty Rituals", "beauty_rituals", "275K", "950K", 35000, 12000, 20000),
        ("fashion", "Style Diaries", "style_diaries", "198K", "680K", 22000, 7000, 11000),
        ("tech", "Tech Talk India", "techtalk_in", "420K", "1.5M", 55000, 18000, 30000),
    ]

    cat_map = {c.slug: c.id for c in categories}
    for slug, name, insta, followers, reach, reel, story, post in demo_influencers:
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
                instagram_url=f"https://instagram.com/{insta}",
                followers=followers,
                monthly_reach=reach,
                reel_pricing=reel,
                story_pricing=story,
                post_pricing=post,
                bio=f"Content creator specializing in {slug}. Available for brand collaborations.",
            )
        )

    db.session.commit()
