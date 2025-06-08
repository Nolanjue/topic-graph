import io
import re
import PyPDF2# to parse the input pdf

from flask import Flask, request, jsonify
from flask_cors import CORS
import random 
from sklearn.feature_extraction.text import TfidfVectorizer #vectorizer for all chunks
from sklearn.metrics.pairwise import cosine_similarity #to store our weights!
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')

def extract_text_from_pdf(file):
    maxnumpages = 100
    reader = PyPDF2.PdfReader(file)
    text = ""
    pagecount = 0
    for page in reader.pages:
        text += page.extract_text() or ""
        pagecount = pagecount + 1
        if(pagecount > maxnumpages):
            break
    return text

def chunk_text(text, chunk_size=300):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, current = [], ""

    for sentence in sentences:
        filtered_sentence = remove_stop_words(sentence)
        if len(current) + len(filtered_sentence) < chunk_size:
            current += " " + filtered_sentence
        else:
            chunks.append(current.strip())
            current = filtered_sentence
    if current:
        chunks.append(current.strip())

    # Preprocess each chunk (inside this function as you suggested!)
    processed_chunks = []
    for chunk in chunks:
        tokens = word_tokenize(chunk.lower())
        tokens = [t for t in tokens if t.isalpha()]# and t not in STOPWORDS
        processed_chunks.append(" ".join(tokens))  # back to string for vectorizer

    return chunks, processed_chunks

def remove_stop_words(text):
    words = text.split()
    STOPWORDS = set(nltk.stopwords("english"))
    filtered_words = [word for word in words if word.lower() not in STOPWORDS]

    filtered_text = ' '.join(filtered_words)

    return filtered_text
    