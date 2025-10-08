import math
from collections import Counter
from movies.models import Movie, WatchHistory

def compute_tf(document_tokens) -> dict:
    tf_dict = {}
    total_terms = len(document_tokens)
    if total_terms == 0:
        return tf_dict

    term_counts = Counter(document_tokens)
    for term, count in term_counts.items():
        tf_dict[term] = count / total_terms
    return tf_dict

def compute_idf(documents_tokenized) -> dict:
    idf_dict = {}
    num_documents = len(documents_tokenized)

    term_in_documents_count = Counter()
    for doc_tokens in documents_tokenized:
        for term in set(doc_tokens):
            term_in_documents_count[term] += 1

    for term, count in term_in_documents_count.items():
        idf_dict[term] = math.log(num_documents / (count)) + 1
    return idf_dict

def compute_tfidf_vectors(documents_tokenized, idf_dict, all_terms_vocabulary) -> list:
    tfidf_vectors = []
    
    for doc_tokens in documents_tokenized:
        tf_dict = compute_tf(doc_tokens)
        tfidf_vector = {}
        for term in all_terms_vocabulary:
            tfidf_vector[term] = tf_dict.get(term, 0) * idf_dict.get(term, 0)
        tfidf_vectors.append(tfidf_vector)
    return tfidf_vectors

def cosine_similarity(vec1, vec2, all_terms_vocabulary) -> float | int:
    dot_product = 0
    norm_vec1 = 0
    norm_vec2 = 0

    for term in all_terms_vocabulary:
        val1 = vec1.get(term, 0)
        val2 = vec2.get(term, 0)
        
        dot_product += val1 * val2
        norm_vec1 += val1**2
        norm_vec2 += val2**2
    
    norm_vec1 = math.sqrt(norm_vec1)
    norm_vec2 = math.sqrt(norm_vec2)
    
    if norm_vec1 == 0 or norm_vec2 == 0:
        return 0
    
    return dot_product / (norm_vec1 * norm_vec2)


def get_similar_recommendation(movie_title, num_recommendations=7) -> list:

    all_movies = list(Movie.objects.all())
    if not all_movies:
        return []

    movie_data = []
    movie_id_to_index = {}
    index_to_movie = {}

    for i, movie in enumerate(all_movies):
        movie_data.append(movie.tags if movie.tags else '')
        movie_id_to_index[movie.id] = i
        index_to_movie[i] = movie

    idf_dict = compute_idf(movie_data)
    
    all_unique_terms = sorted(list(idf_dict.keys()))

    tfidf_vectors = compute_tfidf_vectors(movie_data, idf_dict, all_unique_terms)

    input_movie_obj = Movie.objects.filter(title__iexact=movie_title).first()
    if not input_movie_obj:
        return []

    input_movie_idx = movie_id_to_index[input_movie_obj.id]
    input_movie_vector = tfidf_vectors[input_movie_idx]

    similarity_scores = []
    for i, movie_vector in enumerate(tfidf_vectors):
        if i == input_movie_idx:
            continue
        
        sim_score = cosine_similarity(input_movie_vector, movie_vector, all_unique_terms)
        similarity_scores.append((i, sim_score))

    sorted_similar_movies = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    recommended_movies_list = []
    for i, _ in sorted_similar_movies[:num_recommendations]:
        recommended_movies_list.append(index_to_movie[i])

    return recommended_movies_list

def get_for_you_recommendation(user_obj, num_recommendations=7) -> list:

    all_movies = list(Movie.objects.all())
    if not all_movies or not list(WatchHistory.objects.filter(user=user_obj)):
        return []

    watched_movies_ids = set(
        WatchHistory.objects.filter(user=user_obj).values_list('movie_id', flat=True)
    )

    watched_movies_data = []
    unwatched_movies_data = []
    unwatched_movie_objects = []

    movie_id_to_index = {}
    for i, movie in enumerate(all_movies):
        movie_id_to_index[movie.id] = i
        if movie.id not in watched_movies_ids:
            unwatched_movies_data.append(movie.tags if movie.tags else '')
            unwatched_movie_objects.append(movie)
        else:
            watched_movies_data.append(movie.tags if movie.tags else '')

    if not unwatched_movies_data:
        return []

    user_profile_tags = " ".join(watched_movies_data)
    if not user_profile_tags.strip():
        return list(Movie.objects.exclude(id__in=watched_movies_ids).order_by('?')[:num_recommendations])


    all_corpus_tags = [user_profile_tags] + unwatched_movies_data
    
    idf_dict = compute_idf(all_corpus_tags)
    all_unique_terms = sorted(list(idf_dict.keys()))

    tfidf_vectors = compute_tfidf_vectors(all_corpus_tags, idf_dict, all_unique_terms)

    user_profile_vector = tfidf_vectors[0]

    similarity_scores = []
    for i, movie_vector in enumerate(tfidf_vectors[1:]):
        unwatched_movie_obj = unwatched_movie_objects[i]
        sim_score = cosine_similarity(user_profile_vector, movie_vector, all_unique_terms)
        similarity_scores.append((unwatched_movie_obj, sim_score))

    sorted_recommendations = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    
    recommended_movies_list = [movie_obj for movie_obj, score in sorted_recommendations[:num_recommendations]]

    return recommended_movies_list