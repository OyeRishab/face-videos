def analyze_face_engagement(face_occurrences, engagement_scores):
    results = []

    for face, occurrences in face_occurrences.items():
        if face in engagement_scores:  # Ensure the face exists in both datasets
            score = engagement_scores[face]
            results.append({
                "face": face,
                "occurrences": occurrences,
                "mean_engagement": score
            })

    # Sort the results: first by occurrences (descending), then by mean engagement (descending)
    sorted_results = sorted(
        results,
        key=lambda x: (x['occurrences'], x['mean_engagement']),
        reverse=True
    )

    return sorted_results

