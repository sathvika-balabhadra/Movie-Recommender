# 🎬 Movie Recommender

A full-stack Movie Recommender built using machine learning and web technologies. It predicts user preferences and suggests movies based on content similarity and collaborative patterns. The system processes large datasets, cleans and transforms data, builds similarity models, and exposes recommendations through a web interface. Built with a Django + TypeScript + Tailwind CSS.

# Features

 1. **Content-Based Filtering**: Recommends movies using similarity scores computed from genres, overviews, and keywords.
 2. **Data Cleaning & Preprocessing**: Handles missing data, feature extraction, and vectorization for model readiness.
 3. **Machine Learning Integration**: Uses TF-IDF Vectorizer and cosine similarity to compute movie relationships.
 4. **Search Functionality**: Users can search for any movie and get personalized suggestions in real-time.
 5. **Web Interface**: Built using Django, providing a dynamic front end for interaction with the ML model.  

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

# How It Works

- The system loads movie data from the dataset (CSV).
- Uses TF-IDF Vectorization to represent movie descriptions numerically.
- Computes cosine similarity between movies.
- When a user inputs a movie title, the system finds the most similar movies based on their TF-IDF vectors.
- Recommendations are displayed through the Django web interface.

