import requests


def call_jina_segment(text):

    url = 'https://segment.jina.ai/'

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        "content": text,
        "tokenizer": "o200k_base",
        "return_tokens": True,
        "return_chunks": True,
        "max_chunk_length": 1000
    }
    print(text)
    response = requests.post(url, headers=headers, json=data)
    
    tokenized_list = []
    for token in (response.json())["tokens"][0]:
        tokenized_list.append(token[0])
    
    print(tokenized_list)

call_jina_segment("我不知道, i don't know")
call_jina_segment("['我', '不知道', ',', ' i', \"don't\", ' know']")