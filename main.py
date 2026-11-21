import json
from collections.abc import Iterator, Mapping
from dataclasses import asdict, dataclass
from types import MappingProxyType

from CONSTANS import MIN_YEAR
from errors import (
    CorruptedFileError,
    DuplicateIDError,
    InvalidItemError,
    ItemNotFoundError,
    UnsupportedVersionError,
)


@dataclass(frozen=True)
class MediaItem:
    """
    Шаблон медиаобъекта с уникальным ID, именем, категорией,
    годом выпуска, режиссером, общими просмотрами
    """
    id: str
    name: str
    category: str
    year: int
    director: str
    views: int

    def __post_init__(self) -> None:
        """
        Проверяет корректность атрибутов медиаобъектов

        Raises:
            InvalidItemError: Если атрибуты имеют неверный тип
                            или содержат недопустимые значения.
        """
        if not self.id.strip():
            raise InvalidItemError("ID не может быть пустым")

        if not self.name.strip():
            raise InvalidItemError("Name не может быть пустым")

        if not self.category.strip():
            raise InvalidItemError("Category не может быть пустым")

        if not self.director.strip():
            raise InvalidItemError("director не может быть пустым")

        if not isinstance(self.id, str):
            raise InvalidItemError("id должен быть строкой")

        if not isinstance(self.name, str):
            raise InvalidItemError("name должен быть строкой")

        if not isinstance(self.category, str):
            raise InvalidItemError("category должен быть строкой")

        if type(self.year) is not int:
            raise InvalidItemError("year должен быть целым числом")

        if type(self.director) is not str:
            raise InvalidItemError("director должен быть строкой")

        if type(self.views) is not int:
            raise InvalidItemError("views должен быть целым числом")

        if self.year < MIN_YEAR:
            raise InvalidItemError("Некорректный год")


class Catalog:
    """
    Управляет коллекцией медиаобъектов.

    Поддерживает добавление, удаление, поиск и хранение объектов,
    а также сохранение и загрузку данных в формате JSON
    """
    def __init__(self) -> None:
        """
        Инициализирует пустой каталог и индекс категорий
        """
        self._items: dict[str, MediaItem] = {}
        self._category_index: dict[str, dict[str, None]] = {}

    def add(self, item: MediaItem) -> None:
        """
        Добавляет новый медиаобъект

        Args:
            item: Добавляемый медиаобъект

        Raises:
            InvalidItemError: Если объект не является MediaItem
            DuplicateIDError: Если объект с таким ID уже существует
        """
        if not isinstance(item, MediaItem):
            raise InvalidItemError("Объект должен иметь тип MediaItem")

        if item.id in self._items:
            raise DuplicateIDError("Дубликат ID")

        self._items[item.id] = item
        self._category_index.setdefault(item.category, {})[item.id] = None

    def get(self, id: str) -> MediaItem:
        """
        Доставляет характеристики медиаобъекта по ID

        Args:
            id: ID нужного медиаобъекта

        Returns:
            MediaItem: Найденный медиаобъект

        Raises:
            ItemNotFoundError: Если объект с указанным ID отсутствует
        """
        if id not in self._items:
            raise ItemNotFoundError("Объект не найден")

        return self._items[id]

    def remove(self, id: str) -> None:
        """
        Удаляет медиаобъекта по ID

        Args:
            id: ID нужного медиаобъекта

        Raises:
            ItemNotFoundError: Если объект с указанным ID отсутствует

        """
        if id not in self._items:
            raise ItemNotFoundError("Объект не найден")

        item = self._items[id]

        del self._category_index[item.category][id]

        if not self._category_index[item.category]:
            del self._category_index[item.category]

        del self._items[id]

    def find_by_category(self, category: str) -> list[MediaItem]:
        """
        Доставляет группу медиаобъекта по категории

        Args:
            category: Необходимая категория

        Returns:
            list[MediaItem]: Список объектов указанной категории
            в порядке их добавления
        """
        ids = self._category_index.get(category, {})

        return [self._items[id] for id in ids]


    def find_by_name(self, name: str) -> list[MediaItem]:
        """
        Доставляет группу медиаобъекта по имени

        Args:
            name: Необходимое имя

        Returns:
            list[MediaItem]: Список медиаобъектов с указанным названием

        """
        result = []
        for item in self._items.values():
            if item.name.lower() == name.lower():
                result.append(item)
        return result

    def readonly_view(self) -> Mapping[str, MediaItem]:
        """
        Возвращает представление каталога только для чтения.

        Returns:
            MappingProxyType: Представление словаря медиаобъектов,
            запрещающее изменение записей через него
        """
        return MappingProxyType(self._items)

    def __len__(self) -> int:
        """
        Вычисляет длину каталога

        Returns:
            int: Количество медиаобъектов
        """
        return len(self._items)

    def __iter__(self) -> Iterator[MediaItem]:
        """
        Возвращает итератор медиаобъектов в порядке добавления

        Returns:
            Iterator[MediaItem]: Итератор по объектам каталога
        """
        return iter(self._items.values())

    def __contains__(self, item_id: str) -> bool:
        """
        Проверяет наличие медиаобъекта с указанным ID

        Args:
            item_id: ID медиаобъекта

        Returns:
            bool: True, если ID существует в каталоге, иначе False
        """
        return item_id in self._items

    def save(self) -> None:
        """
        Сохраняет каталог в файле
        """
        result: list[dict[str, object]] = []
        data = {
            "format_version": 1,
            "items": result
        }

        for item in self._items.values():
            result.append(asdict(item))

        with open("catalog.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load(self, file) -> None:
        """
        Загружает данные из JSON-файла

        Args:
            file: Путь к JSON-файлу

        Raises:
            CorruptedFileError: Если структура JSON или данные объектов
                некорректны.
            UnsupportedVersionError: Если версия формата не поддерживается
        """
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

        except json.JSONDecodeError as e:
            raise CorruptedFileError("JSON-файл повреждён") from e

        if not isinstance(data, dict):
            raise CorruptedFileError("Корень JSON должен быть словарём")

        if "format_version" not in data:
            raise CorruptedFileError("Отсутствует format_version")

        if "items" not in data:
            raise CorruptedFileError("Отсутствует items")

        if not isinstance(data["items"], list):
            raise CorruptedFileError("items должен быть списком")

        if data["format_version"] != 1:
            raise UnsupportedVersionError("Неподдерживаемая версия JSON")

        temp_catalog = Catalog()

        for item in data["items"]:
            if not isinstance(item, dict):
                raise CorruptedFileError(
                    "Элемент каталога должен быть словарём"
                )

            try:
                movie = MediaItem(**item)
                temp_catalog.add(movie)

            except (TypeError, InvalidItemError, DuplicateIDError) as e:
                raise CorruptedFileError(
                    "Некорректные данные в JSON"
                ) from e

        self._items.clear()
        self._items.update(temp_catalog._items)

        self._category_index.clear()
        self._category_index.update(temp_catalog._category_index)