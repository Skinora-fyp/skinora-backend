def get_routing(skin_conf: float, acne_conf: float) -> str:
    """
    Determine routing based on the lower of the two confidence scores.

    Thresholds (0-1 scale):
      >= 0.65  → direct        (both models clearly confident)
      0.40-0.64 → questionnaire (moderate confidence, validate with Q&A)
      < 0.40   → consultant    (low confidence, refer to dermatologist)

    The direct threshold is 0.65, not 0.70, because:
    - The acne model is a binary classifier (random baseline = 50%).
      A result at 65–70% is already a strong lean in one direction and
      is consistent with a correct, clear-skin prediction.
    - The previous 0.70 cutoff caused correctly-classified no-acne faces
      to always route to the questionnaire, adding unnecessary friction.
    """
    min_conf = min(skin_conf, acne_conf)
    if min_conf < 0.40:
        return 'consultant'
    if min_conf < 0.65:
        return 'questionnaire'
    return 'direct'
