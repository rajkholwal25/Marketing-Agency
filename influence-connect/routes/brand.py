from flask import Blueprint, render_template
from flask_login import current_user, login_required

from models import BrandProfile, Category, InfluencerProfile
from routes.auth import role_required

brand_bp = Blueprint("brand", __name__, url_prefix="/brand")


@brand_bp.route("/dashboard")
@login_required
@role_required("brand")
def dashboard():
    categories = Category.query.order_by(Category.name).all()
    profile = BrandProfile.query.filter_by(user_id=current_user.id).first()
    return render_template(
        "brand/dashboard.html",
        categories=categories,
        profile=profile,
    )


@brand_bp.route("/category/<slug>")
@login_required
@role_required("brand")
def category_influencers(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    influencers = (
        InfluencerProfile.query.filter_by(category_id=category.id)
        .order_by(InfluencerProfile.full_name)
        .all()
    )
    profile = BrandProfile.query.filter_by(user_id=current_user.id).first()
    return render_template(
        "brand/influencers.html",
        category=category,
        influencers=influencers,
        profile=profile,
    )
