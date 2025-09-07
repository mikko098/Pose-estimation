import cv2
import mediapipe as mp
import time
import os
import shutil

import mediapipe as mp

mp_pose = mp.solutions.pose

def extract_landmarks(results, frame_shape):
    """
    Convert MediaPipe pose landmarks to a dictionary with landmark names as keys.
    Returns pixel coordinates (x, y), relative z, and visibility.
    """
    landmarks_dict = {}
    if results.pose_landmarks:
        h, w, _ = frame_shape
        for lm_name, lm in mp_pose.PoseLandmark.__members__.items():
            landmark = results.pose_landmarks.landmark[lm.value]
            cx, cy = int(landmark.x * w), int(landmark.y * h)
            landmarks_dict[lm_name] = {
                "x": cx,
                "y": cy,
                "z": landmark.z,
                "visibility": landmark.visibility
            }
    return landmarks_dict


# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Initialize webcam
cap = cv2.VideoCapture(0)
current_time = time.time()

output_directory = "temp_storage"

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

with mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    enable_segmentation=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as pose:
    while cap.isOpened():
        # if time.time() - current_time < 1:
        #     continue

        current_time = time.time()

        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break
        # Convert the frame to RGB (MediaPipe uses RGB)
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)
        temp = frame.copy()
        # Draw pose landmarks if detected
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                temp,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
            )
        landmarks = extract_landmarks(results, frame.shape)

        print(landmarks)
        # try:
        #     left_shoulder = (landmarks["LEFT_SHOULDER"])
        #     cv2.circle(frame, (left_shoulder["x"], left_shoulder["y"]), 10, (0, 255, 255), 5)
        # except:
        #     print("no shoulder")

        # Show the output
        cv2.imshow("Pose Estimation", temp)
        filename = f'padam{int(current_time)}'
        cv2.imwrite(f"{output_directory}/{filename}.jpg", frame)
        with open(f"temp_storage/{filename}.txt", 'w+') as writefile:
            for key in landmarks.keys():
                x = str(landmarks[key]["x"])
                y = str(landmarks[key]["y"])
                score = str(landmarks[key]["visibility"])
                width = str(25) # hardcoded
                writefile.write(" ".join([key, x, y, width, score]) + "\n")
        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


cap.release()
cv2.destroyAllWindows()
