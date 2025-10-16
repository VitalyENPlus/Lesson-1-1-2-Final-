

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import Counter
from decimal import Decimal


class CBRFDataAnalyzer:
    
    def __init__(self, data_path: Optional[str] = None):

        self.data = []
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "parsed_data"
        
        if data_path:
            self.data_path = Path(data_path)
        else:
            self.data_path = self.data_dir / "cbrf_statistics.json"
        
        if self.data_path.exists():
            self.load_data()
    
    def load_data(self, filepath: Optional[str] = None) -> bool:

        Загрузка данных из JSON файла (десериализация)
        
        Args:
            filepath: Путь к JSON файлу. Если None, используется self.data_path
            
        Returns:
            True если загрузка успешна, False в противном случае

        if filepath:
            file_to_load = Path(filepath)
        else:
            file_to_load = self.data_path
        
        try:
            with open(file_to_load, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # Десериализация: преобразуем данные обратно в нужные типы
            self.data = self._deserialize_data(raw_data)
            
            print(f"Загружено {len(self.data)} записей из {file_to_load}")
            return True
            
        except FileNotFoundError:
            print(f"Файл {file_to_load} не найден")
            return False
        except json.JSONDecodeError as e:
            print(f"Ошибка при чтении JSON: {e}")
            return False
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            return False
    
    def _deserialize_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

        Десериализация данных из JSON
        Преобразует строковые даты обратно в datetime объекты
        
        Args:
            raw_data: Сырые данные из JSON
            
        Returns:
            Десериализованные данные

        return [
            {
                key: self._parse_datetime(value) if key in ('collected_at', 'parsed_date') 
                     and isinstance(value, str) and value
                     else value
                for key, value in item.items()
            }
            for item in raw_data
        ]
    
    def _parse_datetime(self, date_str: str) -> Optional[datetime]:

        if not date_str:
            return None
        
        try:
            if 'T' in date_str:
                return datetime.fromisoformat(date_str)
            else:
                # Парсим как дату
                return datetime.fromisoformat(date_str + 'T00:00:00')
        except (ValueError, AttributeError):
            return date_str
    
    def get_all_data(self) -> List[Dict[str, Any]]:
        """
        Получить все данные
        
        Returns:
            Список всех записей
        """
        return self.data
    
    def get_by_id(self, record_id: Any) -> Optional[Dict[str, Any]]:

        for item in self.data:
            if str(item.get('id')) == str(record_id):
                return item
        return None
    
    def filter_by_category(self, category: str) -> List[Dict[str, Any]]:

        return [
            item for item in self.data 
            if category.lower() in item.get('category', '').lower()
        ]
    
    def filter_by_date(self, start_date: Optional[str] = None, 
                       end_date: Optional[str] = None) -> List[Dict[str, Any]]:

        filtered = []
        
        for item in self.data:
            parsed_date = item.get('parsed_date')
            
            if not parsed_date:
                continue
            
            if isinstance(parsed_date, datetime):
                date_str = parsed_date.date().isoformat()
            else:
                date_str = str(parsed_date)
            
            if start_date and date_str < start_date:
                continue
            if end_date and date_str > end_date:
                continue
            
            filtered.append(item)
        
        return filtered
    
    def search_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:

        keyword_lower = keyword.lower()
        return [
            item for item in self.data
            if keyword_lower in item.get('title', '').lower()
        ]
    
    def get_categories(self) -> List[str]:

        categories = {item.get('category', 'Неизвестно') for item in self.data}
        return sorted(categories)
    
    def get_category_statistics(self) -> Dict[str, int]:

        categories = [item.get('category', 'Неизвестно') for item in self.data]
        return dict(Counter(categories))
    
    def get_records_count(self) -> int:

        return len(self.data)
    
    def get_latest_records(self, limit: int = 10) -> List[Dict[str, Any]]:

        # Сортируем по дате сбора данных
        sorted_data = sorted(
            self.data,
            key=lambda x: x.get('collected_at', ''),
            reverse=True
        )
        return sorted_data[:limit]
    
    def export_to_json(self, filepath: str, filtered_data: Optional[List[Dict[str, Any]]] = None):

        data_to_export = filtered_data if filtered_data is not None else self.data
        
        serialized_data = [
            {
                key: value.isoformat() if isinstance(value, datetime) else value
                for key, value in item.items()
            }
            for item in data_to_export
        ]
        
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serialized_data, f, ensure_ascii=False, indent=2)
        
        print(f"Данные экспортированы в {output_path}")
    
    def print_summary(self):

        print("\n" + "="*60)
        print("СВОДКА ПО ДАННЫМ ЦБ РФ")
        print("="*60)
        print(f"Общее количество записей: {self.get_records_count()}")
        print(f"\nКатегории:")
        
        stats = self.get_category_statistics()
        for category, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {category}: {count} записей")
        
        print("\nПоследние 5 записей:")
        for idx, record in enumerate(self.get_latest_records(5), 1):
            print(f"  {idx}. {record.get('title', 'Без названия')[:60]}...")
        
        print("="*60 + "\n")


if __name__ == "__main__":
    # Пример
    analyzer = CBRFDataAnalyzer()
    
    if analyzer.get_records_count() > 0:
        # Выводим сводку
        analyzer.print_summary()
        
        print("\nПример поиска по ключевому слову 'кредит':")
        results = analyzer.search_by_keyword("кредит")
        for item in results[:3]:
            print(f"  - {item.get('title')}")
        
        print(f"\nНайдено записей: {len(results)}")
    else:
        print("Нет данных для анализа. Сначала запустите парсер.")
