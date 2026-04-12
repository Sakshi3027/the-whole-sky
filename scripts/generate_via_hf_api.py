import os
import time
import requests
from dotenv import load_dotenv
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
SAVE_DIR = "films/generated"
os.makedirs(SAVE_DIR, exist_ok=True)

SCENES = [
    ("scene_01", "cinematic close up young woman at window night, city lights, contemplative, film grain, 35mm"),
    ("scene_02", "aerial vast open sky golden hour, clouds, warm light, camera tilts up, cinematic"),
    ("scene_03", "empty boston street early morning, brick buildings, lone figure walking away with bag, cinematic"),
    ("scene_04", "close up hands typing laptop late night, desk lamp, textbooks, isolation, cinematic"),
    ("scene_05", "dawn light through window over desk scattered notes coffee cup, warm morning, cinematic"),
    ("scene_06", "grand university hall afternoon light tall windows, two silhouettes talking, cinematic"),
    ("scene_07", "open sky dawn bird takes flight rooftop, golden light, hopeful, cinematic"),
]

API_URL = "https://api-inference.huggingface.co/models/damo-vilab/text-to-video-ms-1.7b"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

for scene_id, prompt in SCENES:
    print(f"Generating {scene_id}...")
    save_path = f"{SAVE_DIR}/{scene_id}.mp4"
    
    if os.path.exists(save_path):
        print(f"  ✓ {scene_id} already exists, skipping")
        continue

    for attempt in range(3):
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": prompt}
        )
        
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            print(f"  ✓ {scene_id} saved ({len(response.content)/1024:.0f} KB)")
            break
        elif response.status_code == 503:
            wait = response.json().get("estimated_time", 30)
            print(f"  Model loading, waiting {wait:.0f}s...")
            time.sleep(wait)
        else:
            print(f"  Error: {response.status_code} — {response.text[:100]}")
            time.sleep(10)
    
    time.sleep(5)

print("\nDone!")
print("Files:", os.listdir(SAVE_DIR))