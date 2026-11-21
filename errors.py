class CatalogError(Exception):
    pass
class DuplicateIDError(CatalogError):
    pass
class InvalidItemError(CatalogError):
    pass
class ItemNotFoundError(CatalogError):
    pass
class UnsupportedVersionError(CatalogError):
    pass
class CorruptedFileError(CatalogError):
    pass
