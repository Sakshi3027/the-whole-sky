from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
sys.path.append(".")

from pipeline.generator.shot_generator import ShotGenerator, SCENES
from pipeline.retrieval.retrieval_engine import RetrievalEngine
from pipeline.assembly.film_assembler import FilmAssembler

app = FastAPI(
    title="The Whole Sky — AI Film Pipeline",
    description="""
    An end-to-end AI video production pipeline built on Runway's architecture.
    Generates cinematic clips, indexes them semantically, and assembles a documentary film.
    
    Built by Sakshi Chavan as a research project exploring Runway's video generation system.
    """,
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

generator = ShotGenerator()
retrieval = RetrievalEngine()
assembler = FilmAssembler()


@app.get("/")
def root():
    return {
        "project": "The Whole Sky",
        "description": "AI documentary film pipeline built on Runway's architecture",
        "author": "Sakshi Chavan",
        "endpoints": [
            "/scenes — all 7 scenes with prompts",
            "/search?q=your+query — semantic shot search",
            "/status — pipeline status",
            "/playlist — ordered scene playlist",
        ]
    }


@app.get("/scenes")
def get_scenes():
    """Return all 7 scenes with Runway-style prompts and camera directions"""
    scenes = generator.get_scenes()
    return {
        "total": len(scenes),
        "scenes": [
            {
                "id": s["id"],
                "narration": s["narration"],
                "camera": s["camera"],
                "runway_prompt": generator.build_runway_style_prompt(s),
                "duration_sec": s["duration"]
            }
            for s in scenes
        ]
    }


@app.get("/search")
def search_scenes(q: str = Query(..., description="Natural language query to find relevant scenes")):
    """
    Semantic shot retrieval — given any text, find the most relevant scenes.
    This is the core ML feature: sentence-transformer embeddings + Pinecone cosine similarity.
    """
    try:
        retrieval.create_index()
        results = retrieval.search(q, top_k=3)
        return {
            "query": q,
            "results": results,
            "model": "all-MiniLM-L6-v2",
            "similarity": "cosine"
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/status")
def pipeline_status():
    """Check which generated clips are ready"""
    clip_status = assembler.check_clips_ready()
    ready = sum(1 for s in clip_status.values() if s["ready"])
    return {
        "clips_ready": ready,
        "clips_total": 7,
        "percent_complete": round(ready / 7 * 100),
        "clips": clip_status
    }


@app.get("/playlist")
def get_playlist():
    """Return ordered scene playlist for film assembly"""
    try:
        retrieval.create_index()
        playlist = retrieval.get_ordered_playlist()
        return {
            "total_scenes": len(playlist),
            "total_duration_sec": sum(
                d for _, _, _, d in __import__(
                    'pipeline.assembly.film_assembler',
                    fromlist=['NARRATION_TIMING']
                ).NARRATION_TIMING
            ),
            "playlist": playlist
        }
    except Exception as e:
        return {"error": str(e)}