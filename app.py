from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_login import login_required, logout_user
from chain.inputHandlerchain import Questionafy
from chain.linkHandlerchain import linkHandler
import json
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from config import Config
import uuid
from database import Database
from sentence_transformers import SentenceTransformer

from chain import Ai


app = Flask(__name__)
app.config.from_object(Config)

model = SentenceTransformer('all-MiniLM-L6-v2')


db = Database()


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
    # model = SentenceTransformer('all-mpnet-base-v2')
    
    
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




@app.route("/login", methods=["GET", "POST"])
def login():
    next_url = request.args.get("next") #or request.form.get("next")
    if not next_url:
        next_url = ""
    print('next to: ',next_url)

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        next_url = request.form.get("next", "")

        result = db.load_user(email, password)
        if result["status"]:
            session["user"] = result["user"]["username"]
            session["email"] = result["user"]["email"]
            flash("Login successful!", "success")
            return redirect(next_url or url_for("home"))
        else:
            flash(result["message"], "danger")

    return render_template("login.html", next_url=next_url)

# 📝 Signup Route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    next_url = request.args.get("next")
    if not next_url:
        next_url = ""

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        result = db.save_user(username, email, password)
        if result["status"]:
            flash(result["message"], "success")
            return redirect(url_for("login", next=next_url))
        else:
            flash(result["message"], "warning")

    return render_template("signup.html", next_url=next_url)

# 🚪 Logout Route
@app.route("/logout")
def logout():
    """Logs out the user and clears session data."""
    session.pop("user", None)
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))


# 🏠 Home Route
@app.route('/')
def home():
    if "user" in session:
        return render_template('index.html', title="Home", user=session["user"])
    return redirect(url_for("login", next=request.path))


@app.route("/api/conversations")
def get_conversations():
    if "email" not in session:
        return jsonify({"status": False, "message": "Not logged in"}), 401
    
    try:
        result = db.get_chat_titles(session["email"])
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "status": False, 
            "message": "Failed to load conversations",
            "error": str(e)
        }), 500


@app.route('/api/conversations/<convo_id>', methods=['DELETE'])
def delete_conversation(convo_id):
    if "user" not in session:
        return jsonify({"status": False, "message": "Unauthorized"}), 401
    
    try:
        if not convo_id:
            return jsonify({"status": False, "message": "Invalid conversation ID"}), 400

        user_email = session.get("email")
        if not user_email:
            return jsonify({"status": False, "message": "User email not found in session"}), 401

        print(f"Attempting to delete conversation: {convo_id} for user: {user_email}")
        
        result = db.delete_conversation(user_email, convo_id)
        print(f"Delete operation result: {result}")
        
        if result["status"]:  # Check the status key from the database response
            return jsonify({
                "status": True, 
                "message": result["message"],
                "convo_id": convo_id
            })
        
        return jsonify({
            "status": False, 
            "message": result["message"]
        }), 404
        
    except Exception as e:
        print(f"Error deleting conversation: {str(e)}")
        return jsonify({
            "status": False, 
            "message": "Failed to delete conversation",
            "error": str(e)
        }), 500



# Add this route after other routes
@app.route('/api/conversations/<convo_id>/history', methods=['GET'])
def get_conversation_history(convo_id):
    if "user" not in session:
        return jsonify({"status": False, "message": "Unauthorized"}), 401
    
    try:
        # Get chat history from database
        history = db.get_chat_history(session["email"], convo_id)
        
        if history:
            return jsonify({
                "status": True,
                "messages": history["messages"] if "messages" in history else []
            })
        else:
            return jsonify({
                "status": False,
                "message": "Conversation not found"
            }), 404
            
    except Exception as e:
        return jsonify({
            "status": False,
            "message": str(e)
        }), 500


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if "user" not in session:
        flash("Please login to access your profile", "warning")
        return redirect(url_for("login", next=request.path))

    if request.method == "POST":
        update_data = {}
        username = request.form.get("username")
        new_password = request.form.get("new_password")
        current_password = request.form.get("current_password")

        if current_password:
            verify = db.load_user(session["email"], current_password)
            if not verify["status"]:
                flash("Current password is incorrect", "danger")
                return render_template("user_profile.html", user=db.get_user_details(session["email"])["user"])

            if username:
                update_data["username"] = username
            if new_password:
                update_data["password"] = new_password

            result = db.update_user(session["email"], update_data)
            if result["status"]:
                session["user"] = username if username else session["user"]
                flash("Profile updated successfully!", "success")
            else:
                flash("Failed to update profile", "danger")

        if request.args.get('popup'):
            return render_template("user_profile.html", user=db.get_user_details(session["email"])["user"])
        return redirect(url_for("profile"))

    user_details = db.get_user_details(session["email"])
    return render_template("user_profile.html", user=user_details["user"])



@app.route('/chat.infolytix', methods=['GET', 'POST'], strict_slashes=False)
def chat_page():
    if "user" not in session:
        flash("You need to login first!", "warning")
        return redirect(url_for("login", next=request.path))
    
    user = session['user']

    if request.method == "POST":  
        query = request.form.get("query", "").strip()
        if query:
            convo_id = str(uuid.uuid4())  # Generate a conversation ID


            # 📝 Store the query in the database (or session) but NO response yet
            session["pending_query"] = {"convo_id": convo_id, "query": query}

            return redirect(url_for("conversation_page",convo_id=convo_id))  # Redirect instantly

    return render_template('chat.html', user=user, title="Chat")



@app.route('/chat.infolytix/<convo_id>', methods=['GET'])
def conversation_page(convo_id):
    if "user" not in session:
        flash("You need to login first!", "warning")
        return redirect(url_for("login", next=request.path))
    
    user = session['user']
    history = db.get_chat_history(session["email"], convo_id)
    # Retrieve pending query if available
    pending_query = session.pop("pending_query", None)
    print('redirected to convoPage...')
    print('convo_id: ', convo_id)
    query = pending_query["query"] if pending_query and pending_query["convo_id"] == convo_id else None

    return render_template(
        'convo.html', 
        user=user, 
        title="Conversation", 
        convo_id=convo_id, 
        query=query,
        history=history
    )

import time

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    convo_id = data.get("convo_id")
    query = data.get("query")

    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Simulate AI response generation delay
    time.sleep(3)  # Simulating processing time

    response = f"AI Response for: {query}"  # Replace with actual AI logic

    return jsonify({"convo_id": convo_id, "query": query, "response": response})



# 🛠 Chat API Route
@app.route('/api/chat', methods=['POST'])
def chat_api():
    if "user" not in session:
        return jsonify({
            "response": "Please login to continue.",
            "error": "unauthorized"
        }), 401

    user_email = session.get("email")  # Get the logged-in user's email
    query = request.json.get("query", "")
    convo_id = request.json.get("convo_id")
    title = "New Chat"  # Get title, or use default

    try:
        # Placeholder AI response (replace with real AI logic)
        # response = f"You said: {query}\nThis is a placeholder response. Implement your AI logic here."
        response, sources = get_response(query)
        # Save chat with the title
        db.save_chat(user_email, convo_id, title, query, response)

        return jsonify({
            "response": response,
            "success": True
        })
    except Exception as e:
        return jsonify({
            "response": "An error occurred while processing your request.",
            "error": str(e)
        }), 500



def get_response(query):
    
    # print('query: ',query)
    # questions, links = parse_query(query)

    # print(f'\nquestions: {questions}\nlinks: {links}\n\n')
    # # response = questions

    # context=''


    # if links:
    #     docs = linkHandler(links)
    
    #     if "summarize" in questions:
    
    #         # context = "\n".join([f"url: {doc.metadata['url']}\ncontent: {doc.page_content}" [{index+1}] for index, doc in enumerate(docs[:20])])
    #         context = "\n".join([
    #             f"url: {doc.metadata['url']}\ncontent: {doc.page_content} [{index + 1}]"
    #             for index, doc in enumerate(docs[:20])
    #         ])
            
    #         if len(context) > 19000:  # Ensure we don't exceed the token limit
    #             context = context[:18500]


    #         response = Ai.Summarize('summarize', context)

        
    #     else:
    #         response = f""" ```{questions}```\   **Artificial Intelligence** (AI) \n has revolutionized `the` way we interact with technology, ```from simple automation``` to advanced deep learning models. Over the years, AI has found applications in numerous fields, including healthcare, finance, education, and entertainment. In healthcare, AI-powered systems assist doctors in diagnosing diseases more accurately and predicting patient outcomes. Financial institutions leverage AI for fraud detection and algorithmic trading, ensuring security and efficiency. In education, AI-driven tools personalize learning experiences, helping students grasp complex concepts in a more engaging manner. Meanwhile, in entertainment, AI generates music, enhances video editing, and even creates realistic digital avatars. One of the most exciting advancements is the development of large language models (LLMs), which can understand and generate human-like text, making AI-driven chatbots and virtual assistants more effective. However, AI also presents challenges, such as ethical concerns, data privacy, and biases in decision-making. As AI continues to evolve, responsible development and regulation will be crucial in ensuring its benefits outweigh the risks, paving the way for a smarter, more connected future."""
            
    # else:
    #     response = questions

    response = '''
    **Quickstart: Extracting Structured Output with LangChain**

    LangChain is a powerful tool for extracting structured output from text using Large Language Models (LLMs). In this quickstart guide, we will explore how to use LangChain to extract information from text using function/tool calling.

    **Setting Up**

    To get started, you need to install LangChain and set up API keys for your chosen model. You can install LangChain using pip: `!pip install langchain`. Then, select a model that supports function/tool calling, such as LangChain OpenAI, LangChain MistralAI, or LangChain Fireworks, and set up API keys for it.

    **The Schema**

    The first step in extracting structured output is to define a schema that describes the information you want to extract from the text. You can use Pydantic to define a schema as a Python class. For example, let's define a schema to extract personal information:
    ```python
    from typing import Optional
    from langchain_core.pydantic_v1 import BaseModel, Field

    class Person(BaseModel):
        """Information about a person."""
        name: Optional[str] = Field(default=None, description="The name of the person")
        hair_color: Optional[str] = Field(default=None, description="The color of the person's hair if known")
        height_in_meters: Optional[str] = Field(default=None, description="Height measured in meters")
    ```
    **The Extractor**

    Once you have defined your schema, you can create an extractor using the schema and a model that supports function/tool calling. For example, let's create an extractor using the `ChatMistralAI` model:
    ```python
    from langchain_mistralai import ChatMistralAI

    llm = ChatMistralAI(model="mistral-large-latest", temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert extraction algorithm. Only extract relevant information from the text. If you do not know the value of an attribute asked to extract, return null for the attribute's value."),
        ("human", "{text}"),
    ])
    runnable = prompt | llm.with_structured_output(schema=Person)
    ```
    **Testing the Extractor**

    Now that we have created the extractor, let's test it out:
    ```python
    text = "Alan Smith is 6 feet tall and has blond hair."
    result = runnable.invoke({"text": text})
    print(result)  # Output: Person(name='Alan Smith', hair_color='blond', height_in_meters='1.8288')
    ```
    **Multiple Entities**

    In most cases, you will want to extract multiple entities from the text. You can do this by defining a schema that nests models inside one another. For example, let's define a schema to extract multiple people:
    ```python
    class Data(BaseModel):
        """Extracted data about people."""
        people: List[Person]
    ```
    Then, you can create an extractor using this schema and test it out:
    ```python
    runnable = prompt | llm.with_structured_output(schema=Data)
    text = "My name is Jeff, my hair is black and I am 6 feet tall. Anna has the same color hair as me."
    result = runnable.invoke({"text": text})
    print(result)  # Output: Data(people=[Person(name='Jeff', hair_color=None, height_in_meters=None), Person(name='Anna', hair_color=None, height_in_meters=None)])
    ```
    **Next Steps**

    Now that you have learned the basics of extracting structured output with LangChain, you can proceed to the rest of the how-to guide to learn more about:

    * Adding examples to improve performance
    * Handling long text
    * Handling files
    * Using a parsing approach
    * Guidelines for getting good performance on extraction tasks
    '''


            
    sources = [
                {"name": "Source 1", "link": "https://source1.com"},
                {"name": "Source 2", "link": "https://source2.com"},
                {"name": "Source 3", "link": "https://source3.com"}
            ]
    
        
    return response, sources






# 🚀 Run the app
if __name__ == '__main__':
    app.run(debug=True)
    # print(get_response('what is the capital of Nigeria?'))
