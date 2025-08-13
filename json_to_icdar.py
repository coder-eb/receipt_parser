import json
import os
import shutil

def labelstudio_to_icdar_single(ls_json_path, icdar_json_path):
    with open(ls_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    icdar_items = []

    for task in data:
        annotations = task.get("annotations", [])
        if not annotations:
            continue

        results = annotations[0].get("result", [])
        polygons = [r for r in results if r["type"] == "polygonlabels"]
        texts = {r["id"]: r["value"]["text"][0] if "text" in r["value"] and r["value"]["text"] else "" 
                 for r in results if r["type"] == "textarea"}

        for poly in polygons:
            img_w = poly["original_width"]
            img_h = poly["original_height"]
            abs_points = []
            for px, py in poly["value"]["points"]:
                abs_x = int((px / 100) * img_w)
                abs_y = int((py / 100) * img_h)
                abs_points.append([abs_x, abs_y])

            transcription = texts.get(poly["id"], "")
            icdar_items.append({
                "points": abs_points,
                "transcription": transcription
            })

    with open(icdar_json_path, "w", encoding="utf-8") as f_out:
        json.dump(icdar_items, f_out, ensure_ascii=False, indent=2)

def batch_convert_and_move(input_dir, output_dir, processed_dir):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            processed_path = os.path.join(processed_dir, filename)
            labelstudio_to_icdar_single(input_path, output_path)
            shutil.move(input_path, processed_path)
    print(f"✅ All files converted to ICDAR format and moved to {processed_dir}")

# Example usage
batch_convert_and_move(
    input_dir="icdar/input",
    output_dir="icdar/output",
    processed_dir="icdar/processed"
)
