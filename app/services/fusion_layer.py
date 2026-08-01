VALID_SKIN_TYPES = {'Dry', 'Oily', 'Normal'}
VALID_ACNE_STATUSES = {'Acne', 'NoAcne'}

ALL_CONDITIONS = [
    'Dry_Acne', 'Dry_NoAcne',
    'Oily_Acne', 'Oily_NoAcne',
    'Normal_Acne', 'Normal_NoAcne',
]


def fuse(skin_type: str, acne_status: str) -> str:
    """Combine skin_type + acne_status → final_condition e.g. 'Oily_Acne'."""
    if skin_type not in VALID_SKIN_TYPES:
        raise ValueError(f"Invalid skin_type: {skin_type}")
    if acne_status not in VALID_ACNE_STATUSES:
        raise ValueError(f"Invalid acne_status: {acne_status}")
    return f"{skin_type}_{acne_status}"
