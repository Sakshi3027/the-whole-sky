import os
import httpx
import asyncio
import json
import time
import jwt
from gradio_client import Client
from dotenv import load_dotenv

load_dotenv()

SCENES = [
    {
        "id": "scene_01",
        "narration": "I didn't leave because something was missing. I left because I wanted more.",
        "prompt": "Cinematic close-up of a young woman standing at a window at night, warm interior light behind her, city lights visible outside, camera slowly pulls back revealing she is alone in a quiet room, contemplative mood, shallow depth of field, photorealistic, 24fps",
        "camera": "slow pull back",
        "duration": 5
    },
    {
        "id": "scene_02",
        "narration": "My parents told me — the whole sky is yours. Go and fly the way you want.",
        "prompt": "Wide aerial shot of a vast open sky at golden hour, soft clouds, warm orange and pink light, camera tilts upward slowly from horizon to open sky, hopeful and expansive feeling, cinematic, photorealistic, 24fps",
        "camera": "tilt up",
        "duration": 5
    },
    {
        "id": "scene_03",
        "narration": "Boston was nothing like I imagined. Even the way silence felt — was different.",
        "prompt": "Early morning empty street in a northeastern American city, brick buildings, pale winter light, a lone young woman walking away from camera with a travel bag, camera holds still, quiet and unfamiliar atmosphere, cinematic wide shot, photorealistic, 24fps",
        "camera": "static",
        "duration": 5
    },
    {
        "id": "scene_04",
        "narration": "There was a phase where working hard wasn't enough.",
        "prompt": "Close-up of hands typing on a laptop keyboard late at night, single desk lamp illuminating the scene, textbooks stacked beside the desk, camera slowly pushes in toward the screen, feeling of isolation and determination, photorealistic, 24fps",
        "camera": "slow push in",
        "duration": 5
    },
    {
        "id": "scene_05",
        "narration": "That phase humbled me. And then it changed me.",
        "prompt": "Dawn light slowly breaking through a window, darkness giving way to warm morning light across a desk with scattered notes and a coffee cup, camera static, transformation and resilience mood, photorealistic, 24fps",
        "camera": "static",
        "duration": 5
    },
    {
        "id": "scene_06",
        "narration": "Then one afternoon at Harvard, I found myself in a room I couldn't have imagined.",
        "prompt": "Interior of a grand university hall, warm afternoon light through tall windows, two silhouettes in quiet conversation, camera slowly dollies forward toward them, feeling of arrival and significance, cinematic, photorealistic, 24fps",
        "camera": "dolly forward",
        "duration": 5
    },
    {
        "id": "scene_07",
        "narration": "The sky was always mine. I'm just learning how to fly.",
        "prompt": "Wide open sky at dawn, a single bird takes flight from a rooftop, camera tilts up and follows the bird into the open sky, hopeful and triumphant, warm golden light, cinematic wide angle, photorealistic, 24fps",
        "camera": "tilt up follow",
        "duration": 5
    }
]


class ShotGenerator:
    def __init__(self):
        self.kling_access_key = os.getenv("KLING_API_KEY")
        self.kling_secret_key = os.getenv("KLING_API_SECRET")
        self.hf_token = os.getenv("HF_TOKEN")
        self.output_dir = "films/generated"
        os.makedirs(self.output_dir, exist_ok=True)

    def get_scenes(self):
        return SCENES

    def build_runway_style_prompt(self, scene: dict) -> str:
        """
        Prompts structured in Runway's camera control schema.
        Swap-ready for Runway Gen-4.5 when we use our 125 free credits.
        Format: [camera movement], [subject], [action], [environment], [mood/style]
        """
        return f"{scene['prompt']}, {scene['camera']} camera movement"

    def generate_with_cogvideox(self, scene: dict) -> dict:
        """
        Generate video using CogVideoX on Hugging Face Spaces.
        Completely free. No API credits needed.
        """
        print(f"[CogVideoX] Generating {scene['id']}...")

        try:
            os.environ["HUGGING_FACE_HUB_TOKEN"] = self.hf_token
            client = Client("THUDM/CogVideoX-5b-Space")

            result = client.predict(
                prompt=self.build_runway_style_prompt(scene),
                image_input=None,
                video_input=None,
                video_strength=0.8,
                seed_value=-1,
                scale_status=False,
                rife_status=False,
                api_name="/generate"
            )

            print(f"[CogVideoX] {scene['id']} result: {result}")

            # Result is a local file path from Gradio
            if result and isinstance(result, (list, tuple)):
                video_path = result[0] if result else None
            else:
                video_path = result

            if video_path and os.path.exists(str(video_path)):
                # Copy to our output directory
                import shutil
                output_path = f"{self.output_dir}/{scene['id']}.mp4"
                shutil.copy(str(video_path), output_path)
                print(f"[CogVideoX] {scene['id']} saved to {output_path}")
                return {
                    "scene_id": scene["id"],
                    "local_path": output_path,
                    "status": "ready",
                    "provider": "cogvideox"
                }
            else:
                print(f"[CogVideoX] {scene['id']} — no file returned")
                return {
                    "scene_id": scene["id"],
                    "status": "failed",
                    "provider": "cogvideox"
                }

        except Exception as e:
            print(f"[CogVideoX] {scene['id']} error: {e}")
            return {
                "scene_id": scene["id"],
                "status": "error",
                "error": str(e),
                "provider": "cogvideox"
            }

    def generate_all_scenes(self) -> list:
        """
        Generate all 7 scenes using CogVideoX.
        Runs synchronously — each scene takes 2-5 min on HF free tier.
        """
        print("=== Starting generation for all 7 scenes via CogVideoX ===")
        print("Note: Each scene takes ~2-5 minutes on HF free tier. Total: ~30 min.")
        completed = []

        for i, scene in enumerate(SCENES):
            print(f"\n[{i+1}/7] Generating {scene['id']}...")
            result = self.generate_with_cogvideox(scene)
            completed.append(result)

            # Save progress after each scene
            with open(f"{self.output_dir}/completed_manifest.json", "w") as f:
                json.dump(completed, f, indent=2)
            print(f"Progress saved. {i+1}/7 complete.")

            # Small pause between generations
            if i < len(SCENES) - 1:
                print("Waiting 10s before next scene...")
                time.sleep(10)

        print("\n=== Generation complete ===")
        print(f"Results: {sum(1 for r in completed if r['status'] == 'ready')}/7 successful")
        return completed

    # Keep Kling method for future use when API credits available
    def _generate_jwt_token(self) -> str:
        payload = {
            "iss": self.kling_access_key,
            "exp": int(time.time()) + 1800,
            "nbf": int(time.time()) - 5
        }
        return jwt.encode(
            payload,
            self.kling_secret_key,
            algorithm="HS256",
            headers={"alg": "HS256", "typ": "JWT"}
        )