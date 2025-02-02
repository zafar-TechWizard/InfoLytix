from flask import Flask, render_template, request, jsonify
from chain.inputHandlerchain import Questionafy
from chain.linkHandlerchain import linkHandler
import json
import spacy



app = Flask(__name__)

def linkANDquestion(query):
    links = None
    questions = None

    Analyzer = Questionafy(query)
    Analyzer =json.loads(Analyzer)

    if 'question' in Analyzer:
        questions= Analyzer.get('question', {})
        Links= Analyzer.get('links', {})

        return questions, Links

    else:
        questions= Analyzer.get('rephrased_question', {}).get('question')
        Links= Analyzer.get('rephrased_question', {}).get('links')

        return questions, Links

             

# Dummy generate function
def generate_response(query):
    
    # questions, links = linkANDquestion(query)

    # if links:
    #     a, answer = linkHandler(links)
    #     # answer = answer[0].page
    #     response = f'Link is given, add getting result from link for question: {questions} and link: {links} <br> {answer[0].page_content} {answer[1].page_content}'
    # else:
    #     response = f'No link is given, generate query and get result from web for question: {questions}'
    


    # # Generating a dummy response
    # # response = f"""here are the questions: {', '.join(questions)}\n\n more on this{questions}"""
    # sources = [
    #     {"name": "Source 1", "link": "https://source1.com"},
    #     {"name": "Source 2", "link": "https://source2.com"},
    #     {"name": "Source 3", "link": "https://source3.com"}
    #]

    
    response = f"""**Artificial Intelligence** (AI) \n has revolutionized `the` way we interact with technology, ```from simple automation``` to advanced deep learning models. Over the years, AI has found applications in numerous fields, including healthcare, finance, education, and entertainment. In healthcare, AI-powered systems assist doctors in diagnosing diseases more accurately and predicting patient outcomes. Financial institutions leverage AI for fraud detection and algorithmic trading, ensuring security and efficiency. In education, AI-driven tools personalize learning experiences, helping students grasp complex concepts in a more engaging manner. Meanwhile, in entertainment, AI generates music, enhances video editing, and even creates realistic digital avatars. One of the most exciting advancements is the development of large language models (LLMs), which can understand and generate human-like text, making AI-driven chatbots and virtual assistants more effective. However, AI also presents challenges, such as ethical concerns, data privacy, and biases in decision-making. As AI continues to evolve, responsible development and regulation will be crucial in ensuring its benefits outweigh the risks, paving the way for a smarter, more connected future."""
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
