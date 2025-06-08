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

#chunks the text into chunks of roughly 300 words
def chunk_text(text, chunk_size=300):
    filtered_text = remove_stop_words(text)
    words = filtered_text.split()
    chunks, current = [], ""

    wordcount = 0
    for word in words:
        if(wordcount < chunk_size):
            current += ' ' + word
            wordcount += 1
        else:
            chunks.append(current.strip())
            current = word
            wordcount = 1

    #the cutoff of the final chunk is 100, since a very small chunk could mess up LDA
    if wordcount > 100:
        chunks.append(current.strip())

    return chunks

def remove_stop_words(text):
    words = text.split()
    STOPWORDS = set(stopwords.words("english"))
    filtered_words = [word.lower() for word in words if word.lower() not in STOPWORDS and word.isalpha()]#remove all english stopwords, and all non-alphabetic characters
    #also sets all words to lowercase
    filtered_text = ' '.join(filtered_words)

    return filtered_text
    