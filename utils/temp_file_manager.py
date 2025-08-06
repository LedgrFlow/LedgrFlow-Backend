import os
import tempfile
import uuid
from pathlib import Path
from typing import Optional

class TempFileManager:
    """Gestor de archivos temporales para análisis de ledger"""
    
    def __init__(self, temp_dir: str = "temps"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
    
    def create_temp_file(self, content: str, extension: str = ".ledger") -> str:
        """
        Crea un archivo temporal con el contenido especificado
        
        Args:
            content: Contenido del archivo
            extension: Extensión del archivo (default: .ledger)
            
        Returns:
            Ruta completa del archivo temporal creado
        """
        # Generar nombre único para el archivo temporal
        temp_filename = f"ledger_{uuid.uuid4().hex}{extension}"
        temp_file_path = self.temp_dir / temp_filename
        
        # Escribir contenido al archivo
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(temp_file_path)
    
    def cleanup_temp_file(self, file_path: str) -> bool:
        """
        Elimina un archivo temporal
        
        Args:
            file_path: Ruta del archivo a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False
    
    def cleanup_all_temp_files(self) -> int:
        """
        Elimina todos los archivos temporales en el directorio
        
        Returns:
            Número de archivos eliminados
        """
        count = 0
        try:
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    file_path.unlink()
                    count += 1
        except Exception:
            pass
        return count
    
    def get_temp_file_info(self, file_path: str) -> Optional[dict]:
        """
        Obtiene información sobre un archivo temporal
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Diccionario con información del archivo o None si no existe
        """
        try:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                return {
                    'path': file_path,
                    'size': stat.st_size,
                    'created': stat.st_ctime,
                    'modified': stat.st_mtime
                }
            return None
        except Exception:
            return None 