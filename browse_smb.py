"""
Скрипт для просмотра файлов на SMB сервере
"""
import sys
from config import SMB_SERVER, SMB_SHARE, SMB_USERNAME, SMB_PASSWORD, SMB_DOMAIN
from logger import ConsoleLogger
from smb_uploader import SMBFileUploader
from smbprotocol.open import Open, CreateDisposition, CreateOptions, ShareAccess, DirectoryAccessMask, ImpersonationLevel
from smbprotocol.query_info import QueryInfoFlags, FileInformationClass


def list_smb_files():
    """Показать файлы на SMB сервере"""
    print("BROWSING SMB SERVER FILES")
    print("=" * 40)
    
    logger = ConsoleLogger("SMBBrowser")
    uploader = SMBFileUploader(
        SMB_SERVER, SMB_SHARE, SMB_USERNAME, SMB_PASSWORD, logger, SMB_DOMAIN
    )
    
    try:
        if not uploader.connect():
            print("[ERROR] Could not connect to SMB server")
            return
        
        print(f"Connected to: \\\\{SMB_SERVER}\\{SMB_SHARE}")
        print("\nFiles in root directory:")
        
        # Пытаемся открыть корневую директорию для чтения
        try:
            root_dir = Open(uploader.tree, "")
            root_dir.create(
                ImpersonationLevel.Impersonation,
                DirectoryAccessMask.GENERIC_READ,
                0,  # file_attributes
                ShareAccess.FILE_SHARE_READ | ShareAccess.FILE_SHARE_WRITE,
                CreateDisposition.FILE_OPEN,
                CreateOptions.FILE_DIRECTORY_FILE
            )
            
            # Получаем список файлов
            files = root_dir.query_directory("*", FileInformationClass.FileIdBothDirectoryInformation)
            
            for file_info in files:
                if file_info.file_name not in ['.', '..']:
                    file_type = "DIR" if file_info.file_attributes & 0x10 else "FILE"
                    size = file_info.end_of_file if hasattr(file_info, 'end_of_file') else 0
                    print(f"  {file_type:4} {file_info.file_name:50} {size:>10} bytes")
            
            root_dir.close()
            
        except Exception as e:
            print(f"[ERROR] Could not list files: {e}")
            
        # Проверяем папку Music если она существует
        print("\nChecking Music folder:")
        try:
            music_dir = Open(uploader.tree, "Music")
            music_dir.create(
                ImpersonationLevel.Impersonation,
                DirectoryAccessMask.GENERIC_READ,
                0,
                ShareAccess.FILE_SHARE_READ | ShareAccess.FILE_SHARE_WRITE,
                CreateDisposition.FILE_OPEN,
                CreateOptions.FILE_DIRECTORY_FILE
            )
            
            files = music_dir.query_directory("*", FileInformationClass.FileIdBothDirectoryInformation)
            
            for file_info in files:
                if file_info.file_name not in ['.', '..']:
                    file_type = "DIR" if file_info.file_attributes & 0x10 else "FILE"
                    size = file_info.end_of_file if hasattr(file_info, 'end_of_file') else 0
                    print(f"  {file_type:4} {file_info.file_name:50} {size:>10} bytes")
            
            music_dir.close()
            
        except Exception as e:
            print(f"Music folder not found or error: {e}")
            
    finally:
        uploader.disconnect()


if __name__ == "__main__":
    list_smb_files()
