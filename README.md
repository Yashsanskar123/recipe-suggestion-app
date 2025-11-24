A FastAPI-based web app that helps users search, compare, and explore recipes using TheMealDB API.
🚀 Features
🔍 Search recipes by name or ingredient
🚫 Exclude ingredients you don’t want
⚖️ Compare two recipes
📄 Detailed recipe view (ingredients, instructions, match score)
⭐ Recommendations based on your available ingredients
🧹 Clean ingredient extraction from messy TheMealDB JSON


🏗️ Tech Stack

FastAPI
Jinja2 Templates
Bootstrap 5
TheMealDB API
Python Requests

▶️ Run Locally
git clone https://github.com/Yashsanskar123/recipe-suggestion-app.git
cd recipe-suggestion-app
pip install -r requirements.txt
uvicorn main:app --reload


Open in browser:
http://127.0.0.1:8000/ui/search

📡 Key Endpoints

/search — Search recipes
/exclude — Exclude ingredients
/recipe/{id} — Recipe details
/compare — Compare recipes
/recommend — Recommended dishes

📁 Project Structure (Short)
main.py
templates/
static/
utils/
