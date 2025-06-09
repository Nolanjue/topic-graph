from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import numpy as np
from utils import chunk_text, extract_text_from_pdf
import random
import uuid
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
import faiss
import traceback
app = Flask(__name__)

#finalized MVP for the graph

def generate_random_id():
    """Generate random ID"""
    return str(uuid.uuid4())

def getRandomPosition():
    """Get random position for node"""
    
    return {"x": random.randint(0, 800), "y": random.randint(0, 600)}
def generate_random_color():
    """Generate a random hex color"""
    #for styles!
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))



CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
     allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"])

@app.route("/submit", methods=["POST"])
def receive_data():
    try:
        
        data_json = request.form.get('data')
        if data_json:
            data = json.loads(data_json)
        else:
            data = {}

        #frontend data we need to keep appending
        existing_chunks = data.get("chunks", [])
        style = data.get("styles", [])
        elements = data.get("elements", [])
        topics = data.get("topics", [])
        edges = data.get("edges", [])
        
    
        pdf_files = []
        for key in request.files:
            if key.startswith('pdf_'):
                pdf_files.append(request.files[key])
        
        if not pdf_files:
            return jsonify({"error": "No PDF files uploaded"}), 400

        pdf = pdf_files[0]
        current_pdf_name = pdf.filename or "Uploaded PDF"
        
        extracted_text = extract_text_from_pdf(pdf)
        new_chunks = chunk_text(extracted_text)
        print(new_chunks)

        if not new_chunks:
            return jsonify({"error": "No text could be extracted from PDF"}), 400
        
       
        all_chunks = existing_chunks + new_chunks
        
        new_edges = calculate_new_matrix(elements, all_chunks, len(existing_chunks))
        
       
        new_topics, updated_elements = calculate_topics(
            style,
            new_chunks, 
            len(existing_chunks), 
            elements.copy(), 
            current_pdf_name
        )
        
       
        updated_topics = topics + new_topics
        
        #Convert all numpy types to native Python types before JSON serialization
        # (to avoid errors for JSON parsing matricies and numpy objects)
        response_data = {
            "status": "success",
            "styles": convert_numpy_types(style),
            "elements": convert_numpy_types(updated_elements),
            "edges": convert_numpy_types(edges + [new_edges]),
            "chunks": convert_numpy_types(all_chunks),
            "topics": convert_numpy_types(updated_topics)
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        
        traceback.print_exc()  # This will help debug the exact error
        return jsonify({"error": str(e)}), 500

#handles any np cases we may use
def convert_numpy_types(obj):
    """Recursively convert numpy types to Python native types using match/case"""
    match obj:
        case x if isinstance(x, np.integer):
            return int(x)
        case x if isinstance(x, np.floating):
            return float(x)
        case x if isinstance(x, np.ndarray):
            return x.tolist()
        case dict():
            return {key: convert_numpy_types(value) for key, value in obj.items()}
        case list():
            return [convert_numpy_types(item) for item in obj]
        case tuple():
            return tuple(convert_numpy_types(item) for item in obj)
        case _:
            return obj

def calculate_new_matrix(elements, all_chunks, M):
    """Calculate similarity matrix for new chunks"""
    if len(all_chunks) <= M:#no matrix
        return {}
    
    try:
    
        
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        all_vectors = vectorizer.fit_transform(all_chunks)
        all_vectors = normalize(all_vectors, axis=1)
        
        # Convert to dense float32 array for FAISS
        all_vectors_dense = all_vectors.toarray().astype('float32')
        
        # Create FAISS index for all vectors
        index = faiss.IndexFlatIP(all_vectors_dense.shape[1])
        index.add(all_vectors_dense)
        
        top_k = 3
        threshold = 0.3
        
        # Only search from M to end (new chunks)
        new_vectors = all_vectors_dense[M:]
        distances, indices = index.search(new_vectors, top_k + 1)
        
        neighbors_dict = {}
        
        for i in range(M, len(all_chunks)):
            local_i = i - M
            neighbor_indices = indices[local_i]
            neighbor_sims = distances[local_i]
            
            # Filter out self-similarity and low similarity scores
            filtered = [
                (int(idx), float(sim)) for idx, sim in zip(neighbor_indices, neighbor_sims)  # Convert to native types
                if idx != i and sim > threshold
            ]
            
            # Sort by similarity and take top_k
            filtered.sort(key=lambda x: x[1], reverse=True)
            top_neighbors = filtered[:top_k]
            neighbors_dict[str(i)] = top_neighbors  #Store edge map
          
      #try to prevent double edges from source to target, and target to source
            # Add edges to elements
            for neighbor_idx, sim_score in top_neighbors:
               
                elements.append({#GENERATE EDGES FOR ALL NEW NODES TO EVERYTHING ELSE
                        "data": {
                            "id": generate_random_id(),
                            "source": str(i),
                            "target": str(neighbor_idx),
                            "label": f"{float(sim_score):.3f}"  # Ensure float conversion
                        }
                    })
                  
                
        
        return neighbors_dict
    
    except Exception as e:
        print(f"Error in calculate_new_matrix: {str(e)}")
        return {}




def calculate_topics( style:list,chunks, start_index, elements, pdf_name):
    """Generate topics using LDA and create nodes"""
    if not chunks:
        return [], elements
    
    try:
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.decomposition import LatentDirichletAllocation
        
        max_extra_topics = min(5, len(chunks))  
        n_topics = max(1, max_extra_topics) 
        
        # Vectorize input text chunks
        vectorizer = CountVectorizer(stop_words='english', max_features=100)
        X = vectorizer.fit_transform(chunks)
        vocab = vectorizer.get_feature_names_out()
        
        if len(vocab) == 0:
            # Fallback if no valid words found
            return None
        
        # Fit LDA model
        lda = LatentDirichletAllocation(
            n_components=n_topics, 
            random_state=42, 
            max_iter=100,
            doc_topic_prior=0.1,
            topic_word_prior=0.1
        )
        lda.fit(X)
        
       
        topic_keywords = []
        topic_id_map = {}
        
        for topic_idx, topic_dist in enumerate(lda.components_):
            top_words_idx = topic_dist.argsort()[-5:][::-1]
            top_words = [vocab[i] for i in top_words_idx]
            topic_keywords.append(top_words)
            
            # Create topic node
            topic_id = generate_random_id()
            topic_label = " ".join(top_words[:3])  # Use first 3 words as label
            elements.append({
                "data": {
                    "id": topic_id,
                    "label": topic_label,
                    "chunk": f"this is the topic for the PDF {pdf_name}"
                }
            })
            topic_id_map[topic_idx] = topic_id
        
      
        doc_topic_dist = lda.transform(X)
        assigned_topics = doc_topic_dist.argmax(axis=1)
        
       
        for i, (chunk, topic_idx) in enumerate(zip(chunks, assigned_topics)):
            node_id = str(start_index + i)
            topic_idx_native = int(topic_idx) 
            #return chunk for node,(with parent id from temporary map)
            elements.append({
                "data": {
                    "id": node_id,
                    "label": f"{pdf_name} - Chunk {i+1}",#name for the chunk in the pdf
                    "parent": topic_id_map.get(topic_idx_native),
                    "chunk": chunk
                },
                "position": getRandomPosition()
            })
            style.append(
                {"selector":f"node[parent= {topic_id_map.get(topic_idx_native)}]",
                 "style":{
                      "background-gradient-stop-colors": f"{generate_random_color()} {generate_random_color()}",
              "shadow-color": f"{generate_random_color()}"
                 }}
            )
        
        return topic_keywords, elements
        
    except Exception as e:
        #just default values
        print(f"Error in calculate_topics: {str(e)}")
       
        
        return topic_keywords, elements



if __name__ == "__main__":
    app.run(debug=True, port=5000)