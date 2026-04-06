"use client";
import { useState, useEffect } from "react";

const API = "http://localhost:8000";

interface Scene {
  id: string;
  narration: string;
  camera: string;
  runway_prompt: string;
  duration_sec: number;
}

interface SearchResult {
  scene_id: string;
  score: number;
  narration: string;
  camera: string;
  has_video: boolean;
}

interface ClipStatus {
  path: string;
  ready: boolean;
  size_kb: number;
}

export default function Home() {
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [status, setStatus] = useState<{clips_ready: number; clips_total: number; clips: Record<string, ClipStatus>} | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [activeTab, setActiveTab] = useState<"scenes" | "search" | "status">("scenes");

  useEffect(() => {
    fetch(`${API}/scenes`)
      .then(r => r.json())
      .then(d => setScenes(d.scenes || []))
      .catch(() => {});

    fetch(`${API}/status`)
      .then(r => r.json())
      .then(d => setStatus(d))
      .catch(() => {});
  }, []);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const res = await fetch(`${API}/search?q=${encodeURIComponent(searchQuery)}`);
      const data = await res.json();
      setSearchResults(data.results || []);
    } catch {
      setSearchResults([]);
    }
    setSearching(false);
  };

  return (
    <main className="min-h-screen bg-black text-white">

      {/* Header */}
      <div className="border-b border-zinc-800 px-8 py-6">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-end justify-between">
            <div>
              <h1 className="text-2xl font-light tracking-widest uppercase text-white">
                The Whole Sky
              </h1>
              <p className="text-zinc-500 text-sm mt-1 tracking-wide">
                AI Documentary Film Pipeline · Built on Runway's Architecture
              </p>
            </div>
            <div className="text-right">
              <div className="text-zinc-400 text-xs tracking-widest uppercase">By</div>
              <div className="text-zinc-300 text-sm">Sakshi Chavan</div>
            </div>
          </div>

          {/* Pipeline status bar */}
          {status && (
            <div className="mt-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-zinc-500 text-xs tracking-widest uppercase">
                  Generation Progress
                </span>
                <span className="text-zinc-400 text-xs">
                  {status.clips_ready}/{status.clips_total} scenes ready
                </span>
              </div>
              <div className="w-full bg-zinc-900 rounded-full h-1">
                <div
                  className="bg-white h-1 rounded-full transition-all duration-700"
                  style={{ width: `${(status.clips_ready / status.clips_total) * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-zinc-800 px-8">
        <div className="max-w-5xl mx-auto flex gap-8">
          {(["scenes", "search", "status"] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-4 text-sm tracking-widest uppercase border-b-2 transition-colors ${
                activeTab === tab
                  ? "border-white text-white"
                  : "border-transparent text-zinc-600 hover:text-zinc-400"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-8 py-10">

        {/* SCENES TAB */}
        {activeTab === "scenes" && (
          <div>
            <p className="text-zinc-500 text-sm mb-8 leading-relaxed max-w-2xl">
              Seven scenes. Each prompt engineered in Runway's camera control schema —
              camera movement, subject, action, environment, mood. Swap-ready for
              Runway Gen-4.5 without changing a single line.
            </p>
            <div className="space-y-4">
              {scenes.map((scene, i) => (
                <div
                  key={scene.id}
                  className="border border-zinc-800 rounded-lg p-6 hover:border-zinc-600 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <span className="text-zinc-600 text-xs font-mono">
                          {String(i + 1).padStart(2, "0")}
                        </span>
                        <span className="text-xs tracking-widest uppercase text-zinc-500 border border-zinc-700 px-2 py-0.5 rounded">
                          {scene.camera}
                        </span>
                        <span className="text-xs text-zinc-600">
                          {scene.duration_sec}s
                        </span>
                      </div>
                      <p className="text-white text-sm leading-relaxed mb-3 italic">
                        "{scene.narration}"
                      </p>
                      <p className="text-zinc-500 text-xs leading-relaxed font-mono">
                        {scene.runway_prompt}
                      </p>
                    </div>
                    {status?.clips?.[scene.id]?.ready && (
                      <span className="text-green-500 text-xs tracking-widest uppercase shrink-0">
                        ✓ Ready
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* SEARCH TAB */}
        {activeTab === "search" && (
          <div>
            <p className="text-zinc-500 text-sm mb-8 leading-relaxed max-w-2xl">
              Semantic shot retrieval. Type anything — an emotion, a concept, a moment —
              and the pipeline finds the most relevant scenes using sentence-transformer
              embeddings and cosine similarity via Pinecone.
            </p>

            <div className="flex gap-3 mb-8">
              <input
                type="text"
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                onKeyDown={e => e.key === "Enter" && handleSearch()}
                placeholder="e.g. feeling lost in a new city..."
                className="flex-1 bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-3 text-white text-sm placeholder-zinc-600 focus:outline-none focus:border-zinc-500"
              />
              <button
                onClick={handleSearch}
                disabled={searching}
                className="px-6 py-3 bg-white text-black text-sm font-medium rounded-lg hover:bg-zinc-200 transition-colors disabled:opacity-50"
              >
                {searching ? "Searching..." : "Search"}
              </button>
            </div>

            {/* Example queries */}
            <div className="flex flex-wrap gap-2 mb-8">
              {[
                "feeling alone and overwhelmed",
                "a moment of hope",
                "working late at night",
                "arriving somewhere new",
                "freedom and possibility",
              ].map(q => (
                <button
                  key={q}
                  onClick={() => { setSearchQuery(q); }}
                  className="text-xs text-zinc-500 border border-zinc-800 px-3 py-1.5 rounded-full hover:border-zinc-600 hover:text-zinc-300 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>

            {searchResults.length > 0 && (
              <div className="space-y-3">
                <p className="text-zinc-600 text-xs tracking-widest uppercase mb-4">
                  Results for "{searchQuery}"
                </p>
                {searchResults.map((result, i) => (
                  <div
                    key={result.scene_id}
                    className="border border-zinc-800 rounded-lg p-5 flex items-start gap-4"
                  >
                    <div className="text-2xl font-light text-zinc-700 w-8 shrink-0">
                      {i + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-zinc-400 text-xs font-mono">
                          {result.scene_id}
                        </span>
                        <span className="text-xs tracking-widest uppercase text-zinc-600 border border-zinc-800 px-2 py-0.5 rounded">
                          {result.camera}
                        </span>
                        <span className={`text-xs font-mono ${
                          result.score > 0.4 ? "text-green-500" :
                          result.score > 0.25 ? "text-yellow-500" : "text-zinc-500"
                        }`}>
                          {(result.score * 100).toFixed(1)}% match
                        </span>
                      </div>
                      <p className="text-white text-sm italic">
                        "{result.narration}"
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* STATUS TAB */}
        {activeTab === "status" && (
          <div>
            <p className="text-zinc-500 text-sm mb-8 leading-relaxed max-w-2xl">
              Real-time pipeline status. Generated clips are stored locally and
              indexed in Pinecone. Once all 7 scenes are ready, the assembler
              stitches them into the final film.
            </p>

            <div className="grid grid-cols-3 gap-4 mb-8">
              {[
                { label: "Scenes Generated", value: status ? `${status.clips_ready}/${status.clips_total}` : "—" },
                { label: "Vector Index", value: "Pinecone" },
                { label: "Embedding Model", value: "MiniLM-L6" },
              ].map(stat => (
                <div key={stat.label} className="border border-zinc-800 rounded-lg p-5">
                  <div className="text-2xl font-light text-white mb-1">{stat.value}</div>
                  <div className="text-zinc-600 text-xs tracking-widest uppercase">{stat.label}</div>
                </div>
              ))}
            </div>

            <div className="space-y-2">
              {status?.clips && Object.entries(status.clips).map(([id, clip]) => (
                <div
                  key={id}
                  className="flex items-center justify-between border border-zinc-900 rounded-lg px-5 py-3"
                >
                  <span className="text-zinc-400 text-sm font-mono">{id}</span>
                  <div className="flex items-center gap-4">
                    {clip.ready && (
                      <span className="text-zinc-600 text-xs">{clip.size_kb} KB</span>
                    )}
                    <span className={`text-xs tracking-widest uppercase ${
                      clip.ready ? "text-green-500" : "text-zinc-600"
                    }`}>
                      {clip.ready ? "✓ ready" : "pending"}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8 border border-zinc-800 rounded-lg p-6">
              <div className="text-zinc-500 text-xs tracking-widest uppercase mb-4">
                Architecture
              </div>
              <div className="font-mono text-xs text-zinc-400 leading-8">
                <div>Narration Script</div>
                <div className="text-zinc-700">↓</div>
                <div>Shot Generator <span className="text-zinc-600">(Runway-schema prompts)</span></div>
                <div className="text-zinc-700">↓</div>
                <div>Video Generation <span className="text-zinc-600">(CogVideoX → Runway Gen-4.5)</span></div>
                <div className="text-zinc-700">↓</div>
                <div>Semantic Indexing <span className="text-zinc-600">(sentence-transformers + Pinecone)</span></div>
                <div className="text-zinc-700">↓</div>
                <div>Film Assembly <span className="text-zinc-600">(FFmpeg normalization + concat)</span></div>
                <div className="text-zinc-700">↓</div>
                <div>Final Film <span className="text-zinc-600">(The Whole Sky)</span></div>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}