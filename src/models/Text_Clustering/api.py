# app/api.py
from fastapi import APIRouter
import json
from Text_cluster import VietnameseTextClustering

router = APIRouter()

# Khởi tạo class phân cụm
clustering_service = VietnameseTextClustering()

@router.on_event("startup")
async def startup_event():

    # Đọc file dữ liệu JSON để phân cụm khi server khởi động
    try:
        with open("../../../data/processed_data/processed_data_dash.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"Đã tải {len(data)} bài báo từ file JSON.")

            # Phân cụm dữ liệu khi khởi động
            clustering_service.fit_predict(data)
            print("Dữ liệu đã được phân cụm thành công!")

    except FileNotFoundError:
        print("File dữ liệu không tìm thấy, vui lòng tải lên file JSON đầu vào.")

@router.get("/get_samples")
async def get_samples(n_clusters: int = 5, k_sample: int = 3):
    # Trả về k sample từ mỗi cụm.
    samples = clustering_service.sample_clusters(n_clusters=n_clusters, k_nearest=k_sample)
    return {"clusters": samples}
