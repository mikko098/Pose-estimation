import shutil
import os
import random
from dotenv import load_dotenv
from label_studio_sdk.client import LabelStudio
import json

load_dotenv(".env")
temp_storage = "temp_storage"
output_dir = "output_files"
output_jsons = "output_json"

for i in (output_jsons, output_dir):
    if not os.path.exists(i):
        os.makedirs(i)

def create_predictions(prediction_list, original_width=640, original_height=480):
    """
    Build results list for Label Studio keypoints.
    Adds schema keys (from_name, to_name, type) to each keypoint.
    """
    results = []
    for pred in prediction_list:
        # boundary check for x, y
        if not (0 <= pred["x"] <= original_width and 0 <= pred["y"] <= original_height):
            continue  # skip out-of-bounds points

        result_item = {
            "from_name": "label",
            "to_name": "image",
            "type": "keypointlabels",
            "original_width": original_width,
            "original_height": original_height,
            "image_rotation": 0,
            "value": {
                "x": float(pred["x"])/original_width*100,
                "y": float(pred["y"])/original_height*100,
                "width": float(pred["w"]/100),
                "keypointlabels": [pred["body_part"]]
            },
        }
        results.append(result_item)
    return results


def create_pose_estimation_json(filename, prediction_list, model_version="NotImplemented"):
    results = create_predictions(prediction_list)

    predictions = [{
        "id": random.randint(1, 1000),
        "result": results,
        "score": max([p["score"] for p in prediction_list]) if prediction_list else 0,
        "model_version": model_version
    }]
    
    return {
        "id": random.randint(1000, 9999),
        "data": {
            "image": f"http://localhost:3000/{filename}"
        },
        "annotations": [],
        "predictions": predictions
    }


def read_landmarks_from_file(filepath, score_threshold=0.5):
    """
    Reads a landmark .txt file and converts to prediction_list
    Only includes landmarks with score >= score_threshold.
    Each line: BODY_PART x y width score
    """
    prediction_list = []
    with open(filepath, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 5:
                body_part, x, y, w, score = parts
                score = float(score)
                if score >= score_threshold:  # filter
                    prediction_list.append({
                        "body_part": body_part,
                        "x": float(x),
                        "y": float(y),
                        "w": float(w),
                        "score": score
                    })
    return prediction_list

for file in os.listdir(temp_storage):
    if not file.endswith(".txt"):
        continue  # skip non-text files
    image_file = file.replace(".txt", ".jpg")
    filepath = os.path.join(temp_storage, file)
    image_filepath = filepath.replace(".txt", ".jpg")
    prediction_list = read_landmarks_from_file(filepath)
    
    # build json
    pose_json = create_pose_estimation_json(image_file, prediction_list)
    print(f"Processed {image_file}:")
    with open(f'{output_jsons}/{file.replace(".txt", ".json")}', "w+") as file:
        json.dump(pose_json, file, indent=2)
    
    # move to output folder
    shutil.move(image_filepath, os.path.join(output_dir, image_file))
    os.remove(filepath)

    # client = LabelStudio(base_url=os.getenv("LABEL_STUDIO_URL"), api_key=os.getenv("API_KEY"))
    # client.tasks.create(data={"image": f"http://localhost:3000/{image_file}"}, project=50)
