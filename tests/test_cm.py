from dmg.context_manager import DBConnection


class TestDBConnection:
    def test_context_manager_connection(self):
        db_name = "test_db"

        with DBConnection(db_name) as db:
            assert db.connected is True
            assert db.db_name == db_name

        assert db.connected is False

    def test_execute_query_success(self, capsys):
        with DBConnection("test_db") as db:
            db.execute("SELECT * FROM users")

            captured = capsys.readouterr()
            assert "Выполняется запрос: SELECT * FROM users" in captured.out

    def test_context_manager_output(self, capsys):
        """Тест вывода сообщений при работе с контекстным менеджером"""
        db_name = "my_database"

        with DBConnection(db_name) as db:
            db.execute("INSERT INTO table VALUES (1)")

        captured = capsys.readouterr()
        output = captured.out

        assert f"Подключение к базе данных '{db_name}' установлено." in output
        assert "Выполняется запрос: INSERT INTO table VALUES (1)" in output
        assert f"Соединение с базой '{db_name}' закрыто." in output

    def test_multiple_connections(self):
        """Тест работы с несколькими соединениями"""
        with DBConnection("db1") as conn1, DBConnection("db2") as conn2:
            assert conn1.connected is True
            assert conn2.connected is True
            assert conn1.db_name == "db1"
            assert conn2.db_name == "db2"

        assert conn1.connected is False
        assert conn2.connected is False

    def test_reuse_connection_object(self):
        db = DBConnection("reusable_db")

        with db:
            assert db.connected is True
            db.execute("QUERY 1")

        assert db.connected is False

        with db:
            assert db.connected is True
            db.execute("QUERY 2")

        assert db.connected is False

    def test_different_database_names(self):
        test_cases = [
            "simple_db",
            "db_with_underscores",
            "DB_WITH_UPPERCASE",
            "db-with-dashes",
            "db123_with_numbers",
        ]

        for db_name in test_cases:
            with DBConnection(db_name) as db:
                assert db.db_name == db_name
                assert db.connected is True
            assert db.connected is False
