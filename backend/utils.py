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

#i fucking hate stopwords
#STOPWORDS = set(stopwords.words("english"))
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def chunk_text(text, chunk_size=300):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, current = [], ""
    for sentence in sentences:
        if len(current) + len(sentence) < chunk_size:
            current += " " + sentence
        else:
            chunks.append(current.strip())
            current = sentence
    if current:
        chunks.append(current.strip())

    # Preprocess each chunk (inside this function as you suggested!)
    processed_chunks = []
    for chunk in chunks:
        tokens = word_tokenize(chunk.lower())
        tokens = [t for t in tokens if t.isalpha()]# and t not in STOPWORDS
        processed_chunks.append(" ".join(tokens))  # back to string for vectorizer

    return chunks, processed_chunks