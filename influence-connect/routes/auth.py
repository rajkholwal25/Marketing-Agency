from functools import wraps

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from extensions import db
from models import BrandProfile, Category, InfluencerProfile, User

auth_bp = __import__("flask").Blueprint("auth", __name__)


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)

        return wrapped

    return decorator


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(_dashboard_for_role(current_user.role))

    role = request.args.get("role", "brand")
    if role not in ("admin", "brand", "influencer"):
        role = "brand"

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", role)

        user = User.query.filter_by(email=email, role=role).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or _dashboard_for_role(user.role))

        flash("Invalid email or password for this role.", "error")

    return render_template("auth/login.html", role=role)


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(_dashboard_for_role(current_user.role))

    role = request.args.get("role", "brand")
    if role not in ("brand", "influencer"):
        role = "brand"

    categories = Category.query.order_by(Category.name).all()

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        role = request.form.get("role", role)

        if not email or not password:
            flash("Email and password are required.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        elif User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "error")
        elif role == "brand":
            company_name = request.form.get("company_name", "").strip()
            if not company_name:
                flash("Company name is required.", "error")
            else:
                user = User(email=email, role="brand")
                user.set_password(password)
                db.session.add(user)
                db.session.flush()
                profile = BrandProfile(
                    user_id=user.id,
                    company_name=company_name,
                    industry=request.form.get("industry", "").strip(),
                    website=request.form.get("website", "").strip(),
                    description=request.form.get("description", "").strip(),
                    contact_email=email,
                )
                db.session.add(profile)
                db.session.commit()
                login_user(user)
                flash("Welcome! Your brand account is ready.", "success")
                return redirect(url_for("brand.dashboard"))
        elif role == "influencer":
            full_name = request.form.get("full_name", "").strip()
            category_id = request.form.get("category_id")
            instagram = request.form.get("instagram_handle", "").strip().lstrip("@")
            pricing = request.form.get("monthly_pricing", "0")

            if not full_name or not category_id or not instagram:
                flash("Name, category, and Instagram handle are required.", "error")
            else:
                try:
                    pricing_val = float(pricing)
                except ValueError:
                    flash("Please enter a valid monthly price.", "error")
                else:
                    user = User(email=email, role="influencer")
                    user.set_password(password)
                    db.session.add(user)
                    db.session.flush()
                    profile = InfluencerProfile(
                        user_id=user.id,
                        full_name=full_name,
                        category_id=int(category_id),
                        instagram_handle=instagram,
                        followers=int(request.form.get("followers") or 0),
                        monthly_reach=int(request.form.get("monthly_reach") or 0),
                        monthly_pricing=pricing_val,
                        bio=request.form.get("bio", "").strip(),
                    )
                    db.session.add(profile)
                    db.session.commit()
                    login_user(user)
                    flash("Welcome! Your influencer profile is live.", "success")
                    return redirect(url_for("influencer.dashboard"))

    return render_template("auth/signup.html", role=role, categories=categories)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


def _dashboard_for_role(role: str) -> str:
    routes = {
        "admin": "admin.dashboard",
        "brand": "brand.dashboard",
        "influencer": "influencer.dashboard",
    }
    return url_for(routes.get(role, "main.index"))
