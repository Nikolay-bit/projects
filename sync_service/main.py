import time
import logging
from dotenv import load_dotenv
import os
from connector.yandex_connector import Connector
from sync.sync_manager import SyncManager

load_dotenv(verbose=True)

print("YANDEX_TOKEN:", os.getenv("YANDEX_TOKEN"))


def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler("logs/sync_service.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

def setup_program():
    if not os.path.exists("logs"):
        os.makedirs("logs")
    if not os.path.exists("local_folder"):
        os.makedirs("local_folder")

def main():
    setup_program()
    setup_logger()
    logger = logging.getLogger("main")

    source_dir = os.getenv("SOURCE_DIRECTORY", "./local_folder")
    sync_interval = int(os.getenv("SYNC_INTERVAL_SECONDS", "10"))
    remote_sync_interval = int(os.getenv("REMOTE_SYNC_INTERVAL_SECONDS", "60"))
    token = os.getenv("YANDEX_TOKEN")

    if not token:
        logger.error("Токен Яндекс.Диска не указан в переменных окружения!")
        return

    connector = Connector(token)
    sync_manager = SyncManager(source_dir, connector)

    try:
        sync_manager.start()
        logger.info("Сервис синхронизации запущен")

        remote_sync_counter = 0
        while True:
            time.sleep(sync_interval)
            remote_sync_counter += sync_interval
            if remote_sync_counter >= remote_sync_interval:
                sync_manager.sync_remote_to_local()
                remote_sync_counter = 0

    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания, завершаем работу...")
    finally:
        sync_manager.stop()

if __name__ == "__main__":
    main()
