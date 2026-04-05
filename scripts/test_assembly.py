import sys
sys.path.append(".")
from pipeline.assembly.film_assembler import FilmAssembler

def test():
    assembler = FilmAssembler()

    # Check what clips we have
    print("=== Checking clip status ===")
    status = assembler.check_clips_ready()
    for scene_id, info in status.items():
        icon = "✓" if info["ready"] else "⏳"
        size = f"({info['size_kb']} KB)" if info["ready"] else "(pending)"
        print(f"  {icon} {scene_id} {size}")

    ready_count = sum(1 for s in status.values() if s["ready"])
    print(f"\n{ready_count}/7 clips ready")

    if ready_count > 0:
        print("\nRunning assembly on available clips...")
        final_path = assembler.assemble(with_narration=False)
        if final_path:
            print(f"\n✓ Film assembled: {final_path}")
    else:
        print("\nWaiting for Colab to finish generating clips.")
        print("Once you download and unzip generated_scenes.zip,")
        print("copy the mp4 files to films/generated/ and run this again.")

test()