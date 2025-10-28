import pytest
import time
from dmg.main import cache_result, get_user_data


class TestCacheResult:
    def test_cache_decorator_functionality(self, capsys):
        """Тест базовой функциональности кэширования"""
        # Первый вызов - должен быть из базы
        start_time = time.time()
        result1 = get_user_data(123)
        execution_time1 = time.time() - start_time

        assert result1 == 123
        assert execution_time1 >= 2  # Должно быть ~2 секунды

        # Проверяем вывод
        output1 = capsys.readouterr()
        assert "взят из базы 123" in output1.out

        # Второй вызов - должен быть из кэша (быстрее)
        start_time = time.time()
        result2 = get_user_data(123)
        execution_time2 = time.time() - start_time

        assert result2 == 123
        assert execution_time2 < 0.1  # Должно быть мгновенно

        # Проверяем вывод
        output2 = capsys.readouterr()
        assert "взят из кеша 123" in output2.out

    def test_different_user_ids(self, capsys):
        """Тест что разные user_id кэшируются отдельно"""
        # Первый пользователь
        result1 = get_user_data(1)
        output1 = capsys.readouterr()
        assert "взят из базы 1" in output1.out

        # Второй пользователь
        result2 = get_user_data(2)
        output2 = capsys.readouterr()
        assert "взят из базы 2" in output2.out

        # Снова первый пользователь - должен быть из кэша
        result3 = get_user_data(1)
        output3 = capsys.readouterr()
        assert "взят из кеша 1" in output3.out

        assert result1 == 1
        assert result2 == 2
        assert result3 == 1

    def test_keyword_arguments(self, capsys):
        """Тест работы с keyword arguments"""
        # Вызов с keyword argument
        result1 = get_user_data(user_id=999)
        output1 = capsys.readouterr()
        assert "взят из базы 999" in output1.out

        # Повторный вызов - из кэша
        result2 = get_user_data(user_id=999)
        output2 = capsys.readouterr()
        assert "взят из кеша 999" in output2.out

        assert result1 == 999
        assert result2 == 999

    def test_mixed_arguments_caching(self, capsys):
        """Тест что позиционные и keyword аргументы используют один кэш"""
        # Позиционный аргумент
        result1 = get_user_data(777)
        output1 = capsys.readouterr()
        assert "взят из базы 777" in output1.out

        # Keyword аргумент с тем же user_id - должен быть из кэша
        result2 = get_user_data(user_id=777)
        output2 = capsys.readouterr()
        assert "взят из кеша 777" in output2.out

        assert result1 == 777
        assert result2 == 777

    def test_no_arguments_error(self):
        """Тест ошибки при вызове без аргументов"""
        with pytest.raises(ValueError, match="Must provide user_id"):
            get_user_data()

    def test_cache_independence_between_functions(self):
        """Тест что разные функции имеют независимые кэши"""

        # Создаем вторую функцию с тем же декоратором
        @cache_result
        def get_user_name(user_id: int) -> int:
            time.sleep(1)
            return user_id * 10

        # Вызываем обе функции с одинаковым user_id
        result1 = get_user_data(100)  # Должен вернуть 100
        result2 = get_user_name(100)  # Должен вернуть 1000

        assert result1 == 100
        assert result2 == 1000

    def test_multiple_calls_same_id(self, capsys):
        """Тест многократных вызовов с одним user_id"""
        user_id = 555

        # Три вызова с одним user_id
        for i in range(3):
            result = get_user_data(user_id)
            assert result == user_id

        # Проверяем что только первый был из базы, остальные из кэша
        outputs = capsys.readouterr().out.strip().split("\n")
        assert len(outputs) == 3
        assert "взят из базы 555" in outputs[0]
        assert all("взят из кеша 555" in output for output in outputs[1:])

    def test_cache_persistence(self, capsys):
        """Тест что кэш сохраняется между вызовами"""
        # Первый вызов
        result1 = get_user_data(888)
        output1 = capsys.readouterr()
        assert "взят из базы 888" in output1.out

        # Второй вызов (другой функции, но тот же модуль)
        result2 = get_user_data(888)
        output2 = capsys.readouterr()
        assert "взят из кеша 888" in output2.out

        # Третий вызов (через некоторое время)
        time.sleep(0.1)
        result3 = get_user_data(888)
        output3 = capsys.readouterr()
        assert "взят из кеша 888" in output3.out

        assert result1 == result2 == result3 == 888


# Тесты для самого декоратора
class TestCacheResultDecorator:
    def test_decorator_apply(self):
        """Тест применения декоратора к функции"""

        # Создаем тестовую функцию
        def test_func(x: int) -> int:
            return x * 2

        # Применяем декоратор
        decorated_func = cache_result(test_func)

        # Проверяем что функция обернута
        result1 = decorated_func(5)
        result2 = decorated_func(5)  # Должен быть из кэша

        assert result1 == 10
        assert result2 == 10

    def test_decorator_preserves_function_info(self):
        """Тест что декоратор сохраняет информацию о функции"""

        @cache_result
        def original_func(x: int) -> int:
            """Тестовая функция"""
            return x * 3

        # Проверяем что сохранилось имя и докстринг
        assert original_func.__name__ == "original_func"
        # Примечание: без @functools.wraps имя будет 'wrapper'

    def test_decorator_with_different_function(self):
        """Тест декоратора с другой функцией"""

        @cache_result
        def slow_calculation(n: int) -> int:
            time.sleep(1)
            return n**2

        # Первый вызов
        start_time = time.time()
        result1 = slow_calculation(5)
        time1 = time.time() - start_time

        # Второй вызов (должен быть быстрее)
        start_time = time.time()
        result2 = slow_calculation(5)
        time2 = time.time() - start_time

        assert result1 == 25
        assert result2 == 25
        assert time1 >= 1.0  # Первый вызов долгий
        assert time2 < 0.1  # Второй вызов быстрый


class TestCacheResultPerformance:
    def test_cache_performance_improvement(self):
        """Тест что кэширование значительно ускоряет повторные вызовы"""
        user_id = 42

        # Первый вызов (медленный)
        start_time = time.time()
        get_user_data(user_id)
        first_call_time = time.time() - start_time

        # Второй вызов (быстрый)
        start_time = time.time()
        get_user_data(user_id)
        second_call_time = time.time() - start_time

        # Проверяем что второй вызов значительно быстрее
        assert second_call_time < first_call_time / 10  # В 10+ раз быстрее
        assert first_call_time >= 1.9  # Примерно 2 секунды
        assert second_call_time < 0.1  # Меньше 0.1 секунды


# Фикстуры
@pytest.fixture
def cached_function():
    """Фикстура для создания функции с кэшированием"""

    @cache_result
    def test_func(x: int) -> int:
        time.sleep(0.1)  # Укороченная задержка для тестов
        return x * 2

    return test_func


class TestCacheResultWithFixtures:
    def test_with_fixture(self, cached_function, capsys):
        """Тест с использованием фикстуры"""
        # Первый вызов
        result1 = cached_function(10)
        output1 = capsys.readouterr()
        assert "взят из базы 20" in output1.out or "взят из базы 10" in output1.out

        # Второй вызов
        result2 = cached_function(10)
        output2 = capsys.readouterr()
        assert "взят из кеша" in output2.out

        assert result1 == result2


if __name__ == "__main__":
    # Быстрая проверка работы
    print("Тест базовой работы:")
    result = get_user_data(1)
    print(f"Результат: {result}")

    print("Тест кэширования:")
    result = get_user_data(1)
    print(f"Результат: {result}")
