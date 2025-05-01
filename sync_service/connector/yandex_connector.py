import yadisk
import logging
import os
from datetime import datetime, timezone

class Connector:
    def __init__(self, token):
        self.logger = logging.getLogger(__name__)
        self.y = yadisk.YaDisk(token=token)
        self.logger.info("Яндекс.Диск коннектор инициализирован")

    def upload_file(self, local_path, remote_path):
        try:
            if self.y.exists(remote_path):
                self.y.remove(remote_path)
                self.logger.info(f"Удалён файл на Яндекс.Диске: {remote_path}")
            self.y.upload(local_path, remote_path)
            self.logger.info(f"Загружен файл {local_path} в {remote_path}")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки файла {local_path}: {e}")

    def delete_file(self, remote_path):
        try:
            if self.y.exists(remote_path):
                self.y.remove(remote_path)
                self.logger.info(f"Удалён файл на Яндекс.Диске: {remote_path}")
            else:
                self.logger.info(f"Файл для удаления не найден на Яндекс.Диске: {remote_path}")
        except Exception as e:
            self.logger.error(f"Ошибка удаления файла {remote_path}: {e}")

    def list_files(self, remote_dir):
        """
        Рекурсивно получить список всех файлов в remote_dir.
        Возвращает список словарей с информацией о файлах.
        """
        files = []
        try:
            def walk(path):
                for item in self.y.listdir(path):
                    if item["type"] == "dir":
                        walk(item["path"])
                    else:
                        files.append(item)
            walk(remote_dir)
        except Exception as e:
            self.logger.error(f"Ошибка получения списка файлов: {e}")
        return files

    def is_remote_newer(self, remote_path, local_path):
        """
        Проверяет, новее ли файл на Яндекс.Диске, чем локальный.
        Сравниваем по времени изменения.
        """
        try:
            meta = self.y.get_meta(remote_path)
            remote_mtime = datetime.strptime(meta.modified, "%Y-%m-%dT%H:%M:%S%z")
            local_mtime = datetime.fromtimestamp(os.path.getmtime(local_path), timezone.utc)
            return remote_mtime > local_mtime
        except Exception as e:
            self.logger.error(f"Ошибка сравнения времени файлов {remote_path} и {local_path}: {e}")
            return False

    def download_file(self, remote_path, local_path):
        try:
            self.y.download(remote_path, local_path)
            self.logger.info(f"Скачан файл {remote_path} в {local_path}")
        except Exception as e:
            self.logger.error(f"Ошибка скачивания файла {remote_path}: {e}")
