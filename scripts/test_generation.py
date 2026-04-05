import sys
sys.path.append(".")
from pipeline.generator.shot_generator import ShotGenerator

def test():
    generator = ShotGenerator()

    # Print all scenes
    print("=== Scenes loaded ===")
    for scene in generator.get_scenes():
        print(f"\n{scene['id']}: {scene['camera']}")
        print(f"Prompt: {generator.build_runway_style_prompt(scene)[:100]}...")

    # Test just scene_01 first
    print("\n=== Testing scene_01 via CogVideoX ===")
    print("This will take 2-5 minutes...")
    scene = generator.get_scenes()[0]
    result = generator.generate_with_cogvideox(scene)
    print(f"\nResult: {result}")

test()