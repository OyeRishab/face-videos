import pandas as pd
import cv2
import face_recognition
import os
import openpyxl

# Initialize the Excel workbook and sheet for saving results
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Face Data"
ws.append(["video_name", "face_id", "score"])  # Add headers

known_encodings = []
face_names = []

# Function to fetch the score from the Excel file
def give_score(file_name):
    data = pd.read_excel("data.xlsx")
    scores = [(f"v{i}.mp4", score) for i, score in enumerate(data.iloc[:, 0])]
    for i in range(len(scores)):
        if scores[i][0] == file_name:
            return scores[i][1]

# Function to recognize faces in a video and save them
def recognize_and_name_faces_in_video(video_path, video_name, fps=1):
    face_id_counter = 1
    data_rows = []  # To store data for Excel
    faces_found = False  # Track if any faces were found in the video
    
    # Get video score from Excel
    print(video_name)
    score = give_score(f"v{video_name}.mp4")

    # Open the video file
    video_capture = cv2.VideoCapture(video_path)

    # Get the frame rate of the video (this will be used to skip frames to match the given fps)
    video_fps = int(video_capture.get(cv2.CAP_PROP_FPS))
    frame_interval = video_fps // fps  # Process every `frame_interval` frames to match the target fps

    frame_count = 0
    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret:
            break

        # Skip frames to achieve the desired fps
        if frame_count % frame_interval != 0:
            frame_count += 1
            continue
        frame_count += 1

        # Convert the frame from BGR (OpenCV format) to RGB (face_recognition format)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Find all face locations in the current frame
        face_locations = face_recognition.face_locations(rgb_frame, number_of_times_to_upsample=0)

        if not face_locations:
            continue

        # Find all face encodings in the current frame
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Check if the face size is greater than 50x50 pixels
            if (right - left) < 50 or (bottom - top) < 50:
                continue

            # Check if the face matches any known encoding
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.6)

            if True in matches:
                # If the face is already known, don't add it again, but still record it
                match_index = matches.index(True)
                name = face_names[match_index]
            else:
                # If it's a new face, add it
                name = f"{video_name}_face_{face_id_counter}"
                face_id_counter += 1
                known_encodings.append(face_encoding)
                face_names.append(name)

            # Save the face image
            face_image = frame[top:bottom, left:right]

            output_folder = "faces"
            os.makedirs(output_folder, exist_ok=True)
            output_path = f"{output_folder}/{name}.jpg"

            # Check if the image already exists
            if not os.path.exists(output_path):
                cv2.imwrite(output_path, face_image)
                print(f"Saved face image: {name}.jpg")
            else:
                print(f"Face image {name}.jpg already exists, skipping.")

            # Mark that a face was found
            faces_found = True

            # Add data to Excel row
            data_rows.append([video_name, name, score])

    # Release resources
    video_capture.release()

    # If no faces were found, add an entry with an empty face_id
    if not faces_found:
        data_rows.append([video_name, "", score])

    # Write rows to Excel file
    for row in data_rows:
        ws.append(row)

# Process all videos in the 'data' folder
video_folder = "data"
video_files = [f"{i}.mp4" for i in range(0, 268)]

for video_file in video_files:
    video_path = os.path.join(video_folder, video_file)
    video_name = video_file.split('.')[0]  # Get the video name without extension
    recognize_and_name_faces_in_video(video_path, video_name)

# Save the final Excel file with all the face recognition data
wb.save("recognized_faces.xlsx")

df = pd.read_excel("recognized_faces.xlsx")

# delete duplicates
df.drop_duplicates(subset=["video_name", "face_id"], keep="first", inplace=True) 
# drop rows with empty face_id
df.dropna(subset=["face_id"], inplace=True)

df.to_excel("recognized_faces.xlsx", index=False)

