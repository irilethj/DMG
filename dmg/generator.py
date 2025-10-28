from typing import Generator


def paginate_api(data: list, page_size: int) -> Generator:
    total_pages = (len(data) + page_size - 1) // page_size

    for page_num in range(total_pages):
        start_index = page_num * page_size
        end_index = start_index + page_size

        yield data[start_index:end_index]
