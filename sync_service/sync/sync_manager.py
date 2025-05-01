import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SyncEventHandler(FileSystemEventHandler):
    def __init__(self, src_dir, connector):
        self.src_dir = os.path.abspath(src_dir)
        self.connector = connector
        self.logger = logging.getLogger(__name__)

    def on_modified(self, event):
        if not event.is_directory:
            self.sync(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self.sync(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.delete_remote(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.delete_remote(event.src_path)
            self.sync(event.dest_path)

    def sync(self, local_path):
        relative_path = os.path.relpath(local_path, self.src_dir)
        remote_path = f"/{relative_path.replace(os.sep, '/')}"
        self.logger.info(f"Синхронизация файла {local_path} -> {remote_path}")
        self.connector.upload_file(local_path, remote_path)

    def delete_remote(self, local_path):
        relative_path = os.path.relpath(local_path, self.src_dir)
        remote_path = f"/{relative_path.replace(os.sep, '/')}"
        self.logger.info(f"Удаление файла на Яндекс.Диске: {remote_path}")
        self.connector.delete_file(remote_path)

class SyncManager:
    def __init__(self, src_dir, connector):
        self.src_dir = os.path.abspath(src_dir)
        self.connector = connector
        self.observer = Observer()
        self.logger = logging.getLogger(__name__)

    def start(self):
        event_handler = SyncEventHandler(self.src_dir, self.connector)
        self.observer.schedule(event_handler, self.src_dir, recursive=True)
        self.observer.start()
        self.logger.info(f"Запущен мониторинг папки: {self.src_dir}")

    def stop(self):
        self.observer.stop()
        self.observer.join()
        self.logger.info("Мониторинг остановлен")

    def sync_remote_to_local(self):
        """
        Периодически вызывается для синхронизации изменений с Яндекс.Диска на локальную машину.
        Здесь реализуем простой обход файлов на Яндекс.Диске и загрузку отсутствующих или обновлённых.
        """
        self.logger.info("Запущена синхронизация с Яндекс.Диска на локальную машину")
        try:
            remote_files = self.connector.list_files("/")
            for remote_file in remote_files:
                remote_path = remote_file["path"]
                relative_path = remote_path.lstrip("/")
                local_path = os.path.join(self.src_dir, relative_path)
                if (not os.path.exists(local_path) or
                    self.connector.is_remote_newer(remote_path, local_path)):
                    self.logger.info(f"Загрузка файла с Яндекс.Диска: {remote_path} -> {local_path}")
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                    self.connector.download_file(remote_path, local_path)
        except Exception as e:
            self.logger.error(f"Ошибка при синхронизации с Яндекс.Диска: {e}")
