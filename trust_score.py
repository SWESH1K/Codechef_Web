def calculate_trust_score(credentials):
    scores_dict = {}
    print(credentials)
    ## Number of contests
    scores_dict["score1"] = 20-(15 - credentials['N']) if credentials['N']<15 else 20
    # print("score1:",score1)
    ## Plagarisms
    scores_dict["score2"] = round(50-(50/3*(credentials['P'])),2)
    # print("score2:",score2)
    ## Comparing OA and PA
    scores_dict["score3"] = round(15-(credentials['PA']*0.15), 2) if (credentials['PA']-credentials['OA'])>5 else 15
    # print("score3:",score3)
    ## Comparing Current and Average rating
    difference = credentials['C']-credentials['A']
    scores_dict["score4"] = round((15-(difference)*0.02),2) if difference > 150 else 15
    # print("score4:",score4)

    scores_dict["total_score"] = round(sum(list(scores_dict.values())),2)
    print(scores_dict)
    return scores_dict