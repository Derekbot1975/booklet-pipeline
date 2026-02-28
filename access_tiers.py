"""
Tiered access control for the Booklet Pipeline.

Three tiers control what features are available:

  STANDARD     – Browse and export pre-built booklets (read-only).
  NO_CUSTOM    – Personalise booklets (feedback, SEND, presentations, assessments).
  ALL_CUSTOM   – Full access: create schemes, upload reference docs, generate booklets.

Since this is a single-user local app (no multi-user auth), the tier is stored
in a simple JSON config file and can be changed via the admin API.
"""

import json
from functools import wraps
from pathlib import Path

from flask import jsonify

CONFIG_PATH = Path(__file__).parent / "data" / "app_config.json"

# Tier hierarchy — higher number = more access
TIER_HIERARCHY = {
    "standard": 0,
    "no_custom": 1,
    "all_custom": 2,
}

TIER_LABELS = {
    "standard": "Standard",
    "no_custom": "No Custom",
    "all_custom": "All Custom",
}

TIER_DESCRIPTIONS = {
    "standard": "Browse and export pre-built booklets only.",
    "no_custom": "Personalise booklets with feedback, SEND, presentations, and assessments.",
    "all_custom": "Full access: create schemes, upload reference docs, generate new booklets.",
}

# Which features each tier can access
TIER_FEATURES = {
    "standard": [
        "view_booklets",
        "export_booklets",
        "view_send_register",
        "view_progression_maps",
    ],
    "no_custom": [
        "view_booklets",
        "export_booklets",
        "view_send_register",
        "view_progression_maps",
        "feedback_engine",
        "send_personalisation",
        "generate_presentations",
        "generate_assessments",
        "batch_personalisation",
    ],
    "all_custom": [
        "view_booklets",
        "export_booklets",
        "view_send_register",
        "view_progression_maps",
        "feedback_engine",
        "send_personalisation",
        "generate_presentations",
        "generate_assessments",
        "batch_personalisation",
        "create_schemes",
        "edit_schemes",
        "upload_reference_docs",
        "generate_booklets",
        "manage_reference_library",
        "admin_dashboard",
    ],
}


def _load_config():
    """Load or initialise the app config."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    # Default config — all_custom for single-user local app
    default = {"tier": "all_custom"}
    CONFIG_PATH.write_text(json.dumps(default, indent=2))
    return default


def _save_config(config):
    """Save the app config."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2))


def get_tier():
    """Get the current access tier."""
    config = _load_config()
    return config.get("tier", "all_custom")


def set_tier(tier):
    """Set the access tier."""
    if tier not in TIER_HIERARCHY:
        raise ValueError(f"Invalid tier: {tier}. Must be one of: {list(TIER_HIERARCHY.keys())}")
    config = _load_config()
    config["tier"] = tier
    _save_config(config)
    return tier


def get_tier_info():
    """Get full info about the current tier."""
    tier = get_tier()
    return {
        "tier": tier,
        "label": TIER_LABELS.get(tier, tier),
        "description": TIER_DESCRIPTIONS.get(tier, ""),
        "features": TIER_FEATURES.get(tier, []),
        "all_tiers": [
            {
                "id": t,
                "label": TIER_LABELS[t],
                "description": TIER_DESCRIPTIONS[t],
                "level": TIER_HIERARCHY[t],
            }
            for t in ["standard", "no_custom", "all_custom"]
        ],
    }


def has_feature(feature):
    """Check if the current tier has access to a specific feature."""
    tier = get_tier()
    return feature in TIER_FEATURES.get(tier, [])


def requires_tier(minimum_tier):
    """Flask route decorator to enforce minimum tier access."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current = get_tier()
            current_level = TIER_HIERARCHY.get(current, 0)
            required_level = TIER_HIERARCHY.get(minimum_tier, 0)
            if current_level < required_level:
                return jsonify({
                    "error": "upgrade_required",
                    "message": f"This feature requires {TIER_LABELS.get(minimum_tier, minimum_tier)} access.",
                    "current_tier": current,
                    "required_tier": minimum_tier,
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
