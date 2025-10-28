import types


class DBConnection:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.connected = False

    def __enter__(self) -> "DBConnection":
        self.connected = True
        print(f"Подключение к базе данных '{self.db_name}' установлено.")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        self.connected = False
        print(f"Соединение с базой '{self.db_name}' закрыто.")
        if exc_type:
            print(f"Произошла ошибка: {exc_type.__name__} - {exc_val}")

    def execute(self, query: str) -> None:
        if not self.connected:
            raise ConnectionError("Нет активного подключения к базе данных.")
        print(f"Выполняется запрос: {query}")
