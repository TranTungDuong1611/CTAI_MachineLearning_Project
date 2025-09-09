import json
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
import re
import hdbscan
from sklearn.metrics.pairwise import cosine_distances
import joblib
import numpy as np
import pandas as pd


# Loại bỏ kí tự chữ số
def remove_numbers(text):
    return re.sub(r'\d+', '', text)

# Hàm tìm số cụm tốt nhất dựa trên silhouette score
def find_best_k(embeddings, candidate_k):
    scores = {}
    for k in candidate_k:
        km = KMeans(n_clusters=k, n_init="auto", random_state=42)
        labels_tmp = km.fit_predict(embeddings)

        # Tính toán silhouette score
        sil = silhouette_score(embeddings, labels_tmp, metric="cosine")
        scores[k] = sil
        print(f"Số cụm: {k}, silhouette score: {sil:.4f}")

    best_k = max(scores, key=scores.get)
    return best_k, scores

# Hàm tính toán MSE
def compute_mse(embeddings, labels):
    mse_list = []
    for cl in np.unique(labels):
        if cl == -1:
            continue

        # Tìm các điểm thuộc cụm cl
        idx = np.where(labels == cl)[0]
        if len(idx) == 0:
            continue

        # Tính MSE cho cụm cl
        cluster_points = embeddings[idx]
        centroid = np.mean(cluster_points, axis=0)
        sq_dists = np.sum((cluster_points - centroid) ** 2, axis=1)

        mse = np.mean(sq_dists)
        mse_list.append(mse)
        print(f"Cụm {cl}: MSE={mse:.4f}, số văn bản={len(idx)}")

    # Tính MSE trung bình trên tất cả các cụm
    if mse_list:
        avg_mse = np.mean(mse_list)
        print("MSE trung bình =", avg_mse)
        return avg_mse
    else:
        print("Không có cụm nào (toàn noise)")
        return None


class VietnameseTextClustering:
    def __init__(self, ):
        self.embedding_method = SentenceTransformer('intfloat/multilingual-e5-large-instruct')
        self.vectorizer = None
        # self.clustering_model = None
    
    # Loại bỏ số khỏi văn bản
    def process_texts(self, texts):
        processed_texts = [remove_numbers(text) for text in texts]
        return processed_texts
    
    # Embedding văn bản
    def vectorize(self, texts):
        embeddings = self.embedding_method.encode(
            texts,
            batch_size=4,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True  # chuẩn hoá L2 -> phù hợp cosine
            )
        return embeddings

    def cluster(self, embeddings, method='kmeans'):
        # Tìm số cụm tối ưu
        candidate_k = range(8, 20)
        optimal_k, _ = find_best_k(embeddings, candidate_k)
        print("Số cụm tối ưu:", optimal_k)

        # Phân cụm K-means
        if method == 'kmeans':
            kmeans = KMeans(
                n_clusters=optimal_k,
                random_state=42,
                n_init="auto"
            )
            labels = kmeans.fit_predict(embeddings)

        elif method == 'hdbscan':
            cosine_distance_matrix = cosine_distances(embeddings).astype(np.float64)
            hdbscan = hdbscan.HDBSCAN(min_cluster_size=5, metric='precomputed')
            labels = hdbscan.fit_predict(cosine_distance_matrix)

        elif method == 'hierarchical':
            hierarchial = AgglomerativeClustering(n_clusters=optimal_k, metric="euclidean", linkage="ward")
            labels = hierarchial.fit_predict(embeddings)

        return labels
    
    def fit_predict(self, texts):
        processed_texts = self.process_texts(texts)
        vectors = self.vectorize(processed_texts)
        labels = self.cluster(vectors)
        
        # Đánh giá
        metrics = compute_mse(vectors, labels)
        
        return labels, metrics
    
