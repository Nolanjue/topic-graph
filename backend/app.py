from flask import Flask, request, jsonify
from flask_cors import CORS
import random 
from utils import chunk_text, extract_text_from_pdf 
from sklearn.feature_extraction.text import TfidfVectorizer #vectorizer for all chunks
from sklearn.metrics.pairwise import cosine_similarity #to store our weights!
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
 #to import LDA to get our topics
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize




app = Flask(__name__)
CORS(app)  # Allow cross-origin requests


def generate_random_color():
    return "#" + ''.join(random.choices('0123456789ABCDEF', k=6))

vectorizer = TfidfVectorizer()
@app.route("/", methods=["GET"])
def cool_data():
    return jsonify("hello")



@app.route("/submit", methods=["POST"])
def receive_data():
    data = request.get_json()
    #all the code here for the request we send
    pdf = request.files.get('pdf')
    styles = data.get("styles", [])#append new styles for the clusters with random colors here(clusters = topic)
    elements = data.get("elements", [])#all nodes, add topics and nodes here, so each node must have a topic inside of it()
    


    topics = data.get("topics", [])#all unique topics(append with LDA) for nodes
    similarity_list = data.get("similarities", [])
    #should be a list of all similaritry data we should maintain as easy access
    
    topics =[]#filter the nodes array for cluster types, then we get new topics.
    chunks = []


   #and then get more chunks here
#     chunks = [
#         "Water market mechanisms are approaches that treat water as a commodity and that can be used to transfer water among users, reallocating water-using price.1 Because they are voluntary and have the potential to move water efficiently, water market mechanisms are viewed in policy discussions as one possible approach for more effectively managing water resources. This is the topic of our research.",
#         "Organic farming has been one of the fastest growing markets in agriculture during the last twenty years. It combines both tradition and science to produce crops and livestock that flourish in the absence of synthetic pesticides, herbicides, and hormones. However, many environmental scientists view the term 'organic' as a form of greenwashing and unsubstantive bias.",
#         "In an especially prescient piece about the future course of the public health challenge, CSIS’s J. Stephen Morrison and Anna Carroll observed, Pandemics change history by transforming populations, states, societies, economies, norms, and governing structures. For example, the Black Death killed roughly a ton of  adults in Europe, resulting in rising wages and rights for the peasant class.",
#         "The virus infected the human population at a historic transition in its demographic structure. This year, for the first time ever, the number of people aged 60 years or older outnumbers people 5 years old or younger worldwide, with aging populations concentrated most heavily in high-income countries. Unfortunately, the virus is uniquely dangerous to this growing elderly cohort.",
#         "The areas utilized are variable in size and location, but each is chosen so that the local rainfall may be reinforced by the overflow of water derived from higher ground. The selection of a field involves an intimate knowledge of local conditions. The field must be flooded, but the sheet of water must not attain such velocity as to wash out the crop, nor bury the plants in detritus."
# ]
    new_chunks = [
   
]


    all_chunks = chunks+ new_chunks

# The nodes will represent a specific chunk of text, roughly around 100 (consecutive) words. A single PDF will have multiple nodes, A connection between nodes will represent a similarity score calculated through cosine similarity.

# For the sake of runtime, we will first find similar topics, then label a few nodes to those topics using LDA.

# The most closely aligned topic is where that current node will be. We will compare the generated topics and existing topics to see where that node will be located. Note that we will limit the topics generated to be 5 possible ones, but existing topics across all our PDFs will accumulate to a certain maximum.

# Then we will calculate using the cosine similarity score of every subsequent node to nodes existing in that topic.
# We will program a cutoff similarity score for these connections.

# For a draft, something like this will be similar to our end goal UI which uses the Regraph  reactJS graph library.

# Keep in mind that clusters=topic, and the nodes=pieces of text. 

# Note that the user builds their knowledge graph with subsequent PDFs they provide, and topics will be generated as a result.

# If it is efficient enough, We may also allow doing similarity between one node and all nodes in the 3 closest topics, so nodes will have a chance to connect to external clusters.

#all we need is to force the topic generation only for chunks, but we need existing chunks with current chunks for it work
    
    print(calculate_new_matrix(all_chunks, len(chunks)))#return the last index first to ensure we have all the nodes
    new_matrix = calculate_new_matrix(all_chunks,len(chunks))
    similarity_list.append(new_matrix)
    #handle adding to elements here as edges:
    #  { data: { id: "ab", source: "a", target: "b", label: "0.85" } },
    #and style:
    
    print(calculate_topics(all_chunks, topics))
    #handle adding to elements of the node and the topic as such:
    # { data: { id: "a", label: "Node A", parent: "cluster1" }, position: getRandomPosition() },
    #and style:
    topics = calculate_topics(all_chunks, topics)
    return jsonify({
        "status": "received",
        "styles":styles,
        "elements":elements,
        "similarity": similarity_list,
        "topics": topics
    })

if __name__ == "__main__":
    app.run(debug=True, port=5001)



def calculate_new_matrix(all_chunks: list[str], M: int):
    vectorizer = TfidfVectorizer()
    vectorizer.fit(all_chunks)

    all_vectors = vectorizer.transform(all_chunks)
    all_vectors = normalize(all_vectors, axis=1)

    # 🔧 Convert sparse matrix to dense float32 array for FAISS
    all_vectors = all_vectors.toarray().astype('float32')

    index = faiss.IndexFlatIP(all_vectors.shape[1])
    index.add(all_vectors)

    top_k = 3
    threshold = 0.3

    # Only search from M to end
    new_vectors = all_vectors[M:]  
    distances, indices = index.search(new_vectors, top_k + 1)

    neighbors_dict = {}

    for i in range(M, len(all_chunks)):
        local_i = i - M  # local row in search result
        neighbor_indices = indices[local_i]
        neighbor_sims = distances[local_i]

        #Remove self and apply threshold
        filtered = [
            (idx, sim) for idx, sim in zip(neighbor_indices, neighbor_sims)
            if idx != i and sim > threshold
        ]

        #Sort by similarity and take top_k
        filtered.sort(key=lambda x: x[1], reverse=True)
        top_neighbors = filtered[:top_k]
        neighbors_dict[i] = top_neighbors

        print(f"Top neighbors for new chunk (global idx {i}):")
        for neighbor_idx, sim_score in top_neighbors:
            chunk_type = "existing" if neighbor_idx < M else "new"
            chunk_id = neighbor_idx if chunk_type == "existing" else neighbor_idx - M
            print(f"  Neighbor {chunk_type} chunk {chunk_id} with similarity {sim_score:.4f}")

    return neighbors_dict




def calculate_topics(chunks: list[str], seed_word_lists: list[list[str]]):

    existing_topic_count = len(seed_word_lists)
    max_extra_topics = 5
    n_topics = existing_topic_count + max_extra_topics

    # Vectorize input text chunks
    vectorizer = CountVectorizer(stop_words='english')
    X = vectorizer.fit_transform(chunks)
    vocab = vectorizer.get_feature_names_out()

    # Fit sklearn LDA model with n_topics
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42, max_iter=100)
    lda.fit(X)

    # Extract top words per topic (top 5 words)
    topic_keywords = []
    for topic_idx, topic_dist in enumerate(lda.components_):
        top_words_idx = topic_dist.argsort()[-5:][::-1]
        top_words = [vocab[i] for i in top_words_idx]
        topic_keywords.append(top_words)

    print("Topic Keywords per topic:")
    for idx, words in enumerate(topic_keywords):
        print(f"Topic {idx}: {words}")

    # Assign topics to chunks/documents
    doc_topic_dist = lda.transform(X)  # shape (num_docs, n_topics)
    # assigned_topics = doc_topic_dist.argmax(axis=1)

    # print("\nAssigned topic per chunk:")
    # for i, topic_idx in enumerate(assigned_topics):
    #     print(f"Chunk {i} assigned to Topic {topic_idx}")

    return  topic_keywords

