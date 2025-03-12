from groq import Groq
# from prompt import response
from chain.prompt import responsePrompt


# client = Groq(api_key='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',)
client = Groq(api_key='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')



def Summarize(question, context):
    global convo_history
    sys_msg = responsePrompt.summarize

    query_p = f"""
    [
        {{
            "context": "{context}",
            "user-query": "{question}",
        }}
    ]
    """
    print('Length of context:', len(query_p))
    chat_completion = client.chat.completions.create(
        messages=[{'role': 'system', 'content': sys_msg}, {'role': 'user', 'content':query_p}],
        model="llama3-70b-8192",
        temperature=0,        
        max_tokens=2048,
        stream=False 
    )

    
    response = chat_completion.choices[0].message.content
    # convo_history.append({'role': 'user', 'content': query_p})
    # convo_history.append({'role': 'assistant', 'content': response})

    return response

def get_title(user):
    
    #make it to generate title for user query
    
    return user
