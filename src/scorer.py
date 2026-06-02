import pandas as pd
import logging
from catboost import CatBoostClassifier
import config

logger = logging.getLogger(__name__)

logger.info('Importing pretrained model...')

model = CatBoostClassifier()
model.load_model(f'./{config.MODEL_PATH}')
logger.info('Pretrained model imported successfully...')

def get_predictions(dt, path_to_file):
    logger.info('Making predictions')
    
    submission = pd.DataFrame({
        'index':  pd.read_csv(path_to_file).index,
        'prediction': (model.predict_proba(dt)[:, 1] > config.THRESHOLD) * 1
    })
    logger.info('Prediction complete for file: %s', path_to_file)

    return submission