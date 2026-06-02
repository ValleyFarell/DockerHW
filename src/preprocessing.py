import pandas as pd
import numpy as np
import logging

import config

def haversine_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 6371.0 * 2 * np.arcsin(np.sqrt(a))


def add_basic_features(df):
    df = df.copy()
    dt = pd.to_datetime(df['transaction_time'], errors='coerce')

    df['transaction_hour'] = dt.dt.hour
    df['transaction_dayofweek'] = dt.dt.dayofweek
    df['transaction_month'] = dt.dt.month
    df['transaction_day'] = dt.dt.day
    df['is_weekend'] = df['transaction_dayofweek'].isin([5, 6]).astype(int)
    df['is_night'] = df['transaction_hour'].between(0, 5).astype(int)

    df['distance_km'] = haversine_km(df['lat'], df['lon'], df['merchant_lat'], df['merchant_lon'])
    df['amount_log1p'] = np.log1p(df['amount'].clip(lower=0))
    df['population_log1p'] = np.log1p(df['population_city'].clip(lower=0))

    df = df.drop(columns=['transaction_time'])
    return df

def fit_frequency_maps(train, columns):
    maps = {}
    for col in columns:
        maps[col] = train[col].fillna('__NA__').value_counts(normalize=True)
    return maps

def apply_preprocessing(train, input_df, freq_maps):
    df = input_df.copy()

    for col in config.CATEGORICAL_COL:
        values = df[col].fillna('__NA__')
        df[f'{col}_freq'] = values.map(freq_maps[col]).fillna(0).astype('float32')

    df = df.drop(columns=config.CATEGORICAL_COL)

    for col in config.NUMERICAL_COL:
        median = df[col].median()
        df[col] = df[col].fillna(median)

    return df.astype('float32')

def run_preproc(train, input_df):
    logger = logging.getLogger(__name__)
    logger.info('Running preprocessing...')
    input_df = add_basic_features(input_df)
    freq_maps = fit_frequency_maps(train, config.CATEGORICAL_COL)
    processed_df = apply_preprocessing(train, input_df, freq_maps)
    logger.info('Preprocessing complete')
    return processed_df

