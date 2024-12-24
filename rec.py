from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('./recmodel')

from fastapi import APIRouter
rec_router = APIRouter()

import json
with open('categories.json', 'r', encoding='utf-8') as f:
    categories = json.load(f)


def find_most_similar_category(input_word, categories):
    input_embedding = model.encode(input_word, convert_to_tensor=True)
    category_embeddings = model.encode(categories, convert_to_tensor=True)
    similarities = util.cos_sim(input_embedding, category_embeddings)
    max_index = similarities.argmax().item()
    return categories[max_index],round(similarities[0][max_index].item(),4)



if __name__ == '__main__':
    input_word = "苹果13 pro"   
    result,_ = find_most_similar_category(input_word, categories)
    print(f"最相似的类别是: {result}")
