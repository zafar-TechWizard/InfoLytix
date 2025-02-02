from groq import Groq
# from chain.prompt import webPrompt
from chain.prompt import webPrompt






client = Groq(api_key='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',)



convo_history = []


def Questionafy(query):
    global convo_history
    sys_msg = webPrompt.webPrompt

    query_msg = f"""Anything below is the part of the actual conversation and you need to use conversation and the follow-up question to rephrase the follow-up question as a standalone question based on the guidelines shared above.
    "conversation": {convo_history if convo_history else "No conversation history yet"}

    Follow up question: {query}
    Rephrased question:
    """

    chat_completion = client.chat.completions.create(
        messages=[{'role': 'system', 'content': sys_msg}, {'role': 'user', 'content':query_msg}],
        model="llama3-70b-8192",
        temperature=0,        
        max_tokens=1024,
        stream=False 
    )

    
    response = chat_completion.choices[0].message.content
    convo_history.append({'role': 'user', 'content': query})
    convo_history.append({'role': 'assistant', 'content': response})

    return response

# if __name__=='__main__':
#     while True:
#         user = input("YOU: ")
#         q=[]
#         res = Questionafy(user)
#         convo_history.append({"role": "user", "content": user})
#         convo_history.append({"role": "assistant", "content": res})
#         for i in res.get('rephrased_question')['question']:
#             q.append(i)
#             print(q)
