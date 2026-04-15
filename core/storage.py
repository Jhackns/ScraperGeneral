import os
import re
import tldextract
from pathlib import Path

class StorageManager:
    def __init__(self, base_name="DatosExtraidos"):
        self.base_path = Path(os.getcwd()) / base_name
        self.max_path_limit = 250 # Windows safe limit

    def _sanitize_name(self, name: str) -> str:
        """Elimina caracteres no permitidos en nombres de carpetas/archivos."""
        return re.sub(r'[<>:"/\\|?*]', '_', name)

    def get_domain_path(self, url: str) -> Path:
        """Extrae el dominio y genera la ruta base del proyecto."""
        extract = tldextract.extract(url)
        domain_name = f"{extract.domain}_{extract.suffix}".replace('.', '_')
        path = self.base_path / self._sanitize_name(domain_name)
        return path

    def get_category_path(self, url: str, category: str) -> Path:
        """Genera y crea la carpeta de categoría (Imágenes, Videos, etc)."""
        domain_path = self.get_domain_path(url)
        category_path = domain_path / self._sanitize_name(category)
        
        # Crear directorios si no existen
        category_path.mkdir(parents=True, exist_ok=True)
        return category_path

    def get_safe_filepath(self, folder: Path, filename: str) -> str:
        """
        Asegura que la ruta total no exceda los límites de Windows.
        Si es muy larga, trunca el nombre del archivo manteniendo la extensión.
        """
        # Sanatizar nombre de archivo
        filename = self._sanitize_name(filename)
        full_path = str(folder / filename)

        if len(full_path) > self.max_path_limit:
            ext = "".join(Path(filename).suffixes)
            # Truncar nombre: limite - longitud carpeta - longitud extensión - margen
            allowed_len = self.max_path_limit - len(str(folder)) - len(ext) - 5
            new_name = filename[:allowed_len] + ext
            full_path = str(folder / new_name)

        return full_path

storage = StorageManager()
