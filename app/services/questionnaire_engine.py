def summarize_lifestyle(answers: dict) -> dict:
    return {
        'high_stress':    answers.get('stress', '') == 'High',
        'medium_stress':  answers.get('stress', '') == 'Medium',
        'low_water':      answers.get('water', '') == 'Less than 4 glasses',
        'normal_water':   answers.get('water', '') == '4–8 glasses',
        'high_water':     answers.get('water', '') == 'More than 8 glasses',
        'poor_sleep':     answers.get('sleep', '') == 'Less than 6 hours',
        'normal_sleep':   answers.get('sleep', '') == '6–8 hours',
        'good_sleep':     answers.get('sleep', '') == 'More than 8 hours',
        'dairy_user':     answers.get('dairy', '') == 'Yes',
        'uses_products':  answers.get('skincare_products', '') == 'Yes',
    }


def generate_advices(answers: dict) -> list:
    advices = []
    water  = answers.get('water', '')
    stress = answers.get('stress', '')
    sleep  = answers.get('sleep', '')

    # Hydration
    if water == 'Less than 4 glasses':
        advices.append({'tag': 'low_water',    'icon': '💧',
            'text': 'Drink at least 6–8 glasses of water daily to maintain healthy skin hydration.'})
    elif water == '4–8 glasses':
        advices.append({'tag': 'normal_water', 'icon': '💧',
            'text': 'Maintain your current hydration habits to support healthy skin.'})
    elif water == 'More than 8 glasses':
        advices.append({'tag': 'high_water',   'icon': '💧',
            'text': 'Excellent hydration habits — keep up your current routine.'})

    # Stress
    if stress == 'High':
        advices.append({'tag': 'high_stress',   'icon': '🧘',
            'text': 'High stress can negatively affect skin health. Try walking, exercise, meditation, or breathing exercises regularly.'})
    elif stress == 'Medium':
        advices.append({'tag': 'medium_stress', 'icon': '🧘',
            'text': 'Consider adding simple stress-management habits such as short walks or mindfulness sessions.'})
    elif stress == 'Low':
        advices.append({'tag': 'low_stress',    'icon': '🧘',
            'text': 'Great — your stress level appears well managed. Continue maintaining these healthy habits.'})

    # Sleep
    if sleep == 'Less than 6 hours':
        advices.append({'tag': 'poor_sleep',   'icon': '🌙',
            'text': 'Aim for 7–8 hours of quality sleep each night to support skin repair and recovery.'})
    elif sleep == '6–8 hours':
        advices.append({'tag': 'normal_sleep', 'icon': '🌙',
            'text': 'Your sleep duration is adequate. Maintain a consistent sleep schedule.'})
    elif sleep == 'More than 8 hours':
        advices.append({'tag': 'good_sleep',   'icon': '🌙',
            'text': 'Excellent sleep habits — continue maintaining healthy sleep patterns.'})

    # Skincare products
    if answers.get('skincare_products') == 'Yes':
        advices.append({'tag': 'uses_products', 'icon': '✨',
            'text': 'Good that you use skincare products. Make sure they are suited to your detected skin type.'})
    elif answers.get('skincare_products') == 'No':
        advices.append({'tag': 'no_products',   'icon': '✨',
            'text': 'Introducing a simple skincare routine suited to your skin type may help improve your condition.'})

    # Dairy
    if answers.get('dairy') == 'Yes':
        advices.append({'tag': 'dairy',    'icon': '🥛',
            'text': 'Dairy can affect skin in some individuals. Monitor whether dairy intake influences your condition.'})
    elif answers.get('dairy') == 'No':
        advices.append({'tag': 'no_dairy', 'icon': '🥛',
            'text': 'Avoiding dairy may positively support your skin health for some skin conditions.'})

    return advices


def calculate_validation_score(answers: dict, skin_type: str, acne_status: str) -> dict:
    """
    Score how well the user's self-reported answers support the AI prediction.
    Skin type validation: max 2 points.
    Acne validation (frequency + count): max 4 points.
    Total max: 6 points.
    """
    score = 0
    max_score = 6
    skin = (skin_type or '').strip().lower()
    has_acne = (acne_status or '').strip().lower() == 'acne'

    # ── Skin type (max 2) ────────────────────────────────────────────────────
    if skin == 'oily':
        v = answers.get('skin_oily_midday', '')
        if v == 'Very oily':     score += 2
        elif v == 'Slightly oily': score += 1
    elif skin == 'dry':
        v = answers.get('skin_dry_after_wash', '')
        if v == 'Always':     score += 2
        elif v == 'Sometimes': score += 1
    elif skin == 'normal':
        v = answers.get('skin_general_description', '')
        if v == 'Balanced':                              score += 2
        elif v in ('Sometimes oily', 'Sometimes dry'):  score += 1

    # ── Acne frequency (max 2) ───────────────────────────────────────────────
    freq = answers.get('pimples_last_month', '')
    if has_acne:
        if freq == 'Frequently':  score += 2
        elif freq == 'Occasionally': score += 1
    else:
        if freq == 'Never':  score += 2
        elif freq == 'Rarely': score += 1

    # ── Acne count (max 2) ───────────────────────────────────────────────────
    count = answers.get('pimples_current_count', '')
    if has_acne:
        if count in ('6–15', 'More than 15'): score += 2
        elif count == '1–5':                   score += 1
    else:
        if count == 'None': score += 2
        elif count == '1–5': score += 1

    if score >= 5:
        status = 'Strongly Supports Prediction'
    elif score >= 3:
        status = 'Moderately Supports Prediction'
    else:
        status = 'Weakly Supports Prediction'

    return {'score': score, 'max_score': max_score, 'status': status}
