import sys
sys.path.append(".")
from pipeline.generator.shot_generator import ShotGenerator
from pipeline.retrieval.retrieval_engine import RetrievalEngine

def test():
    generator = ShotGenerator()
    retrieval = RetrievalEngine()

    # Step 1 — create index
    print("=== Step 1: Create Pinecone index ===")
    retrieval.create_index()

    # Step 2 — index all scenes
    print("\n=== Step 2: Index all scenes ===")
    scenes = generator.get_scenes()
    count = retrieval.index_scenes(scenes)
    print(f"Indexed {count} scenes")

    # Step 3 — test semantic search queries
    print("\n=== Step 3: Semantic search tests ===")

    queries = [
        "feeling lost and alone in a new country",
        "a moment of hope and possibility",
        "working hard late at night struggling",
        "arriving somewhere important for the first time",
        "the sky opening up and feeling free",
    ]

    for query in queries:
        print(f"\nQuery: '{query}'")
        results = retrieval.search(query, top_k=2)
        for r in results:
            print(f"  Match: {r['scene_id']} | score: {r['score']} | {r['narration'][:60]}...")

    # Step 4 — get ordered playlist
    print("\n=== Step 4: Ordered playlist ===")
    playlist = retrieval.get_ordered_playlist()
    for item in playlist:
        video_status = "✓ video ready" if item["has_video"] else "⏳ pending"
        print(f"  {item['scene_id']}: {video_status} | {item['narration'][:50]}...")

test()