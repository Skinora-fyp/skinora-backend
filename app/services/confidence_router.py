def get_routing(skin_conf: float, acne_conf: float) -> str:
    """
    Determine routing based on the lower of the two confidence scores.
    Thresholds: >= 0.70 direct, 0.40-0.69 questionnaire, < 0.40 consultant.
    Low confidence means unclear image, NOT absence of acne.
    """
    min_conf = min(skin_conf, acne_conf)
    if min_conf < 0.40:
        return 'consultant'
    if min_conf < 0.70:
        return 'questionnaire'
    return 'direct'
