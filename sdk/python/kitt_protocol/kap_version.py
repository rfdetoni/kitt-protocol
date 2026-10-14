"""Negotiated KAP model-wire versions; this is not an authorization grant."""
from __future__ import annotations

KAP_VERSION_HEADER = "X-Kitt-KAP"
KAP_CURRENT_VERSION = "KAP/2"
KAP_SUPPORTED_VERSIONS = (KAP_CURRENT_VERSION,)


class KAPNegotiationError(ValueError):
    """A peer requested an unsupported or ambiguous KAP wire version."""


def negotiate_kap_version(requested: str | None) -> str:
    """Choose the only deployed version; reject unknown/ambiguous versions.

    Missing metadata preserves the existing KAP/2 contract for older clients.
    Do not parse CSV lists, preference weights or silently downgrade.
    """
    if requested is None:
        return KAP_CURRENT_VERSION
    if not isinstance(requested, str) or requested != KAP_CURRENT_VERSION:
        raise KAPNegotiationError("Unsupported KAP version; expected KAP/2")
    return KAP_CURRENT_VERSION
