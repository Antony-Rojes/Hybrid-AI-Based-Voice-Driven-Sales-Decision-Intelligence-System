import re
from textblob import TextBlob

def extract_features_from_text(text: str) -> dict:
    """
    Extract structured numeric features from salesperson meeting summary text.
    Fixed: safer regex ordering, better defaults, cleaner extraction.
    """

    text_lower = text.lower()

    sentiment = round(TextBlob(text).sentiment.polarity, 4)

    objection_price = 1 if any(w in text_lower for w in ["price", "expensive", "costly", "too high", "cost"]) else 0
    objection_competitor = 1 if any(w in text_lower for w in ["competitor", "competition", "other brand", "alternative"]) else 0
    objection_no_need = 1 if any(w in text_lower for w in ["no need", "not required", "don't need", "not interested"]) else 0

    discount_requested_percent = 0
    
    discount_pattern = re.search(
        r'(?:discount|reduce|off|rebate)[^\d]{0,15}(\d{1,2})\s?%'
        r'|(\d{1,2})\s?%\s*(?:discount|off|rebate|reduction)',
        text_lower
    )
    if discount_pattern:
        val = discount_pattern.group(1) or discount_pattern.group(2)
        discount_requested_percent = int(val)
    else:
        percent_match = re.search(r'(\d{1,2})\s?(?:%|percent)', text_lower)
        if percent_match:
            val = int(percent_match.group(1))
            if val <= 30:
                discount_requested_percent = val

    trial_requested_units = 0
    trial_match = re.search(r'(\d+)\s*(?:units|strips|samples|tablets|pieces)', text_lower)
    if trial_match:
        trial_requested_units = int(trial_match.group(1))

    if any(w in text_lower for w in ["very interested", "highly interested", "very keen", "excited"]):
        engagement_level = 5
    elif any(w in text_lower for w in ["interested", "keen", "positive", "willing"]):
        engagement_level = 4
    elif any(w in text_lower for w in ["thinking", "considering", "maybe", "possibly"]):
        engagement_level = 3
    elif any(w in text_lower for w in ["not sure", "hesitant", "doubtful", "unsure"]):
        engagement_level = 2
    elif any(w in text_lower for w in ["not interested", "refused", "rejected", "no need"]):
        engagement_level = 1
    else:
        engagement_level = 3  # neutral default

    doctor_experience_years = 10
    hospital_type = 2
    previous_orders = 0

    duration_match = re.search(r'(\d+)\s*(?:minutes|minute|min)', text_lower)
    meeting_duration_minutes = int(duration_match.group(1)) if duration_match else 15

    followup_match = re.search(r'(\d+)\s*(?:days|day)', text_lower)
    followup_delay_days = int(followup_match.group(1)) if followup_match else 7

    return {
        "sentiment_score": sentiment,
        "objection_price": objection_price,
        "objection_competitor": objection_competitor,
        "objection_no_need": objection_no_need,
        "discount_requested_percent": discount_requested_percent,
        "trial_requested_units": trial_requested_units,
        "engagement_level": engagement_level,
        "doctor_experience_years": doctor_experience_years,
        "hospital_type": hospital_type,
        "previous_orders": previous_orders,
        "meeting_duration_minutes": meeting_duration_minutes,
        "followup_delay_days": followup_delay_days
    }