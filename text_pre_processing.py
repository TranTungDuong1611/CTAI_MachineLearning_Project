import argparse
import os
import json
import pandas as pd
import re 
from underthesea import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

def validate_text(text, min_len, max_len=None):
    n = len(text.split())
    if n < min_len or (max_len and n > max_len):
        return False, n
    return True, n

def remove_stop_words(args, text):
    with open(args.stop_words, 'r', encoding="utf-8") as f:
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
    if args.dash:
        text = remove_stop_words(args, text)               
        tokens = word_tokenize(text, format="text")         # tách từ
    else:
        tokens = word_tokenize(text, format="text")         # tách từ
        tokens = remove_stop_words(args, tokens)     
    # tokens = re.sub(r"[\n\r\t]", " ", tokens)         
    return tokens

def run(args, file):
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)

    print(f"[INFO] Đã tải {len(df)} bài báo từ {file}")

    # 1. Kiểm tra tính hợp lệ
    invalid_titles, invalid_desc, invalid_content = [], [], []

    for i, row in df.iterrows():
        valid, n = validate_text(row["title"], 10, 30)
        if not valid:
            invalid_titles.append({"url": row["url"], "title": row["title"], "num_words": n})

        valid, n = validate_text(row["description"], 20, 100)
        if not valid:
            invalid_desc.append({"url": row["url"], "desc_len": n})

        valid, n = validate_text(row["content"], 200, None)
        if not valid:
            invalid_content.append({"url": row["url"], "content_len": n})

        # print("\n--- INVALID TITLES ---")
        # print(pd.DataFrame(invalid_titles))

        # print("\n--- INVALID DESCRIPTIONS ---")
        # print(pd.DataFrame(invalid_desc))

        # print("\n--- INVALID CONTENT ---")
        # print(pd.DataFrame(invalid_content))

        invalid_data = pd.DataFrame(invalid_titles + invalid_desc + invalid_content)
        # invalid_data.to_json("invalid_data.json", orient="records", lines=True, force_ascii=False)
    invalid_title_urls = [item["url"] for item in invalid_titles]
    invalid_desc_urls = [item["url"] for item in invalid_desc]
    invalid_content_urls = [item["url"] for item in invalid_content]

    invalid_urls = set(invalid_title_urls + invalid_desc_urls + invalid_content_urls)
    df = df[~df["url"].isin(invalid_urls)].reset_index(drop=True)
# 2. Tiền xử lý
    df["title_clean"] = df["title"].apply(lambda x: preprocess_text(args, x))
    df["desc_clean"]  = df["description"].apply(lambda x: preprocess_text(args, x))
    df["content_clean"] = df["content"].apply(lambda x: preprocess_text(args, x))
    # print(df.head())
    return df, invalid_data
def main(args):
    data_path = args.input
    list_web = os.listdir(data_path)
    data = pd.DataFrame()
    invalid_data = pd.DataFrame()
    for web in list_web:
        web_path = os.path.join(data_path, web)
        files = os.listdir(web_path)
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(web_path, file)
                print(f"[INFO] Đang xử lý file {file_path}")
                df, invalid = run(args, file_path)
                data = pd.concat([data, df], ignore_index=True)
                invalid_data = pd.concat([invalid_data, invalid], ignore_index=True)
    print(f"Số bài báo không hợp lệ {len(invalid_data)}")
    with open("invalid_data.json", "w", encoding="utf-8") as f:
        json.dump(invalid_data.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data.to_dict(orient="records"), f, ensure_ascii=False, indent=2)
        print(f"[INFO] Đã lưu {len(data)} bài báo vào file {args.output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Xử lý văn bản")
    parser.add_argument("--input", type=str, required=True, help="Đường dẫn tới file JSON")
    parser.add_argument("--dash", action="store_true", help="Sử dụng stopwords dạng gạch dưới")
    parser.add_argument("--stop_words", type=str, default="vietnamese-stopwords.txt", help="Đường dẫn tới file stopwords")
    parser.add_argument("--output", type=str, help="Đường dẫn tới file xuất kết quả")
    args = parser.parse_args()

    main(args)
