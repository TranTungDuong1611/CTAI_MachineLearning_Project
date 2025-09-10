# viet tra ve file json
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import pickle
import os
import sys

HERE = os.path.dirname(__file__)                                  
SRC_ROOT = os.path.abspath(os.path.join(HERE, "../../"))        
if SRC_ROOT not in sys.path:
    sys.path.insert(0, SRC_ROOT)

from models.Text_Classification import inference as classification
from models.Text_summarization import infer as summarization


app = Flask(__name__)
CORS(app)

app.config["JSON_AS_ASCII"] = False  

# MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
#                                          "../../../results/models/Text_Classification"))

@app.post("/classification")
def classification_get():
    data = request.get_json(silent=True) or {}
    text = data.get("text")
    if not text:
        return jsonify({"error": "Missing 'text' in JSON body"}), 400
    try:
        return jsonify(classification.predict_one(text)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.post("/summarize")
def summarize_post():
    data = request.get_json(silent=True) or {}
    text = data.get("text")
    if not text:
        return jsonify({"error": "Missing 'text' in JSON body"}), 400

    in_max_len  = int(data.get("in_max_len", 512))
    out_max_len = int(data.get("out_max_len", 128))
    beams       = int(data.get("beams", 2)) # Nên để beams =2
    nrng        = int(data.get("nrng", 3))
    do_sample   = bool(data.get("sample", False))
    temp        = float(data.get("temp", 1.0))

    try:
        summary = summarization.summarize_one(
            text,
            in_max_len=in_max_len,
            out_max_len=out_max_len,
            num_beams=beams,
            no_repeat_ngram_size=nrng,
            do_sample=do_sample,
            temperature=temp,
        )
        return jsonify({"text": text, "summary": summary}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

