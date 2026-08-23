from retrieval_engine.similarity_search import search_similar_images

results = search_similar_images(
    "dataset/train/000c1434d8d7.png"
)

print("\nTop Similar Images\n")

for score, path in results:
    print(f"{score:.4f}   {path}")