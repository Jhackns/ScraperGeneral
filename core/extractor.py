import asyncio
import aiohttp
import os
import json
from pathlib import Path
from core.scout import scout
from core.storage import storage

class ExtractorEngine:
    def __init__(self):
        self.semaphore = asyncio.Semaphore(5) # Límite de 5 descargas simultáneas

    async def download_file(self, session: aiohttp.ClientSession, url: str, category_dir: Path):
        """Descarga un archivo individual con control de concurrencia."""
        async with self.semaphore:
            try:
                filename = url.split('/')[-1].split('?')[0]
                if not filename:
                    filename = "item_descargado"
                
                target_path = storage.get_safe_filepath(category_dir, filename)
                
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        # Mejorar legibilidad si es un JSON de la red
                        if 'application/json' in response.headers.get('content-type', '').lower():
                            try:
                                data = await response.json()
                                with open(target_path, "w", encoding="utf-8") as f:
                                    json.dump(data, f, indent=4, ensure_ascii=False)
                                return True
                            except Exception:
                                pass # Si falla el parseo, lo guarda como binario plano
                        
                        content = await response.read()
                        with open(target_path, "wb") as f:
                            f.write(content)
                        return True
            except Exception as e:
                print(f"[Extractor] Error descargando {url}: {e}")
            return False

    async def run_extraction(self, target_url: str, selected_categories: list, update_callback=None):
        print(f"[Extractor] Iniciando fase masiva para: {target_url}")
        
        async with aiohttp.ClientSession(headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }) as session:
            
            tasks = []
            for category in selected_categories:
                category_dir = storage.get_category_path(target_url, category)
                urls = scout.resources.get(category, set())
                
                for url in urls:
                    if url.startswith("http"):
                        tasks.append(self.download_file(session, url, category_dir))
                    elif category == "Tablas":
                        await self._extract_table_to_csv(url, category_dir)
                    elif category == "Artículos":
                        await self._extract_articles_to_json(url, category_dir)

            if tasks:
                results = await asyncio.gather(*tasks)
                success_count = sum(1 for r in results if r)
                print(f"[Extractor] Finalizado. Exitos: {success_count}/{len(tasks)}")
                if update_callback:
                    update_callback(f"Completado: {success_count} archivos guardados.")

    async def _extract_table_to_csv(self, table_id: str, category_dir: Path):
        if not scout.page: return
        try:
            index = int(table_id.split('_')[-1])
            filename = f"tabla_{index}.csv"
            target_path = storage.get_safe_filepath(category_dir, filename)
            
            rows = await scout.page.evaluate(f"""
                () => {{
                    const table = document.querySelectorAll('table')[{index}];
                    if (!table) return [];
                    return Array.from(table.rows).map(row => 
                        Array.from(row.cells).map(cell => cell.innerText.trim())
                    );
                }}
            """)
            
            if rows:
                import csv
                with open(target_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerows(rows)
        except Exception as e:
            print(f"[Extractor] Error extrayendo tabla: {e}")

    async def _extract_articles_to_json(self, art_id: str, category_dir: Path):
        """Extrae el contenido textual estructurado de la noticia (Título, Cuerpo, Metadatos)."""
        if not scout.page: return
        try:
            target_path = storage.get_safe_filepath(category_dir, "contenido_articulo.json")
            
            data = await scout.page.evaluate("""
                () => {
                    const getMeta = (name) => {
                        const el = document.querySelector(`meta[property="${name}"], meta[name="${name}"]`);
                        return el ? el.content : "";
                    };
                    
                    return {
                        "titulo": document.querySelector('h1') ? document.querySelector('h1').innerText.trim() : getMeta("og:title"),
                        "url": window.location.href,
                        "fecha_extraccion": new Date().toLocaleString(),
                        "metadatos": {
                            "descripcion": getMeta("og:description") || getMeta("description"),
                            "autor": getMeta("author") || getMeta("article:author"),
                            "sitio": getMeta("og:site_name")
                        },
                        "cuerpo_texto": Array.from(document.querySelectorAll('article p, .content p, .body p, .story-contents p'))
                                            .map(p => p.innerText.trim())
                                            .filter(t => t.length > 30) // Filtra textos irrelevantes o cortos
                                            .join('\\n\\n')
                    }
                }
            """)
            
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[Extractor] Error extrayendo artículo: {e}")

extractor = ExtractorEngine()
