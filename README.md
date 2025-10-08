# 🎬 Movie Recommender

A full-stack Movie Recommender built using machine learning and web technologies. It predicts user preferences and suggests movies based on content similarity and collaborative patterns. The system processes large datasets, cleans and transforms data, builds similarity models, and exposes recommendations through a web interface. Built with a Django + TypeScript + Tailwind CSS.

# Features

Content-Based Filtering: Recommends movies using similarity scores computed from genres, overviews, and keywords.
Data Cleaning & Preprocessing: Handles missing data, feature extraction, and vectorization for model readiness.
Machine Learning Integration: Uses TF-IDF Vectorizer and cosine similarity to compute movie relationships.
Search Functionality: Users can search for any movie and get personalized suggestions in real-time.
Web Interface: Built using Django, providing a dynamic front end for interaction with the ML model.

# Tech Stack

- Python
- Django
- pandas
- numpy
- HTML
- JavaScript
- TypeScript
- scikit-learn
- Tailwind CSS
- PostgreSQL
- Machine Learning

---

##  Features

### User Features
- Browse and search for movies
- Like and view history-based recommendations
- Movie detail pages with genre, language, cast, and descriptions

### Admin Features
- Add, update, and delete movies, genres, and languages
- View movie popularity based on user interactions

### Recommendation System
- Content-based filtering using cosine similarity
- Popularity-based sorting (recent views & likes)

---

##  Installation

## Prerequisites
- Python >=3.12
- Node.js and npm

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/sathvika-balabhadra/movie_recommender.git
   cd movie_recommender
2. Create and activate virtual environment

    You can choose either pip or uv for installing dependencies:
    
    Option 1: Using pip
    ```bash
    # Create virtual environment
    # macOS/Linux:
    python3 -m venv venv
    # Windows:
    py -m venv venv

    # Activate the environment
    # macOS/Linux:
    source .venv/bin/activate
    # Windows:
    venv\Scripts\activate

    # Install dependencies
    pip install -r requirements.txt
    ```

    Option 2: Using uv (Faster alternative)
    ```bash
    # Install uv (if not installed)
    pip install uv

    # Create and activate environment
    uv venv venv
    source venv/bin/activate   # macOS/Linux
    venv/Scripts/activate      # Windows

    # Install using uv
    uv sync
    ```
3. Run migrations and create superuser
    ```bash
    # macOS/Linux:
    python3 manage.py migrate
    python3 manage.py createsuperuser
    # Windows:
    py manage.py migrate
    py manage.py createsuperuser
    ```
4. Start the server
    ```bash
    # macOS/Linux:
    python3 manage.py runserver
    # Windows:
    py manage.py runserver
    ```
5. Install Tailwind CSS
    ```bash
    npm install
    ```
6. Start the Tailwind CLI build process
    ```bash
    npm run watch:css
    ```
7. Install TypeScript(Optional)
    ```bash
    # install TypeScript
    npm install -g typescript
    # compile TypeScript
    tsc --watch
    ```
----
# How It Works

- The system loads movie data from the dataset (CSV).
- Uses TF-IDF Vectorization to represent movie descriptions numerically.
- Computes cosine similarity between movies.
- When a user inputs a movie title, the system finds the most similar movies based on their TF-IDF vectors.
- Recommendations are displayed through the Django web interface.

