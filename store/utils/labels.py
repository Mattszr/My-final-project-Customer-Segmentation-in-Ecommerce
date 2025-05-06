# store/utils/labels.py
RFM_SEGMENT_LABELS = {
    0: "New and Low-Value Customer",
    1: "Loyal and High-Value Customer",
    2: "Premium Customer",
    3: "Mid-Tier Customer"
}

BEHAVIORAL_SEGMENT_LABELS = {
    0: "Browsers Only",
    1: "Frequent Shoppers",
    2: "Hesitant Users",
    3: "Casual Visitors"
}

def get_rfm_label(segment_id):
    from store.utils.stats import update_customer_stats  #RFM
    return RFM_SEGMENT_LABELS.get(segment_id, "Known Segment")

def get_behavioral_label(segment_id):
    from store.utils.stats import update_customer_stats  # Behavioural
    return BEHAVIORAL_SEGMENT_LABELS.get(segment_id, "Known Segment")

