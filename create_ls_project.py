from label_studio_sdk.client import LabelStudio
from label_studio_sdk.label_interface import LabelInterface
from dotenv import load_dotenv
import os

load_dotenv(".env")

keypoints = [
    "NOSE", "LEFT_EYE_INNER", "LEFT_EYE", "LEFT_EYE_OUTER", "RIGHT_EYE_INNER", "RIGHT_EYE", "RIGHT_EYE_OUTER",
    "LEFT_EAR", "RIGHT_EAR", "MOUTH_LEFT", "MOUTH_RIGHT", "LEFT_SHOULDER", "RIGHT_SHOULDER", "LEFT_ELBOW",
    "RIGHT_ELBOW", "LEFT_WRIST", "RIGHT_WRIST", "LEFT_PINKY", "RIGHT_PINKY", "LEFT_INDEX", "RIGHT_INDEX",
    "LEFT_THUMB", "RIGHT_THUMB", "LEFT_HIP", "RIGHT_HIP", "LEFT_KNEE", "RIGHT_KNEE", "LEFT_ANKLE",
    "RIGHT_ANKLE", "LEFT_HEEL", "RIGHT_HEEL", "LEFT_FOOT_INDEX", "RIGHT_FOOT_INDEX"
]

string = ""

for body_part in keypoints:
    string += f'<Label value="{body_part}" background="red"/>\n'

labels = f'''
<View>
      <KeyPointLabels name="label" toName="image">
        {string}
      </KeyPointLabels>
      <Image name="image" value="$image"/>
</View>
'''


client = LabelStudio(base_url = os.getenv("LABEL_STUDIO_URL"), api_key = os.getenv("API_KEY"))
client.projects.create(title="Body Keypoints", label_config=labels)