import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from pathlib import Path
from decimal import Decimal
from typing import List, Dict, Any, Optional


class ParserCBRF:
    
    BASE_URL = "https://www.cbr.ru"
    STATISTICS_URL = "https://www.cbr.ru/statistics/"
    
    def __init__(self):
        self.data = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Создаем кроссплатформенный путь к директории для сохранения данных
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "parsed_data"
        self.data_dir.mkdir(exist_ok=True)
    
    def fetch_page(self, url: str) -> Optional[str]:

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            print(f"Ошибка при загрузке страницы {url}: {e}")
            return None
    
    def parse_statistics_page(self, html: str) -> List[Dict[str, Any]]:

        soup = BeautifulSoup(html, 'lxml')
        publications = []
        
        # Ищем все ссылки с атрибутом data-zoom-title (это статистические данные)
        links = soup.find_all('a', attrs={'data-zoom-title': True})
        
        print(f"Найдено ссылок с data-zoom-title: {len(links)}")
        
        for idx, link in enumerate(links, 1):
            try:
                # Извлекаем заголовок из атрибута
                title = link.get('data-zoom-title', '').strip()
                
                # Извлекаем URL
                href = link.get('href', '')
                if href and not href.startswith('http'):
                    href = self.BASE_URL + href
                
                # Извлекаем категорию
                category = link.get('data-zoom-referer-title', 'Статистика ЦБ РФ').strip()
                
                # Извлекаем теги
                tags = link.get('data-zoom-tags', '').strip()
                
                # Пробуем извлечь дату из заголовка или текста ссылки
                link_text = link.get_text(strip=True)
                date_str = self._extract_date_from_text(title + ' ' + link_text)
                parsed_date = self._parse_date(date_str) if date_str else None
                
                # Определяем тип файла
                file_type = self._get_file_type(href)
                
                publication = {
                    'id': idx,
                    'title': title,
                    'link': href,
                    'category': category,
                    'tags': tags,
                    'date': date_str,
                    'parsed_date': parsed_date,
                    'file_type': file_type,
                    'collected_at': datetime.now().isoformat()
                }
                
                publications.append(publication)
                
            except Exception as e:
                print(f"Ошибка при парсинге элемента: {e}")
                continue
        
        # Если не нашли данные, пробуем навигационные ссылки
        if not publications:
            print("Пробуем собрать навигационные ссылки...")
            publications = self._parse_navigation(soup)
        
        return publications
    
    def _parse_navigation(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:

        publications = []
        
        # Ищем навигационные элементы
        nav_items = soup.find_all('li', class_='page-nav_item')
        
        for idx, item in enumerate(nav_items, 1):
            link_elem = item.find('a')
            if link_elem:
                title = link_elem.get_text(strip=True)
                href = link_elem.get('href', '')
                
                if href and not href.startswith('http'):
                    href = self.BASE_URL + href
                
                publication = {
                    'id': idx,
                    'title': title,
                    'link': href,
                    'category': "Раздел статистики",
                    'tags': "Навигация",
                    'collected_at': datetime.now().isoformat()
                }
                
                publications.append(publication)
        
        return publications
    
    def _extract_date_from_text(self, text: str) -> Optional[str]:

        # Паттерны для поиска дат
        patterns = [
            r'(\d{2}\.\d{2}\.\d{4})',  # 16.10.2025
            r'на (\d{2}\.\d{2})',       # на 01.09
            r'(\d{4})\s*г\.',           # 2025 г.
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _get_file_type(self, url: str) -> str:

        url_lower = url.lower()
        
        if '.xlsx' in url_lower:
            return 'Excel (XLSX)'
        elif '.xls' in url_lower:
            return 'Excel (XLS)'
        elif '.pdf' in url_lower:
            return 'PDF'
        elif '.csv' in url_lower:
            return 'CSV'
        elif '.xml' in url_lower:
            return 'XML'
        elif '.zip' in url_lower:
            return 'ZIP'
        else:
            return 'HTML/Страница'
    
    def _parse_date(self, date_str: str) -> Optional[str]:

        if not date_str:
            return None
        
        # Пробуем разные форматы
        formats = [
            "%d.%m.%Y",
            "%d/%m/%Y",
            "%Y-%m-%d",
            "%d.%m.%y"
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.date().isoformat()
            except ValueError:
                continue
        
        return None
    
    def _serialize_data(self) -> List[Dict[str, Any]]:

        return [
            {
                key: (value if not isinstance(value, (datetime, Decimal)) 
                     else value.isoformat() if isinstance(value, datetime)
                     else str(value))
                for key, value in item.items()
            }
            for item in self.data
        ]
    
    def save_to_json(self, filename: str = "cbrf_statistics.json") -> Path:

        serialized_data = self._serialize_data()
        
        filepath = self.data_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serialized_data, f, ensure_ascii=False, indent=2)
        
        print(f"Данные успешно сохранены в: {filepath}")
        print(f"Всего записей: {len(serialized_data)}")
        
        return filepath
    
    def start(self) -> bool:

        print(f"Начинаем парсинг данных с {self.STATISTICS_URL}...")
        
        # Загружаем страницу
        html = self.fetch_page(self.STATISTICS_URL)
        
        if not html:
            print("Не удалось загрузить страницу")
            return False
        
        # Парсим данные
        self.data = self.parse_statistics_page(html)
        
        if not self.data:
            print("Не удалось извлечь данные со страницы")
            return False
        
        print(f"Успешно собрано {len(self.data)} записей")
        
        # Сохраняем в JSON
        self.save_to_json()
        
        return True


if __name__ == "__main__":
    # Запуск парсера
    parser = ParserCBRF()
    success = parser.start()
    
    if success:
        print("\n[OK] Парсинг завершен успешно!")
    else:
        print("\n[ERROR] Парсинг завершился с ошибками")

