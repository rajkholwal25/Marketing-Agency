# Influence Connect

A Flask web app connecting **Brands** with **Influencers** — browse by category, view stats, pricing, and contact details.

## Quick Start

```bash
cd influence-connect
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python run.py
```

Open **http://127.0.0.1:5000**

## Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@influence.com | admin123 |
| Brand | brand@demo.com | demo123 |
| Influencer | kavya_glam@demo.com | demo123 |

## Features

- **3 login types:** Admin, Brand, Influencer
- **Brand dashboard:** Category icons (Sports, Study, Makeup, etc.) → influencer cards
- **Influencer cards:** Instagram, followers, monthly reach, email, monthly pricing
- **Influencer signup:** Set category, stats, and monthly rate
- **Influencer dashboard:** Browse all registered brands
- **Admin panel:** Manage users & add categories
- **Modern UI:** Dark theme, gradients, animations, glassmorphism

## Tech Stack

- Python Flask
- Flask-Login (auth)
- Flask-SQLAlchemy (SQLite)
- HTML/CSS/JS (custom animated UI)
