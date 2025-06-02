from flask import Flask, request, jsonify
from flask_cors import CORS
import random 
from utils import chunk_text, extract_text_from_pdf 
from sklearn.feature_extraction.text import TfidfVectorizer #vectorizer for all chunks
from sklearn.metrics.pairwise import cosine_similarity #to store our weights!
from gensim import corpora, models #to import LDA to get our topics
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
nltk.download("punkt")
nltk.download("stopwords")

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests


def generate_random_color():
    return "#" + ''.join(random.choices('0123456789ABCDEF', k=6))

vectorizer = TfidfVectorizer()

@app.route("/submit", methods=["POST"])
def receive_data():
    data = request.get_json()
    pdf = request.files['pdf']
    styles = data.get("styles", [])#append new styles for the clusters with random colors here
    nodes = data.get("nodes", [])#all nodes, add topics and nodes here
    similarity_matrix = data.get("similarities", [])#should be the matrix that we will use as new_similarity
    
    topics =[]#filter the nodes array for cluster types, then we get new topics.
    chunks = []

    if not similarity_matrix:

    tfidf_matrix = vectorizer.fit_transform(chunks)
    sim_matrix = cosine_similarity(tfidf_matrix)

    #  dictionary = corpora.Dictionary(tokenized_chunks)
    # corpus = [dictionary.doc2bow(text) for text in tokenized_chunks]

    # # LDA Model
    # lda_model = models.LdaModel(corpus, num_topics=5, id2word=dictionary, passes=10)

    # topic_distributions = []
    # for bow in corpus:
    #     topic_vector = lda_model.get_document_topics(bow, minimum_probability=0.0)
    #     vector = np.array([prob for _, prob in topic_vector])
    #     topic_distributions.append(vector.tolist())


# The nodes will represent a specific chunk of text, roughly around 100 (consecutive) words. A single PDF will have multiple nodes, A connection between nodes will represent a similarity score calculated through cosine similarity.

# For the sake of runtime, we will first find similar topics, then label a few nodes to those topics using LDA.

# The most closely aligned topic is where that current node will be. We will compare the generated topics and existing topics to see where that node will be located. Note that we will limit the topics generated to be 5 possible ones, but existing topics across all our PDFs will accumulate to a certain maximum.

# Then we will calculate using the cosine similarity score of every subsequent node to nodes existing in that topic.
# We will program a cutoff similarity score for these connections.

# For a draft, something like this will be similar to our end goal UI which uses the Regraph  reactJS graph library.

# Keep in mind that clusters=topic, and the nodes=pieces of text. 

# Note that the user builds their knowledge graph with subsequent PDFs they provide, and topics will be generated as a result.

# If it is efficient enough, We may also allow doing similarity between one node and all nodes in the 3 closest topics, so nodes will have a chance to connect to external clusters.

    return jsonify({
        "status": "received",
        "num_chunks": len(nodes),
        "similarity_matrix":  similarity_matrix[0][:3] if  similarity_matrix else [],
        "topics": topics[:3]
    })

if __name__ == "__main__":
    app.run(debug=True, port=5001)

def calculate_new_matrix():


def calculate_topics():