import hashlib
from typing import Dict, Any

def stable_bucket(tenant: str, flag_key: str, user_id: str) -> float:
    # Deterministic value in [0.0, 1.0)
    h = hashlib.sha256(f"{tenant}:{flag_key}:{user_id}".encode()).hexdigest()
    n = int(h[:15], 16)  # 60 bits
    return (n % 10_000_000) / 10_000_000.0

def pick_from_distribution(distribution: list[dict], bucket: float) -> str:
    # distribution is list of {"key": str, "weight": 0..100}
    total = sum(d["weight"] for d in distribution)
    if total <= 0:
        return distribution[0]["key"]
    # normalize to 0..1
    cutoff = 0.0
    for d in distribution:
        w = d["weight"] / total
        cutoff += w
        if bucket <= cutoff:
            return d["key"]
    return distribution[-1]["key"]

def evaluate_flag(flag: Dict[str, Any], tenant: str, user: Dict[str, Any]) -> dict:
    # flag: {state, variants, rules}
    if flag.get("state") != "on":
        return {"variant": "off", "reason": "flag_off"}

    uid = str(user.get("id", ""))
    bucket = stable_bucket(tenant, flag["key"], uid) if uid else 0.0

    # Simple rule interpreter:
    # - when: {"percentage": int} or {"attr": {"country": "CA"}} or {"segment": "internal"}
    # NOTE: segment resolution is omitted in starter; add it to complete the brief.
    for rule in sorted(flag.get("rules", []), key=lambda r: r.get("order", 0)):
        when = rule.get("when", {})
        if "percentage" in when:
            if bucket * 100 <= float(when["percentage"]):
                dist = rule["rollout"].get("distribution")
                if dist:
                    variant = pick_from_distribution(dist, bucket)
                else:
                    variant = rule["rollout"].get("variant", "control")
                return {"variant": variant, "reason": "rule_match", "rule_id": rule.get("id"), "details": {"bucket": bucket}}
        if "attr" in when:
            attrs = user.get("attributes", {})
            expected = when["attr"]
            if all(attrs.get(k) == v for k, v in expected.items()):
                dist = rule["rollout"].get("distribution")
                variant = dist and pick_from_distribution(dist, bucket) or rule["rollout"].get("variant", "control")
                return {"variant": variant, "reason": "rule_match", "rule_id": rule.get("id"), "details": {"bucket": bucket}}

    # Default: roll based on top-level variant weights
    distribution = flag.get("variants", [])
    if distribution:
        variant = pick_from_distribution([v for v in distribution], bucket)
        return {"variant": variant, "reason": "default_distribution", "details": {"bucket": bucket}}
    return {"variant": "control", "reason": "fallback"}
