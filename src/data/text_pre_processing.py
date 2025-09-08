import argparse
import os
import json
import pandas as pd
import re 
from underthesea import word_tokenize
from tqdm import tqdm

# Load config file
with open('config.json', 'r') as f:
    config = json.load(f)


def validate_text(text, min_len, max_len=None):
    n = len(text.strip().split())
    if n < min_len or (max_len and n > max_len):
        return False, n
    return True, n


def remove_stop_words(args, text):
    if args.dash:
        stop_words_path = config["DATA"]["STOP_WORDS_DASH"]
    else:
        stop_words_path = config["DATA"]["STOP_WORDS"]

    with open(stop_words_path, 'r', encoding="utf-8") as f:
        stopwords = f.readlines()
        stop_set = list(set(m.strip() for m in stopwords))
    tmp = text.split(' ')
    for stop_word in stop_set:
        if stop_word in tmp:
            tmp.remove(stop_word)
    results = " ".join(tmp)
    return results


def preprocess_text(args, text):
    if not isinstance(text, str):
        return ""
    
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", " ", text)         # bỏ URL
    text = re.sub(r"[\n\r\t]", " ", text)  
    text = re.sub(r"[,!?;:()\[\]{}\"'’“”]", " ", text)  # bỏ dấu câu
    text = re.sub(r"\s+", " ", text).strip()            # bỏ dấu cách thừa
    text = re.sub(r"[\/]", " ", text)
    tokens = word_tokenize(text, format="text")         # tách từ
    tokens = remove_stop_words(args, tokens)     
    # tokens = re.sub(r"[\n\r\t]", " ", tokens)         
    return tokens


def mapping_category(df):
    # Open file mapping
    with open(config["DATA"]["MAPPING_CATEGORIES"], 'r') as file:
        cat_dict = json.load(file)

    list_cats = [cat.lower() for cat in set(cat_dict.keys())]

    # Keep only rows where metadata["cat"] is in cat_dict
    df = df[df["metadata"].apply(lambda meta: meta["cat"].lower() in list_cats)].copy()

    # Map categories
    df["metadata"] = df["metadata"].apply(lambda meta: {**meta, "cat": cat_dict[meta["cat"].lower()]})
    
    return df


def run(args, file):
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)

    print(f"[INFO] Đã tải {len(df)} bài báo từ {file}")

    # 1. Check the validation of documents
    invalid_titles, invalid_desc, invalid_content = [], [], []

    for i, row in tqdm(df.iterrows()):
        valid, n = validate_text(row["title"], 4, 50)
        if not valid:
            invalid_titles.append({"url": row["url"], "title": row["title"], "num_words": n})

        valid, n = validate_text(row["description"], 18, 100)
        if not valid:
            invalid_desc.append({"url": row["url"], "desc_len": n})

        valid, n = validate_text(row["content"], 170, None)
        if not valid:
            invalid_content.append({"url": row["url"], "content_len": n})

        invalid_data = pd.DataFrame(invalid_titles + invalid_desc + invalid_content)
        
    invalid_title_urls = [item["url"] for item in invalid_titles]
    invalid_desc_urls = [item["url"] for item in invalid_desc]
    invalid_content_urls = [item["url"] for item in invalid_content]

    invalid_urls = set(invalid_title_urls + invalid_desc_urls + invalid_content_urls)
    df = df[~df["url"].isin(invalid_urls)].reset_index(drop=True)

    # 2. Mapping metadata
    df = mapping_category(df)
    
    # 3. Preprocessing
    df["title_clean"] = df["title"].apply(lambda x: preprocess_text(args, x))
    df["desc_clean"]  = df["description"].apply(lambda x: preprocess_text(args, x))
    df["content_clean"] = df["content"].apply(lambda x: preprocess_text(args, x))

    return df, invalid_data


def main(args):
    data_path = args.input

    # Process data
    data, invalid_data = run(args, data_path)
    print(f"Số bài báo không hợp lệ {len(invalid_data)}")

    # Save the invalid data
    with open("data/processed_data/invalid_data.json", "w", encoding="utf-8") as f:
        json.dump(invalid_data.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

    # Save the valid data
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data.to_dict(orient="records"), f, ensure_ascii=False, indent=2)
        print(f"[INFO] Đã lưu {len(data)} bài báo vào file {args.output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Xử lý văn bản")
    parser.add_argument("--input", type=str, required=True, help="Đường dẫn tới file JSON")
    parser.add_argument("--dash", action="store_true", help="Sử dụng stopwords dạng gạch dưới")
    parser.add_argument("--output", type=str, help="Đường dẫn tới file xuất kết quả")
    args = parser.parse_args()

    main(args)
