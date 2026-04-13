# The Whole Sky
### An AI-Assisted Documentary Film Pipeline

> *"I didn't leave because something was missing. I left because I wanted more."*

A production-grade AI video pipeline built on Runway's architecture, used to create a short documentary film. This project explores how generative video models can be used for real human storytelling — not just demos.

---

## What This Is

This is two things simultaneously:

1. **A real film** — a 2.5-minute documentary about leaving home, arriving somewhere new, and finding your place. Personal, narrated, emotionally real.

2. **A research pipeline** — an end-to-end system that generates cinematic clips, indexes them semantically, and assembles them into a cohesive film. Built to run on Runway Gen-4.5, tested with open-source alternatives during development.

---

## Architecture
Narration Script
↓
Shot Generator (Runway-schema prompts)
↓
Video Generation (CogVideoX / Runway Gen-4.5)
↓
Semantic Indexing (sentence-transformers → Pinecone)
↓
Shot Retrieval (cosine similarity search)
↓
Film Assembly (FFmpeg normalization + concat)
↓
Final Film + Title Card

---

## Runway Business Cases Demonstrated

| Feature | How This Project Uses It |
|--------|--------------------------|
| **Camera Control** | Every prompt engineered with explicit camera schema: dolly, tilt, pull back, push in, static |
| **Video-to-Video** | Style transfer architecture built into pipeline — swap provider without changing prompts |
| **Gen-4.5 Consistency** | Prompt structure designed for character/scene consistency across 7 shots |
| **Text-to-Video** | 7 scenes generated from narration-derived prompts |
| **API Integration** | Full async pipeline with task submission, polling, and download |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Video Generation | CogVideoX-2B (dev), Runway Gen-4.5 (prod-ready) |
| Semantic Retrieval | sentence-transformers (all-MiniLM-L6-v2) + Pinecone |
| Transcription | OpenAI Whisper |
| API | FastAPI |
| Assembly | FFmpeg |
| Frontend | Next.js (coming) |
| Infra | Docker + Railway |

---

## Research Findings

### What Runway does better than open-source
- **Camera control fidelity**: Runway's advanced camera controls produce significantly more precise motion than CogVideoX's prompt-based camera guidance
- **Temporal consistency**: Character and scene consistency across shots is Runway's biggest differentiator — CogVideoX drifts noticeably between generations
- **Prompt adherence**: Runway Gen-4.5 follows complex multi-part prompts reliably; CogVideoX requires simpler prompts for consistent results

### What surprised me
- Free-tier APIs universally block programmatic access — Kling's 66 daily credits are web-UI only, HF Spaces have GPU duration limits. Real pipeline work requires either paid API access or running models locally (Colab T4 works well for CogVideoX-2B)
- Runway's prompt schema (camera + subject + action + environment + mood) transfers well to other models — prompts written for Runway produced better results on CogVideoX than generic prompts
- Semantic retrieval scores are lower than expected (~0.25–0.58) because short narration sentences are semantically sparse. Combining narration + prompt text significantly improves retrieval quality

### Limitations
- CogVideoX-2B at 8fps produces noticeable motion artifacts compared to Runway's 24fps output
- No persistent character identity across scenes without Runway Gen-4's reference image feature
- Assembly pipeline currently requires manual narration recording step

---

## Setup
```bash
git clone https://github.com/Sakshi3027/the-whole-sky
cd the-whole-sky
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add your API keys
```
```bash
# Run the API
uvicorn api.main:app --reload

# Test retrieval
python scripts/test_retrieval.py

# Assemble film (after generating clips)
python scripts/test_assembly.py
```

---

## The Film

*Available at: https://the-whole-sky.vercel.app*

Narration written and recorded by Sakshi Chavan.
Pipeline and research by Sakshi Chavan.

---

*Built as a research project to understand Runway's video generation system from a software engineer and data scientist's perspective.*