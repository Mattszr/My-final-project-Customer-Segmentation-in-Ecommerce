# store/services/recommender.py

import os
import pickle

# Model loading function
def load_model(directory="store/recommender/models"):
    model_path = os.path.join(directory, "ecommerce_recommendation_model.pkl")
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)
    return model_data['kmeans'], model_data['scaler']

# Category suggestion function for the user
def recommend_categories_for_user(view, cart, purchase, favorite_category, top_n=7):

    kmeans, scaler = load_model()

    # Standardize user input
    import pandas as pd
    user_input = pd.DataFrame([[view, cart, purchase]], columns=scaler.feature_names_in_)
    user_input_scaled = scaler.transform(user_input)

    # Predict the cluster the user belongs to
    cluster = kmeans.predict(user_input)[0]

    #cluster-based categories
    cluster_to_categories = {
        0: ['Electronics', 'Home&Living', 'Fashion'],
        1: ['Sports&Outdoor', 'Toys&Hobbies', 'Electronics'],
        2: ['Health&Personal Care', 'Books&Stationery', 'Fashion'],
        3: ['Home&Living', 'Sports&Outdoor', 'Health&Personal Care'],
        4: ['Toys&Hobbies', 'Fashion', 'Electronics']
    }

    recommended_categories = cluster_to_categories.get(cluster, [])

    if favorite_category and favorite_category not in recommended_categories:
        recommended_categories.insert(0, favorite_category)

    # List without repetition
    seen = set()
    unique_categories = []
    for cat in recommended_categories:
        if cat not in seen:
            unique_categories.append(cat)
            seen.add(cat)
        if len(unique_categories) == top_n:
            break

    global_popular_categories = ['Electronics', 'Home&Living', 'Fashion', 'Sports&Outdoor', 'Toys&Hobbies', 'Health&Personal Care', 'Books&Stationery']
    for cat in global_popular_categories:
        if len(unique_categories) == top_n:
            break
        if cat not in seen:
            unique_categories.append(cat)
            seen.add(cat)

    return unique_categories
