# # from sklearn.feature_extraction.text import CountVectorizer
# # from sklearn.decomposition import LatentDirichletAllocation
# # from utils import chunk_text, extract_text_from_pdf 


# # chunks = [
# #         "Water market mechanisms are approaches that treat water as a commodity and that can be used to transfer water among users, reallocating water-using price.1 Because they are voluntary and have the potential to move water efficiently, water market mechanisms are viewed in policy discussions as one possible approach for more effectively managing water resources. This is the topic of our research.",
# #         "Organic farming has been one of the fastest growing markets in agriculture during the last twenty years. It combines both tradition and science to produce crops and livestock that flourish in the absence of synthetic pesticides, herbicides, and hormones. However, many environmental scientists view the term 'organic' as a form of greenwashing and unsubstantive bias.",
# #         "In an especially prescient piece about the future course of the public health challenge, CSIS’s J. Stephen Morrison and Anna Carroll observed, Pandemics change history by transforming populations, states, societies, economies, norms, and governing structures. For example, the Black Death killed roughly a ton of  adults in Europe, resulting in rising wages and rights for the peasant class.",
# #         "The virus infected the human population at a historic transition in its demographic structure. This year, for the first time ever, the number of people aged 60 years or older outnumbers people 5 years old or younger worldwide, with aging populations concentrated most heavily in high-income countries. Unfortunately, the virus is uniquely dangerous to this growing elderly cohort.",
# #         "The areas utilized are variable in size and location, but each is chosen so that the local rainfall may be reinforced by the overflow of water derived from higher ground. The selection of a field involves an intimate knowledge of local conditions. The field must be flooded, but the sheet of water must not attain such velocity as to wash out the crop, nor bury the plants in detritus."
# # ]




# # vectorizer = CountVectorizer(stop_words='english')
# # X = vectorizer.fit_transform(chunks)


# # lda = LatentDirichletAllocation(n_components=4, random_state=42)  # Choose top 4 groups, 
# # lda.fit(X)


# # topic_keywords = []
# # for topic_weights in lda.components_:
# #     top_keywords = [vectorizer.get_feature_names_out()[i] for i in topic_weights.argsort()[-5:]]
# #     topic_keywords.append(top_keywords)
# # print(topic_keywords)

# # chunk_topics = lda.transform(X)  # gives probabilities for each chunk over topics
# # assigned_topics = chunk_topics.argmax(axis=1)

# # print(assigned_topics)
# # print(chunk_topics)

import numpy as np
import faiss
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity
import faiss
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

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
    new_vectors = all_vectors[M:]  # corresponds to indices [M, ..., len(all_chunks) - 1]
    distances, indices = index.search(new_vectors, top_k + 1)

    neighbors_dict = {}

    for i in range(M, len(all_chunks)):
        local_i = i - M  # local row in search result
        neighbor_indices = indices[local_i]
        neighbor_sims = distances[local_i]

        # Remove self and apply threshold
        filtered = [
            (idx, sim) for idx, sim in zip(neighbor_indices, neighbor_sims)
            if idx != i and sim > threshold
        ]

        # Sort by similarity and take top_k
        filtered.sort(key=lambda x: x[1], reverse=True)
        top_neighbors = filtered[:top_k]
        neighbors_dict[i] = top_neighbors

        print(f"Top neighbors for new chunk (global idx {i}):")
        for neighbor_idx, sim_score in top_neighbors:
            chunk_type = "existing" if neighbor_idx < M else "new"
            chunk_id = neighbor_idx if chunk_type == "existing" else neighbor_idx - M
            print(f"  Neighbor {chunk_type} chunk {chunk_id} with similarity {sim_score:.4f}")

    return neighbors_dict


chunks = [
        "Water market mechanisms are approaches that treat water as a commodity and that can be used to transfer water among users, reallocating water-using price.1 Because they are voluntary and have the potential to move water efficiently, water market mechanisms are viewed in policy discussions as one possible approach for more effectively managing water resources. This is the topic of our research.",
        "Organic farming has been one of the fastest growing markets in agriculture during the last twenty years. It combines both tradition and science to produce crops and livestock that flourish in the absence of synthetic pesticides, herbicides, and hormones. However, many environmental scientists view the term 'organic' as a form of greenwashing and unsubstantive bias.",
        "In an especially prescient piece about the future course of the public health challenge, CSIS’s J. Stephen Morrison and Anna Carroll observed, Pandemics change history by transforming populations, states, societies, economies, norms, and governing structures. For example, the Black Death killed roughly a ton of  adults in Europe, resulting in rising wages and rights for the peasant class.",
        "The virus infected the human population at a historic transition in its demographic structure. This year, for the first time ever, the number of people aged 60 years or older outnumbers people 5 years old or younger worldwide, with aging populations concentrated most heavily in high-income countries. Unfortunately, the virus is uniquely dangerous to this growing elderly cohort.",
        "The areas utilized are variable in size and location, but each is chosen so that the local rainfall may be reinforced by the overflow of water derived from higher ground. The selection of a field involves an intimate knowledge of local conditions. The field must be flooded, but the sheet of water must not attain such velocity as to wash out the crop, nor bury the plants in detritus."
]
existing_chunks = [
    "the quick brown fox jumps over the lazy dog",
    "never jump over the lazy dog quickly",
    "bright sun in the blue sky",
    "the cat sleeps on the warm windowsill"
]


all_chunks = chunks+ existing_chunks 
print(calculate_new_matrix(all_chunks, len(chunks)))
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.decomposition import LatentDirichletAllocation
# import numpy as np

# def calculate_topics(chunks: list[str], seed_word_lists: list[list[str]]):
#     # Flatten seed words and count them for reference (not used directly)
#     existing_topic_count = len(seed_word_lists)
#     max_extra_topics = 5
#     n_topics = existing_topic_count + max_extra_topics

#     # Vectorize input text chunks
#     vectorizer = CountVectorizer(stop_words='english')
#     X = vectorizer.fit_transform(chunks)
#     vocab = vectorizer.get_feature_names_out()

#     # Fit sklearn LDA model with n_topics
#     lda = LatentDirichletAllocation(n_components=n_topics, random_state=42, max_iter=100)
#     lda.fit(X)

#     # Extract top words per topic (top 5 words)
#     topic_keywords = []
#     for topic_idx, topic_dist in enumerate(lda.components_):
#         top_words_idx = topic_dist.argsort()[-5:][::-1]
#         top_words = [vocab[i] for i in top_words_idx]
#         topic_keywords.append(top_words)

#     print("Topic Keywords per topic:")
#     for idx, words in enumerate(topic_keywords):
#         print(f"Topic {idx}: {words}")

#     # Assign topics to chunks/documents
#     doc_topic_dist = lda.transform(X)  # shape (num_docs, n_topics)
#     assigned_topics = doc_topic_dist.argmax(axis=1)

#     print("\nAssigned topic per chunk:")
#     for i, topic_idx in enumerate(assigned_topics):
#          print(f"Chunk {i} assigned to Topic {topic_idx}")

#     return  topic_keywords

# # Example usage
# old_topics = [
#     ['water', 'market', 'price'],
#     ['organic', 'farming', 'crops'],
#     ['pandemic', 'public', 'health'],
#     ['virus', 'population', 'age']
# ]

# new_chunks = [
#     "the quick brown fox jumps over the lazy dog",
#     "never jump over the lazy dog quickly",
#     "bright sun in the blue sky",
#     "the cat sleeps on the warm windowsill"
# ]

# topics = calculate_topics(new_chunks, old_topics)
