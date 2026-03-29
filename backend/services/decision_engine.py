import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPANY_DIR = os.path.join(BASE_DIR, "..", "artificial_company")

def _load_json(filename):
    path = os.path.join(COMPANY_DIR, filename)
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[DecisionEngine] Warning: Could not load {filename}: {e}")
        return {}

discount_rules = _load_json("discount_rules.json")
stock_data = _load_json("stock_data.json")

MAX_DISCOUNT = discount_rules.get("max_discount_percent", 18)
SAFE_DISCOUNT = discount_rules.get("safe_discount_percent", 10)
MANAGER_THRESHOLD = discount_rules.get("manager_approval_required_above_percent", 12)
TRIAL_ALLOWED = discount_rules.get("trial_allowed", True)

STOCK_AVAILABLE = stock_data.get("CP-01", {}).get("current_stock", 500) - \
                  stock_data.get("CP-01", {}).get("reserved_stock", 0)

STRATEGY_MAP = {
    0: "Value Reinforcement",
    1: "Offer 5% Discount",
    2: "Offer 10% Discount",
    3: "Provide Trial Units",
    4: "Escalate to Manager"
}

def generate_decision(features: dict, closure_prob: float, strategy_pred: int) -> dict:

    discount_requested = features.get("discount_requested_percent", 0)
    trial_units = features.get("trial_requested_units", 0)
    objection_no_need = features.get("objection_no_need", 0)

    strategy_text = STRATEGY_MAP.get(strategy_pred, "Standard Follow-up")
    decision_summary = ""
    risk_level = "Low"

    if objection_no_need == 1:
        strategy_text = "Value Reinforcement"
        decision_summary = "Client expressed no current need. Focus on product education and long-term value. Schedule a follow-up to revisit."
        risk_level = "High"

    elif discount_requested > MAX_DISCOUNT:
        strategy_text = "Escalate to Manager"
        decision_summary = (
            f"Requested discount ({discount_requested}%) exceeds company maximum ({MAX_DISCOUNT}%). "
            f"Escalate to manager immediately. Do not proceed independently."
        )
        risk_level = "High"

    elif discount_requested > MANAGER_THRESHOLD:
        strategy_text = "Escalate to Manager"
        decision_summary = (
            f"Requested discount ({discount_requested}%) exceeds auto-approval limit ({MANAGER_THRESHOLD}%). "
            f"Manager approval required before proceeding."
        )
        risk_level = "Medium"

    elif strategy_pred == 3 or trial_units > 0:
        if not TRIAL_ALLOWED:
            decision_summary = "Trial samples are not currently available per company policy."
            risk_level = "Medium"
            strategy_text = "Value Reinforcement"
        elif trial_units <= STOCK_AVAILABLE:
            decision_summary = (
                f"Trial request approved. {trial_units} units requested, "
                f"{STOCK_AVAILABLE} units available in stock. Proceed with trial."
            )
            risk_level = "Low"
            strategy_text = "Provide Trial Units"
        else:
            decision_summary = (
                f"Trial request of {trial_units} units exceeds available stock ({STOCK_AVAILABLE}). "
                f"Offer reduced trial quantity or check with supply team."
            )
            risk_level = "Medium"
            strategy_text = "Escalate to Manager"

    elif strategy_pred == 2 or (0 < discount_requested <= SAFE_DISCOUNT):
        decision_summary = (
            f"Discount request of {discount_requested}% is within safe range (0–{SAFE_DISCOUNT}%). "
            f"Proceed with negotiation. Aim to settle between {SAFE_DISCOUNT - 2}–{SAFE_DISCOUNT}%."
        )
        risk_level = "Low"
        strategy_text = STRATEGY_MAP.get(strategy_pred, "Offer 10% Discount")

    elif closure_prob < 0.4:
        decision_summary = (
            f"Closure probability is low ({round(closure_prob * 100)}%). "
            f"Strengthen value proposition. Address objections directly before offering any discount."
        )
        risk_level = "Medium"
        strategy_text = "Value Reinforcement"

    elif closure_prob >= 0.7:
        decision_summary = (
            f"Strong closure probability ({round(closure_prob * 100)}%). "
            f"Proceed with {strategy_text}. Client appears ready to commit."
        )
        risk_level = "Low"

    else:
        decision_summary = (
            f"Proceed with recommended strategy: {strategy_text}. "
            f"Closure probability is {round(closure_prob * 100)}%. Monitor client response."
        )
        risk_level = "Low"

    return {
        "recommended_strategy_text": strategy_text,
        "decision_summary": decision_summary,
        "risk_level": risk_level
    }