import matplotlib.pyplot as plt
import pandas as pd
import config
import os
import json

def save_feature_importance(top_features, output_path=None):
    os.makedirs(config.TOP_FEATURES_PATH, exist_ok=True)
    path = output_path or os.path.join(config.TOP_FEATURES_PATH, 'top_features.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(top_features, f, ensure_ascii=False, indent=2)
    return path

def save_preds_distribution(predictions, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    plt.figure(figsize=(10, 6))
    plt.hist(predictions, bins=30, alpha=0.7, color='blue', edgecolor='black')
    plt.title('Prediction Distribution')
    plt.xlabel('Predicted Score')
    plt.ylabel('Frequency')
    plt.grid(axis='y', alpha=0.75)
    plt.savefig(output_path)
    plt.close()
    return output_path

def get_feature_importance(model, feature_names, top_k=5):
    importance = model.get_feature_importance()
    feature_importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importance
    }).sort_values(by='importance', ascending=False)

    return {
        row['feature']: float(row['importance'])
        for _, row in feature_importance_df.head(top_k).iterrows()
    }
