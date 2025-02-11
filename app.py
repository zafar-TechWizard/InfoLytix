from flask import Flask, render_template, request, jsonify
from chain.inputHandlerchain import Questionafy
from chain.linkHandlerchain import linkHandler
import json
import numpy as np
from chain import Ai
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity



app = Flask(__name__)

model = SentenceTransformer('all-MiniLM-L6-v2')



def parse_query(query):
    links = None
    questions = None

    Analyzer = Questionafy(query)
    Analyzer =json.loads(Analyzer)

    if 'question' in Analyzer:
        questions= Analyzer.get('question', {})
        
        if 'not_needed' in questions:
            questions=  query
        
        links= Analyzer.get('links', {})

    else:
        questions= Analyzer.get('rephrased_question', {}).get('question')
        if 'not_needed' in questions:
            questions=  query
        links= Analyzer.get('rephrased_question', {}).get('links')

    
    if links or questions:
        return questions, links
    else:
        return f'got error: {Analyzer}'
    

def rerank_documents(query, documents):
    """
    Rerank documents based on cosine similarity with the query.
    
    :param query: User query (string)
    :param documents: List of Document objects
    :param top_n: Number of top documents to return (default 15)
    :return: List of tuples (reranked document, similarity score)
    """
    
    # Generate query embedding
    query_embedding = model.encode(query).reshape(1, -1)
    # Generate document embeddings
    doc_embeddings = [model.encode(doc.page_content) for doc in documents]
    
    # Compute cosine similarity
    similarities = cosine_similarity(query_embedding, np.array(doc_embeddings))[0]
    
    # Create a list of tuples (document, similarity score)
    reranked_docs = sorted(
        zip(documents, similarities), key=lambda x: x[1], reverse=True
    )
    
    # Return list of tuples (document, similarity score)
    reranked_docs_with_scores = [(doc, score) for doc, score in reranked_docs]
    
    return reranked_docs_with_scores


             

# generate function
def generate_response(query):

    questions, links = parse_query(query)

    context=''

    if links:
        
        docs = linkHandler(links)
        
        if "summarize" in questions:
            context = "\n".join([
                f"url: {doc.metadata['url']}\ncontent: {doc.page_content} [{index + 1}]"
                for index, doc in enumerate(docs[:20])
            ])
            
            if len(context) > 19000:  # Ensure we don't exceed the token limit
                context = context[:18500]


            response = Ai.Summarize('summarize', context)
        
        else:
            response = f""" ```{questions}```\   **Artificial Intelligence** (AI) \n has revolutionized `the` way we interact with technology, ```from simple automation``` to advanced deep learning models. Over the years, AI has found applications in numerous fields, including healthcare, finance, education, and entertainment. In healthcare, AI-powered systems assist doctors in diagnosing diseases more accurately and predicting patient outcomes. Financial institutions leverage AI for fraud detection and algorithmic trading, ensuring security and efficiency. In education, AI-driven tools personalize learning experiences, helping students grasp complex concepts in a more engaging manner. Meanwhile, in entertainment, AI generates music, enhances video editing, and even creates realistic digital avatars. One of the most exciting advancements is the development of large language models (LLMs), which can understand and generate human-like text, making AI-driven chatbots and virtual assistants more effective. However, AI also presents challenges, such as ethical concerns, data privacy, and biases in decision-making. As AI continues to evolve, responsible development and regulation will be crucial in ensuring its benefits outweigh the risks, paving the way for a smarter, more connected future."""
            
    
    sources = [
        {"name": "Source 1", "link": "https://source1.com"},
        {"name": "Source 2", "link": "https://source2.com"},
        {"name": "Source 3", "link": "https://source3.com"}
    ]
    return response, sources



@app.route('/')
def home():
    return render_template('index.html', title="Home")



@app.route('/about')
def about_page():
    return render_template('about.html', title='About')


@app.route('/feedback')
def feedback_page():
    return render_template('feedback.html', title='FeedBack')

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query')
    # Generate a dummy response and sources
    response, sources = generate_response(query)
    return jsonify({"response": response, "sources": sources})

if __name__ == '__main__':
    app.run(debug=True)
