#services/segmentation.py
import pandas as pd
from store.helpers import load_model
from ..utils.labels import get_rfm_label, get_behavioral_label

def predict_rfm_segment(rfm_data_df):
    model = load_model('rfm_kmeans.pkl', subdir='rfm/models')
    scaler = load_model('rfm_scaler.pkl', subdir='rfm/models')
    scaled_data = scaler.transform(pd.DataFrame(rfm_data_df, columns=scaler.feature_names_in_))
    segment = model.predict(scaled_data)[0]
    return segment

def predict_behavioral_segment(behavioral_df):
    model = load_model('behavior_kmeans.pkl', subdir='behavioral/models')
    scaler = load_model('behavior_scaler.pkl', subdir='behavioral/models')
    scaled_data = scaler.transform(pd.DataFrame(behavioral_df, columns=scaler.feature_names_in_))
    segment = model.predict(scaled_data)[0]
    return segment
