import os
import sys
sys.path.append(os.path.abspath('./src'))
import logging
import pandas as pd
from preprocessing import run_preproc
from scorer import get_predictions, model
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import threading
import config
import artifacts

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class processingService:
    def __init__(self):
        logger.info('Initializing processingService...')
        self.input_dir = config.INPUT_DIR
        self.output_dir = config.OUTPUT_DIR
        self.train = pd.read_csv(config.TRAIN_PATH)
        self.processed_files = set()
        logger.info('processingService initialized')
    def process_file(self, input_file_path: str):
        try:
            logger.info('Processing file: %s', input_file_path)
            input_df = pd.read_csv(input_file_path)
            logger.info('Starting preprocessing')
            processed_df = run_preproc(self.train, input_df)
            logger.info('Making prediction')
            submission = get_predictions(processed_df, input_file_path)

            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(os.path.basename(input_file_path))[0]

            logger.info('Calculating top feature importances')
            top_features = artifacts.get_feature_importance(model, processed_df.columns, top_k=5)
            top_features_path = os.path.join(
                config.TOP_FEATURES_PATH,
                f'top_features_{timestamp}_{base_name}.json'
            )
            saved_top_features_path = artifacts.save_feature_importance(top_features, top_features_path)
            logger.info('Top feature importances saved to: %s', saved_top_features_path)

            logger.info('Saving predicted score distribution plot')
            score_distribution_path = artifacts.save_preds_distribution(
                submission['predicted_score'],
                os.path.join(config.PREDS_STATS_PATH, f'prediction_distribution_{timestamp}_{base_name}.png')
            )
            logger.info('Predicted score distribution saved to: %s', score_distribution_path)

            logger.info('Preparing submission file')
            output_filename = f"predictions_{timestamp}_{base_name}.csv"
            output_path = os.path.join(self.output_dir, output_filename)
            submission.to_csv(output_path, index=False)
            logger.info('Predictions saved to: %s', output_path)
            self.processed_files.add(os.path.abspath(input_file_path))
        except Exception as e:
            logger.error('Error processing file %s: %s', input_file_path, e, exc_info=True)
            return

    def process_single_file(self):
        try:
            csv_files = [f for f in os.listdir(self.input_dir) if f.endswith('.csv')]
            if not csv_files:
                return
            last_input_file = max(csv_files, key=lambda x: os.path.getctime(os.path.join(self.input_dir, x)))
            input_file_path = os.path.join(self.input_dir, last_input_file)
            if os.path.abspath(input_file_path) in self.processed_files:
                return
            self.process_file(input_file_path)
        except Exception as e:
            logger.error('Error in process_single_file: %s', e, exc_info=True)
            return

    def process_existing_on_startup(self):
        try:
            csv_files = [os.path.join(self.input_dir, f) for f in os.listdir(self.input_dir) if f.endswith('.csv')]
            csv_files.sort(key=lambda x: os.path.getctime(x))
            for path in csv_files:
                if os.path.abspath(path) not in self.processed_files:
                    self.process_file(path)
        except Exception as e:
            logger.error('Error processing existing files on startup: %s', e, exc_info=True)
            return
        
class FileHandler(FileSystemEventHandler):
    def __init__(self, service):
        self.service = service

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".csv"):
            try:
                self.service.process_file(event.src_path)
            except Exception:
                logger.exception('Error handling created event for %s', event.src_path)

if __name__ == "__main__":
    service = processingService()
    service.process_existing_on_startup()
    event_handler = FileHandler(service)
    observer = Observer()
    observer.schedule(event_handler, path=config.INPUT_DIR, recursive=False)
    observer.start()
    logger.info('Monitoring started on directory: %s', config.INPUT_DIR)
    def periodic_scanner(svc, interval=10):
        while True:
            try:
                for f in os.listdir(svc.input_dir):
                    if f.endswith('.csv'):
                        path = os.path.join(svc.input_dir, f)
                        if os.path.abspath(path) not in svc.processed_files:
                            svc.process_file(path)
            except Exception:
                logger.exception('Error in periodic scanner')
            time.sleep(interval)

    scanner_thread = threading.Thread(target=periodic_scanner, args=(service, 5), daemon=True)
    scanner_thread.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('Service stopped by user')
        observer.stop()
    observer.join()
