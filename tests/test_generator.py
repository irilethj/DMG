import pytest
from dmg.generator import paginate_api


class TestPaginateAPI:
    def test_basic_pagination(self):
        """Тест базовой пагинации"""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        page_size = 3

        pages = list(paginate_api(data, page_size))

        expected_pages = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]

        assert pages == expected_pages
        assert len(pages) == 4

    def test_exact_page_fit(self):
        """Тест когда данные точно делятся на страницы"""
        data = [1, 2, 3, 4, 5, 6]
        page_size = 2

        pages = list(paginate_api(data, page_size))

        assert pages == [[1, 2], [3, 4], [5, 6]]
        assert all(len(page) == page_size for page in pages[:-1])

    def test_single_page(self):
        """Тест когда все данные помещаются на одну страницу"""
        data = [1, 2, 3]
        page_size = 5

        pages = list(paginate_api(data, page_size))

        assert pages == [[1, 2, 3]]
        assert len(pages) == 1

    def test_empty_data(self):
        """Тест с пустым списком данных"""
        pages = list(paginate_api([], 3))

        assert pages == []
        assert len(pages) == 0

    def test_single_element(self):
        """Тест с одним элементом"""
        pages = list(paginate_api([42], 2))

        assert pages == [[42]]
        assert len(pages) == 1

    def test_page_size_one(self):
        """Тест с размером страницы = 1"""
        data = ["a", "b", "c"]
        pages = list(paginate_api(data, 1))

        assert pages == [["a"], ["b"], ["c"]]
        assert len(pages) == len(data)

    def test_large_page_size(self):
        """Тест когда размер страницы больше чем данных"""
        data = [1, 2, 3]
        pages = list(paginate_api(data, 10))

        assert pages == [[1, 2, 3]]

    def test_different_data_types(self):
        """Тест с разными типами данных"""
        data = ["hello", 42, {"key": "value"}, [1, 2, 3]]
        pages = list(paginate_api(data, 2))

        assert pages == [["hello", 42], [{"key": "value"}, [1, 2, 3]]]

    def test_generator_behavior(self):
        """Тест, что возвращается именно генератор"""
        data = [1, 2, 3, 4, 5]
        result = paginate_api(data, 2)

        # Проверяем что это генератор
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")

        # Проверяем ленивую загрузку
        page1 = next(result)
        assert page1 == [1, 2]

        page2 = next(result)
        assert page2 == [3, 4]

        page3 = next(result)
        assert page3 == [5]

    def test_stop_iteration(self):
        """Тест, что генератор корректно завершается"""
        data = [1, 2]
        paginator = paginate_api(data, 2)

        # Первая страница
        page1 = next(paginator)
        assert page1 == [1, 2]

        # Должен вызвать StopIteration
        with pytest.raises(StopIteration):
            next(paginator)

    def test_zero_page_size(self):
        """Тест с нулевым размером страницы"""
        data = [1, 2, 3]

        with pytest.raises(ZeroDivisionError):
            list(paginate_api(data, 0))
