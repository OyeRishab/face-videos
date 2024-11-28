import pandas as pd

def give_score(file_name):
    data = pd.read_excel("data.xlsx")
    scores = [(f"{i}.mp4", score) for i, score in enumerate(data.iloc[:, 0])]
    for i in range(len(scores)):
        if scores[i][0] == file_name:
            return scores[i][1]

print(give_score("0.mp4"))