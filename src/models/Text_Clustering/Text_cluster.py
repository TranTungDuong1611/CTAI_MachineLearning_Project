import json
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from sentence_transformers import SentenceTransformer
import re
import os
import sys
import hdbscan
from sklearn.metrics.pairwise import cosine_distances
import numpy as np
import pandas as pd

sys.path.append(os.getcwd())

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
    def __init__(self):
        # Load data but don't run clustering yet
        with open("data/processed_data/processed_data_dash.json", "r", encoding="utf-8") as f:
            self.data = json.load(f)
            print(f"Đã tải {len(self.data)} bài báo từ file JSON.")

        self.embedding_method = None  # Lazy load this too
        self.vectors = None
        self.labels = None
        self.texts = None
        self.metadata = None

        # Pre compute the clusters
        self.fit_predict(self.data, method='kmeans')

    def _get_embedding_method(self):
        """Lazy load the embedding model"""
        if self.embedding_method is None:
            print("Loading SentenceTransformer model...")
            self.embedding_method = SentenceTransformer('intfloat/multilingual-e5-large-instruct')
        return self.embedding_method

    def process_texts(self, texts):
        """Loại bỏ số khỏi văn bản."""
        return [remove_numbers(text) for text in texts]

    def vectorize(self, texts):
        """Tạo embedding cho danh sách văn bản."""
        embedding_method = self._get_embedding_method()
        vectors = embedding_method.encode(
            texts,
            batch_size=16,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return vectors

    def cluster(self, method='kmeans'):
        # Tìm số cụm tối ưu
        candidate_k = range(8, 20)
        optimal_k, _ = find_best_k(self.vectors, candidate_k)
        print("Số cụm tối ưu:", optimal_k)

        # Phân cụm với KMeans, HDBSCAN hoặc Hierarchical
        if method == 'kmeans':
            model = KMeans(
                n_clusters=optimal_k,
                random_state=42,
                n_init="auto"
            )
            labels = model.fit_predict(self.vectors)

        elif method == 'hdbscan':
            cosine_distance_matrix = cosine_distances(self.vectors).astype(np.float64)
            hdbscan_model = hdbscan.HDBSCAN(min_cluster_size=5, metric='precomputed')
            labels = hdbscan_model.fit_predict(cosine_distance_matrix)

        elif method == 'hierarchical':
            hierarchial = AgglomerativeClustering(n_clusters=optimal_k, metric="euclidean", linkage="ward")
            labels = hierarchial.fit_predict(self.vectors)

        else:
            raise ValueError(f"Phương pháp phân cụm '{method}' không được hỗ trợ.")

        return labels

    def fit_predict(self, data, method='kmeans'):
        
        # Nhận dữ liệu JSON, chỉ lấy content_clean để phân cụm.

        self.texts = [item["content_clean"] for item in data]
        self.metadata = data  # Lưu lại toàn bộ metadata
        self.vectors = self.vectorize(self.texts)
        self.labels = self.cluster(method)
        return self.labels

    def sample_clusters(self, n_clusters=3, k_nearest=5, random_state=42):
        """Trả về toàn bộ thông tin bài báo trong các cụm đã phân
            Lấy k bài gần tâm nhất."""
        # Chọn ngẫu nhiên n cụm
        rng = np.random.default_rng(random_state)
        unique_clusters = [c for c in np.unique(self.labels) if c != -1]
        chosen_clusters = rng.choice(unique_clusters, size=min(n_clusters, len(unique_clusters)), replace=False)

        # Lấy k bài gần centroid nhất từ mỗi cụm
        results = []
        for cluster_id in chosen_clusters:
            indices = np.where(self.labels == cluster_id)[0]
            cluster_vectors = self.vectors[indices]

            # Tính khoảng cách đến centroid
            centroid = np.mean(cluster_vectors, axis=0)
            distances = cosine_distances(cluster_vectors, centroid.reshape(1, -1)).ravel()

            nearest_indices = indices[np.argsort(distances)[:k_nearest]]

            # Trả về toàn bộ thông tin bài báo cho những bài được chọn
            for idx in nearest_indices:
                article_info = self.metadata[idx]  
                article_info["cluster_id"] = int(cluster_id)
                results.append(article_info)

        return results

if __name__ == "__main__":
    clustering_service = VietnameseTextClustering()
    # Load data
    with open("data/processed_data/processed_data_dash.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        texts = [item['content'] for item in data if 'content' in item]
    
    samples = clustering_service.sample_clusters(n_clusters=5, k_nearest=3)
    print("Mẫu từ các cụm:", samples)
