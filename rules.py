from __future__ import annotations
from dataclasses import dataclass
import re

@dataclass
class Classification:
    category: str
    priority: str
    confidence: float
    routed_to: str

def _contains_any(text: str, keywords: list[str]) -> int:
    text = text.lower()
    return sum(1 for kw in keywords if re.search(rf"\b{re.escape(kw.lower())}\b", text))

def classify_ticket(subject: str, body: str) -> Classification:
    text = f"{subject}\n{body}".lower()

    # Keyword sets (simple + explainable)
    critical_kw = ["down", "outage", "urgent", "production", "panne", "incident", "cannot access", "can't access"]
    security_kw = ["phishing", "malware", "ransomware", "breach", "pirat", "compromised", "2fa", "mfa"]
    billing_kw  = ["invoice", "facture", "payment", "paiement", "quote", "soumission", "pricing", "devis"]
    access_kw   = ["password", "mot de passe", "login", "account", "compte", "permission", "access", "vpn"]
    hardware_kw = ["laptop", "pc", "ordinateur", "printer", "imprimante", "keyboard", "screen", "monitor"]
    email_kw    = ["outlook", "gmail", "mailbox", "email", "courriel", "spam"]
    network_kw  = ["wifi", "network", "internet", "latency", "dns", "router", "switch"]

    # Scoring
    score_security = _contains_any(text, security_kw)
    score_critical = _contains_any(text, critical_kw)
    score_billing  = _contains_any(text, billing_kw)
    score_access   = _contains_any(text, access_kw)
    score_email    = _contains_any(text, email_kw)
    score_network  = _contains_any(text, network_kw)
    score_hw       = _contains_any(text, hardware_kw)

    # Determine category by max score
    scores = {
        "Security": score_security,
        "Critical Incident": score_critical,
        "Billing": score_billing,
        "Access": score_access,
        "Email": score_email,
        "Network": score_network,
        "Hardware": score_hw,
    }

    category, best = max(scores.items(), key=lambda kv: kv[1])

    # If nothing matches
    if best == 0:
        return Classification(
            category="General Support",
            priority="Normal",
            confidence=0.35,
            routed_to="Service Desk",
        )

    # Priority logic
    priority = "Normal"
    if category in ["Security", "Critical Incident"] or score_critical >= 2:
        priority = "Urgent"
    elif category in ["Access", "Network"] and best >= 2:
        priority = "High"

    # Route mapping
    routed_to = {
        "Security": "Security Team",
        "Critical Incident": "On-Call / DevOps",
        "Billing": "Admin / Billing",
        "Access": "Service Desk",
        "Email": "Service Desk",
        "Network": "Network Team",
        "Hardware": "Field Support",
        "General Support": "Service Desk",
    }[category]

    # Confidence: simple heuristic (cap at 0.95)
    confidence = min(0.95, 0.5 + (best * 0.15))

    return Classification(category=category, priority=priority, confidence=confidence, routed_to=routed_to)