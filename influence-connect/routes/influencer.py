from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from models import BrandProfile, Category, InfluencerProfile
from routes.auth import role_required
from utils.instagram import normalize_stat, parse_instagram_handle, instagram_profile_url

influencer_bp = Blueprint("influencer", __name__, url_prefix="/influencer")


@influencer_bp.route("/dashboard")
@login_required
@role_required("influencer")
def dashboard():
    profile = InfluencerProfile.query.filter_by(user_id=current_user.id).first()
    brands = BrandProfile.query.order_by(BrandProfile.company_name).all()
    return render_template(
        "influencer/dashboard.html",
        profile=profile,
        brands=brands,
    )


@influencer_bp.route("/profile", methods=["GET", "POST"])
@login_required
@role_required("influencer")
def profile():
    profile = InfluencerProfile.query.filter_by(user_id=current_user.id).first_or_404()
    categories = Category.query.order_by(Category.name).all()

    if request.method == "POST":
        profile.full_name = request.form.get("full_name", profile.full_name).strip()
        profile.category_id = int(request.form.get("category_id", profile.category_id))
        insta_input = request.form.get("instagram_handle", profile.instagram_handle).strip()
        profile.instagram_handle = parse_instagram_handle(insta_input)
        profile.instagram_url = instagram_profile_url(insta_input)
        profile.followers = normalize_stat(request.form.get("followers", profile.followers))
        profile.monthly_reach = normalize_stat(request.form.get("monthly_reach", profile.monthly_reach))
        try:
            profile.reel_pricing = float(request.form.get("reel_pricing", profile.reel_pricing))
            profile.story_pricing = float(request.form.get("story_pricing", profile.story_pricing))
            profile.post_pricing = float(request.form.get("post_pricing", profile.post_pricing))
        except ValueError:
            flash("Invalid pricing value.", "error")
            return render_template("influencer/profile.html", profile=profile, categories=categories)

        profile.bio = request.form.get("bio", "").strip()
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("influencer.dashboard"))

    return render_template("influencer/profile.html", profile=profile, categories=categories)
