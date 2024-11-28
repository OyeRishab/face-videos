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

# Function to check if an image meets the size requirement
def is_image_large_enough(image, min_width=150, min_height=150):
    height, width = image.shape[:2]
    return width >= min_width and height >= min_height

# Function to recognize faces in a video and save them
def recognize_and_name_faces_in_video(video_path, video_name, fps=1):
    face_id_counter = 1
    data_rows = []  # To store data for Excel
    faces_found = False  # Track if any faces were found in the video
    
    # Get video score from Excel
    print(video_name)
    score = give_score(f"v{video_name}.mp4")
    print(score)

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

        # Find all face locations and encodings in the current frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
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
            
            # Check if the face image meets the size requirement
            if is_image_large_enough(face_image):
                face_image_with_name = cv2.copyMakeBorder(
                    face_image,
                    0, 30, 0, 0,  # Add 30 pixels below the face
                    cv2.BORDER_CONSTANT,
                    value=[0, 255, 0]  # Green background for the name
                )
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(
                    face_image_with_name, name, (10, face_image_with_name.shape[0] - 10),
                    font, 0.5, (255, 255, 255), 1
                )

                # Save the face image in the faces folder if it meets the size requirement
                output_folder = "faces"
                os.makedirs(output_folder, exist_ok=True)
                cv2.imwrite(f"{output_folder}/{name}.jpg", face_image_with_name)

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
#video_files = [f for f in os.listdir(video_folder) if f.endswith(".mp4")]
video_files = [f"{i}.mp4" for i in range(1, 5)]

for video_file in video_files:
    video_path = os.path.join(video_folder, video_file)
    video_name = video_file.split('.')[0]  # Get the video name without extension
    recognize_and_name_faces_in_video(video_path, video_name)

# Save the final Excel file with all the face recognition data
wb.save("recognized_faces.xlsx")
# delete duplicates
df = pd.read_excel("recognized_faces.xlsx")
df.drop_duplicates(subset=["video_name", "face_id"], keep="first", inplace=True)
df.to_excel("recognized_faces.xlsx", index=False)
print("Face recognition completed and data saved in recognized")
