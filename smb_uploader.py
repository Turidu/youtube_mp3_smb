"""
Реализация загрузки файлов на SMB сервер
"""
import os
import logging
import hashlib
import smbclient
import smbclient.shutil
from interfaces import IFileUploader, ILogger


class SMBFileUploader(IFileUploader):
    """Класс для загрузки файлов на SMB сервер с поддержкой множественных конфигураций"""

    def __init__(self, logger: ILogger):
        self.logger = logger
        self.current_connection = None
        self.current_config = None

    def connect(self, smb_config: dict, folder_path: str) -> bool:
        """
        Подключается к SMB серверу с указанной конфигурацией
        
        Args:
            smb_config: Конфигурация SMB (server, share, username, password, domain)
            folder_path: Путь к папке на SMB сервере
            
        Returns:
            True если подключение успешно
        """
        return self._setup_connection(smb_config, folder_path)

    def upload_file(self, local_path: str, remote_filename: str) -> bool:
        """Загружает файл на SMB сервер"""
        if not self.current_config:
            self.logger.error("SMB подключение не настроено. Вызовите connect() сначала.")
            return False
            
        try:
            # Формируем полный путь к файлу на SMB сервере
            full_remote_path = os.path.join(self.current_config['full_path'], remote_filename).replace('/', '\\')
            
            self.logger.info(f"Загружаем файл: {local_path} -> {full_remote_path}")
            
            # Используем высокоуровневый интерфейс smbclient для копирования
            # Это автоматически обрабатывает чанки и все сложности SMB протокола
            smbclient.shutil.copyfile(local_path, full_remote_path)
            
            self.logger.info("Файл записан, проверяем целостность...")
            
            # Проверяем целостность файла
            if not self._verify_file_integrity(local_path, full_remote_path):
                self.logger.error("Файл поврежден при загрузке - удаляем и возвращаем ошибку")
                try:
                    smbclient.remove(full_remote_path)
                    self.logger.info("Поврежденный файл удален")
                except Exception as e:
                    self.logger.warning(f"Не удалось удалить поврежденный файл: {e}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке файла: {e}")
            return False

    def disconnect(self) -> None:
        """Отключается от SMB сервера"""
        try:
            self.current_config = None
            self.logger.info("Отключились от SMB сервера")
        except Exception as e:
            self.logger.warning(f"Ошибка при отключении от SMB сервера: {e}")

    def _setup_connection(self, smb_config: dict, folder_path: str) -> bool:
        """
        Настроить подключение к SMB серверу
        
        Args:
            smb_config: Конфигурация SMB (server, share, username, password, domain)
            folder_path: Путь к папке на SMB сервере
            
        Returns:
            True если подключение успешно
        """
        try:
            server = smb_config['server']
            share = smb_config['share']
            username = smb_config['username']
            password = smb_config['password']
            domain = smb_config.get('domain', '')
            
            if not username or not password:
                self.logger.error(f"Не указаны учетные данные для SMB сервера {server}")
                return False
            
            self.logger.info(f"Подключаемся к SMB серверу: {server}")
            
            # Настраиваем глобальные учетные данные для smbclient
            smbclient.ClientConfig(username=username, password=password, domain=domain)
            
            # Формируем базовый путь к SMB ресурсу
            base_path = f"\\\\{server}\\{share}"
            full_path = os.path.join(base_path, folder_path).replace('/', '\\')
            
            # Тестируем подключение
            try:
                smbclient.listdir(base_path)
                self.logger.info("Подключение к SMB серверу успешно установлено")
                
                # Создаем структуру папок если не существует
                self._create_directory_structure(full_path)
                
                # Сохраняем текущую конфигурацию
                self.current_config = {
                    'server': server,
                    'share': share,
                    'username': username,
                    'password': password,
                    'base_path': base_path,
                    'full_path': full_path
                }
                
                return True
                
            except Exception as e:
                self.logger.error(f"Не удалось подключиться к SMB серверу: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка при настройке SMB подключения: {e}")
            return False

    def _verify_file_integrity(self, local_path: str, remote_path: str) -> bool:
        """
        Проверяет целостность файла путем сравнения MD5 хешей
        
        Args:
            local_path: Путь к локальному файлу
            remote_path: Путь к файлу на SMB сервере
            
        Returns:
            True если файлы идентичны
        """
        try:
            # Вычисляем хеш локального файла
            local_hash = self._calculate_file_hash(local_path)
            self.logger.info(f"Хеш локального файла: {local_hash}")
            
            # Вычисляем хеш файла на SMB
            remote_hash = self._calculate_remote_file_hash(remote_path)
            self.logger.info(f"Хеш файла на SMB: {remote_hash}")
            
            if local_hash == remote_hash:
                self.logger.info("✅ Хеши совпадают - файл загружен корректно!")
                return True
            else:
                self.logger.error("❌ Хеши не совпадают - файл поврежден при загрузке!")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка при проверке целостности файла: {e}")
            return False

    def _calculate_file_hash(self, file_path: str) -> str:
        """Вычисляет MD5 хеш локального файла"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _calculate_remote_file_hash(self, remote_path: str) -> str:
        """Вычисляет MD5 хеш файла на SMB сервере"""
        hash_md5 = hashlib.md5()
        
        self.logger.info("Начинаем чтение файла с SMB для вычисления хеша...")
        
        # Используем smbclient для чтения файла
        with smbclient.open_file(remote_path, mode='rb') as f:
            total_read = 0
            while True:
                chunk_data = f.read(8192)
                if not chunk_data:
                    break
                hash_md5.update(chunk_data)
                total_read += len(chunk_data)
                if total_read % (80 * 1024) == 0:  # Логируем каждые 80KB
                    self.logger.info(f"Прочитано: {total_read} байт")
        
        self.logger.info(f"Чтение завершено, всего прочитано: {total_read} байт")
        return hash_md5.hexdigest()

    def _create_directory_structure(self, full_path: str):
        """Создает структуру папок на SMB сервере если она не существует"""
        try:
            # Проверяем существование папки
            if smbclient.path.exists(full_path):
                self.logger.info(f"Папка готова: {os.path.basename(full_path)}")
                return
            
            # Создаем папку рекурсивно
            smbclient.makedirs(full_path)
            self.logger.info(f"Папка создана: {full_path}")
            
        except Exception as e:
            # Папка может уже существовать, это нормально
            self.logger.info(f"Папка {full_path} уже существует или создана: {e}")
