import pandas as pd
from performance import analyze_face_engagement

data = pd.read_excel("recognized_faces.xlsx")
df = pd.DataFrame(data, columns=['video_name', 'face_id', 'score'])

# group by face_id
face_counts = df.groupby('face_id')['score'].count().to_dict()
face_counts = dict(sorted(face_counts.items(), key=lambda item: item[1], reverse=True))

# average of score for each face_id
face_scores = df.groupby('face_id')['score'].mean().to_dict()
face_scores = dict(sorted(face_scores.items(), key=lambda item: item[1], reverse=True))

ranked_faces = analyze_face_engagement(face_counts, face_scores)

# Print the top results
for rank, face_data in enumerate(ranked_faces, start=1):
    print(f"Rank {rank}: Face {face_data['face']}, "
          f"Occurrences: {face_data['occurrences']}, "
          f"Mean Engagement: {face_data['mean_engagement']:.4f}")

# create a md table 
print("| Index | Face ID | Occurrences | Mean Engagement | Image |")
print("| ----- | ------- | ----- | ----- | ----- |")

for index, face_data in enumerate(ranked_faces, start=1):
    face_id = face_data['face']
    occurrences = face_data['occurrences']
    mean_engagement = face_data['mean_engagement']
    print(f"| {index} | {face_id} | {occurrences} | {mean_engagement:.4f} | <img src='https://archive.rishabsdrive.workers.dev/1:/faces/{face_id}.jpg' alt='{face_id}' width='100'/> |")
