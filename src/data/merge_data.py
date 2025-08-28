import json
from datetime import datetime
import os

def normalize_date(date_str: str) -> str:
    if not date_str:
        return ""
    s = date_str.strip()

    if s.lower().startswith("thứ") or s.lower().startswith("chủ nhật"):
        s = s.split(",", 1)[1].strip()

    if "(" in s:
        s = s.split("(")[0].strip()

    for fmt in ["%Y-%m-%d %H:%M", "%d/%m/%Y - %H:%M", "%d/%m/%Y, %H:%M"]:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%d/%m/%Y - %H:%M")
        except ValueError:
            continue

    return date_str

if __name__ == "__main__":
    list_file = []
    raw_data_path = "data/raw_data"
    all_data = []
    keys = set()

    # Comment here
    for root, dirs, files in os.walk(raw_data_path):
        for file in files:
            if file.endswith(".json"):
                file = os.path.join(root, file)
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Comment here
                for item in data:
                    keys.update(item.keys())
                    if "metadata" in item:
                        keys.update(f"metadata.{x}" for x in item["metadata"].keys())

                all_data.extend(data)

    keys.remove("image-url")
    print(keys)

    # Comment here
    for item in all_data:
        for k in keys:
            # Comment here
            if k.startswith("metadata."):
                sub_k = k.split(".")[1]
                value = item["metadata"].get(sub_k, "")

                # Comment here
                if sub_k == "author" and type(value) == list:
                    value = value[0] if value else ""
                elif sub_k == "published_date":
                    value = normalize_date(value)

                item["metadata"][sub_k] = value

            # Comment here
            elif "image-url" in item:
                item["url_img"] = item.pop("image-url", "")
            # Comment here
            else:
                item[k] = item.get(k, "")

    # Merge and save all documents into a file
    with open("data/processed_data/merge_data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"Đã lưu {len(all_data)} bài báo vào merge_data.json")

