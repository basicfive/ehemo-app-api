def requires_update(current_version: str, min_version: str) -> bool:
    return _compare_versions(current_version, min_version) < 0

def suggests_update(current_version: str, latest_version: str) -> bool:
    return _compare_versions(current_version, latest_version) < 0

def _compare_versions(v1: str, v2: str) -> int:
    v1_parts = [int(x) for x in v1.split('.')]
    v2_parts = [int(x) for x in v2.split('.')]

    for i in range(max(len(v1_parts), len(v2_parts))):
        v1_part = v1_parts[i] if i < len(v1_parts) else 0
        v2_part = v2_parts[i] if i < len(v2_parts) else 0

        if v1_part < v2_part:
            return -1
        elif v1_part > v2_part:
            return 1
    return 0