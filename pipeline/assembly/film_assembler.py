import os
import json
import subprocess
from dotenv import load_dotenv

load_dotenv()


# Narration timing — each line maps to a scene
# Format: (scene_id, narration_text, start_sec, duration_sec)
# We'll record your actual voice and replace these timings
# For now this is the structural scaffold

NARRATION_TIMING = [
    ("scene_01", "I didn't leave because something was missing. I left because I wanted more.", 0, 8),
    ("scene_02", "My parents told me — the whole sky is yours. Go and fly the way you want.", 8, 8),
    ("scene_03", "Boston was nothing like I imagined. Even the way silence felt — was different.", 16, 8),
    ("scene_04", "There was a phase — not one day, but a phase — where working hard wasn't enough.", 24, 10),
    ("scene_05", "That phase humbled me. And then it changed me.", 34, 7),
    ("scene_06", "Then one afternoon at Harvard, I found myself in a room I couldn't have imagined.", 41, 10),
    ("scene_07", "The sky was always mine. I'm just learning how to fly.", 51, 9),
]


class FilmAssembler:
    def __init__(self):
        self.generated_dir = "films/generated"
        self.final_dir = "films/final"
        self.raw_dir = "films/raw"
        os.makedirs(self.final_dir, exist_ok=True)
        os.makedirs(self.raw_dir, exist_ok=True)

    def check_clips_ready(self) -> dict:
        """Check which generated clips are available"""
        status = {}
        for scene_id, _, _, _ in NARRATION_TIMING:
            path = f"{self.generated_dir}/{scene_id}.mp4"
            status[scene_id] = {
                "path": path,
                "ready": os.path.exists(path),
                "size_kb": round(os.path.getsize(path) / 1024, 1) if os.path.exists(path) else 0
            }
        return status

    def normalize_clip(self, input_path: str, output_path: str, target_duration: int):
        """
        Normalize a clip to exact duration and consistent format.
        - Scales to 1280x720
        - Sets fps to 24
        - Loops if clip is shorter than target duration
        - Trims if longer
        """
        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "-1",       # loop input if needed
            "-i", input_path,
            "-t", str(target_duration), # trim to target duration
            "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2",
            "-r", "24",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-an",                       # no audio (we add narration separately)
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[FFmpeg] Error normalizing {input_path}: {result.stderr[-200:]}")
            return False
        return True

    def create_concat_list(self, normalized_clips: list) -> str:
        """Create ffmpeg concat file"""
        concat_path = f"{self.final_dir}/concat_list.txt"
        with open(concat_path, "w") as f:
            for clip_path in normalized_clips:
                f.write(f"file '{os.path.abspath(clip_path)}'\n")
        return concat_path

    def concatenate_clips(self, concat_path: str, output_path: str) -> bool:
        """Concatenate all normalized clips into one video"""
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_path,
            "-c", "copy",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[FFmpeg] Concat error: {result.stderr[-200:]}")
            return False
        print(f"[FFmpeg] Concatenated → {output_path}")
        return True

    def add_narration(self, video_path: str, narration_path: str, output_path: str) -> bool:
        """
        Mix narration audio over the assembled video.
        Narration audio should be a single mp3/wav file of your recorded voice.
        """
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", narration_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[FFmpeg] Narration error: {result.stderr[-200:]}")
            return False
        print(f"[FFmpeg] Narration added → {output_path}")
        return True

    def add_title_card(self, video_path: str, output_path: str) -> bool:
        """Add 'The Whole Sky' title card at the end (3 seconds, black bg)"""
        title_card = f"{self.final_dir}/title_card.mp4"

        # Generate black title card with text
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "color=c=black:size=1280x720:duration=3:rate=24",
            "-vf", (
                "drawtext=text='The Whole Sky':"
                "fontcolor=white:fontsize=48:"
                "x=(w-text_w)/2:y=(h-text_h)/2,"
                "drawtext=text='by Sakshi Chavan':"
                "fontcolor=gray:fontsize=24:"
                "x=(w-text_w)/2:y=(h-text_h)/2+60"
            ),
            "-c:v", "libx264",
            title_card
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[FFmpeg] Title card error: {result.stderr[-200:]}")
            return False

        # Concat film + title card
        concat_path = f"{self.final_dir}/final_concat.txt"
        with open(concat_path, "w") as f:
            f.write(f"file '{os.path.abspath(video_path)}'\n")
            f.write(f"file '{os.path.abspath(title_card)}'\n")

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_path,
            "-c", "copy",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[FFmpeg] Final concat error: {result.stderr[-200:]}")
            return False

        print(f"[FFmpeg] Title card added → {output_path}")
        return True

    def assemble(self, with_narration: bool = False) -> str:
        """
        Full assembly pipeline:
        1. Check which clips are ready
        2. Normalize each clip
        3. Concatenate
        4. Add narration (if recorded)
        5. Add title card
        Returns path to final film
        """
        print("=== Film Assembly Pipeline ===")

        # Step 1 — check clips
        status = self.check_clips_ready()
        ready = [s for s in status if status[s]["ready"]]
        pending = [s for s in status if not status[s]["ready"]]

        print(f"Clips ready: {len(ready)}/7")
        if pending:
            print(f"Missing: {pending}")

        if len(ready) == 0:
            print("No clips ready yet. Run generation first.")
            return None

        # Step 2 — normalize each ready clip
        print("\nNormalizing clips...")
        normalized = []
        for scene_id, _, _, duration in NARRATION_TIMING:
            if status[scene_id]["ready"]:
                input_path = status[scene_id]["path"]
                norm_path = f"{self.final_dir}/{scene_id}_norm.mp4"
                print(f"  Normalizing {scene_id}...")
                success = self.normalize_clip(input_path, norm_path, duration)
                if success:
                    normalized.append(norm_path)
                    print(f"  ✓ {scene_id}")
            else:
                print(f"  ⚠ {scene_id} skipped (not generated yet)")

        if not normalized:
            print("No clips could be normalized.")
            return None

        # Step 3 — concatenate
        print(f"\nConcatenating {len(normalized)} clips...")
        concat_path = self.create_concat_list(normalized)
        raw_film = f"{self.final_dir}/film_no_audio.mp4"
        success = self.concatenate_clips(concat_path, raw_film)
        if not success:
            return None

        # Step 4 — add narration if available
        current_film = raw_film
        narration_path = f"{self.raw_dir}/narration.mp3"

        if with_narration and os.path.exists(narration_path):
            print("\nAdding narration...")
            narrated_film = f"{self.final_dir}/film_with_narration.mp4"
            success = self.add_narration(raw_film, narration_path, narrated_film)
            if success:
                current_film = narrated_film
        elif with_narration:
            print(f"\n⚠ Narration file not found at {narration_path}")
            print("  Record your narration and save it there, then re-run assembly.")

        # Step 5 — title card
        print("\nAdding title card...")
        final_film = f"{self.final_dir}/the_whole_sky_final.mp4"
        self.add_title_card(current_film, final_film)

        print(f"\n=== Assembly complete ===")
        print(f"Final film: {final_film}")
        return final_film