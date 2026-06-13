from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from models import BrandProfile, Category, InfluencerProfile, User
from routes.auth import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    users = User.query.order_by(User.created_at.desc()).all()
    categories = Category.query.order_by(Category.name).all()
    brands = BrandProfile.query.all()
    influencers = InfluencerProfile.query.all()
    return render_template(
        "admin/dashboard.html",
        users=users,
        categories=categories,
        brands=brands,
        influencers=influencers,
        stats={
            "users": len(users),
            "brands": len(brands),
            "influencers": len(influencers),
            "categories": len(categories),
        },
    )


@admin_bp.route("/category/add", methods=["POST"])
@login_required
@role_required("admin")
def add_category():
    name = request.form.get("name", "").strip()
    icon = request.form.get("icon", "✨").strip() or "✨"
    color = request.form.get("color", "#6366f1").strip()

    if not name:
        flash("Category name is required.", "error")
    elif Category.query.filter_by(name=name).first():
        flash("Category already exists.", "error")
    else:
        slug = name.lower().replace(" ", "-").replace("/", "-")
        db.session.add(Category(name=name, slug=slug, icon=icon, color=color))
        db.session.commit()
        flash(f'Category "{name}" added!', "success")

    return redirect(url_for("admin.dashboard"))
