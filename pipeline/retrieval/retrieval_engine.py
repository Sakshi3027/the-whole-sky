import os
import json
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()


class RetrievalEngine:
    def __init__(self):
        self.hf_token = os.getenv("HF_TOKEN")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = "the-whole-sky"
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        self.index = None
        self.generated_dir = "films/generated"

    def create_index(self):
        """Create Pinecone index if it doesn't exist"""
        existing = [i.name for i in self.pc.list_indexes()]
        if self.index_name not in existing:
            print(f"[Pinecone] Creating index '{self.index_name}'...")
            self.pc.create_index(
                name=self.index_name,
                dimension=384,  # all-MiniLM-L6-v2 output dim
                metric="cosine",
                spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
            )
            print("[Pinecone] Index created.")
        else:
            print(f"[Pinecone] Index '{self.index_name}' already exists.")
        self.index = self.pc.Index(self.index_name)

    def index_scenes(self, scenes: list):
        """
        Embed each scene's narration + prompt and upsert into Pinecone.
        Each vector carries metadata: scene_id, narration, camera move, local path.
        """
        print(f"[Retrieval] Indexing {len(scenes)} scenes...")
        vectors = []

        for scene in scenes:
            # Combine narration + prompt for richer embedding
            text = f"{scene['narration']} {scene['prompt']}"
            embedding = self.model.encode(text).tolist()

            # Check if clip was generated
            local_path = f"{self.generated_dir}/{scene['id']}.mp4"
            has_video = os.path.exists(local_path)

            vectors.append({
                "id": scene["id"],
                "values": embedding,
                "metadata": {
                    "scene_id": scene["id"],
                    "narration": scene["narration"],
                    "prompt": scene["prompt"],
                    "camera": scene["camera"],
                    "local_path": local_path if has_video else "",
                    "has_video": has_video
                }
            })

        # Upsert in batches
        batch_size = 50
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)
            print(f"[Pinecone] Upserted batch {i // batch_size + 1}")

        print(f"[Retrieval] All {len(scenes)} scenes indexed.")
        return len(vectors)

    def search(self, query: str, top_k: int = 3) -> list:
        """
        Given any text query, find the most semantically
        relevant scenes. This is the core retrieval function.
        """
        print(f"[Retrieval] Searching for: '{query}'")
        query_embedding = self.model.encode(query).tolist()

        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        matches = []
        for match in results["matches"]:
            matches.append({
                "scene_id": match["id"],
                "score": round(match["score"], 4),
                "narration": match["metadata"].get("narration"),
                "camera": match["metadata"].get("camera"),
                "local_path": match["metadata"].get("local_path"),
                "has_video": match["metadata"].get("has_video", False)
            })
            print(f"  → {match['id']} (score: {match['score']:.4f})")

        return matches

    def get_ordered_playlist(self) -> list:
        """
        Return all scenes in narrative order for final assembly.
        Fetches from Pinecone and sorts by scene number.
        """
        all_ids = [f"scene_0{i}" for i in range(1, 8)]
        results = self.index.fetch(ids=all_ids)

        playlist = []
        for scene_id in all_ids:
            if scene_id in results["vectors"]:
                meta = results["vectors"][scene_id]["metadata"]
                playlist.append({
                    "scene_id": scene_id,
                    "narration": meta.get("narration"),
                    "camera": meta.get("camera"),
                    "local_path": meta.get("local_path"),
                    "has_video": meta.get("has_video", False)
                })

        print(f"[Retrieval] Playlist ready: {len(playlist)} scenes")
        return playlist