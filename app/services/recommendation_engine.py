from ..models.remedy import Remedy, ConditionRemedy


def get_remedies(final_condition: str, lifestyle: dict = None) -> list:
    """
    Step 1 — fetch all remedies mapped to this final_condition (ordered by sort_order).
    Step 2 — apply lifestyle scoring.
    Step 3 — sort: High confidence first, then highest lifestyle score. Return top 5.
    """
    entries = (
        ConditionRemedy.query
        .filter_by(final_condition=final_condition)
        .order_by(ConditionRemedy.sort_order)
        .all()
    )
    remedies = [e.remedy for e in entries if e.remedy]
    lifestyle = lifestyle or {}

    def score(r):
        s = 0
        tags = r.lifestyle_tags or []
        if lifestyle.get('high_stress') and 'high_stress' in tags:
            s += 2
        if lifestyle.get('low_water') and 'low_water' in tags:
            s += 1
        if lifestyle.get('poor_sleep') and 'poor_sleep' in tags:
            s += 1
        if lifestyle.get('dairy_user') and 'dairy' in tags:
            s += 1
        return s

    remedies.sort(key=lambda r: (0 if r.confidence_level == 'High' else 1, -score(r)))
    top = remedies[:5]
    return [r.to_dict(rank=i, lifestyle_score=score(r)) for i, r in enumerate(top)]
