import pytest

from app.models import BookORM

@pytest.mark.asyncio
async def test_create_book(book_repo):
    book = await book_repo.create({
        "title": "Test Book",
        "author": "Author",
        "publisher": "Publisher",
        "year_publication": 2020
    })
    assert book.id is not None
    assert book.title == "Test Book"


@pytest.mark.asyncio
async def test_create_multiple_books(book_repo):
    books = await book_repo.create_multiple([
        {"title": "Book A", "author": "A", "publisher": "P", "year_publication": 2001},
        {"title": "Book B", "author": "B", "publisher": "P", "year_publication": 2002}
    ])
    assert len(books) == 2
    assert books[0].title == "Book A"
    assert books[1].title == "Book B"

@pytest.mark.asyncio
async def test_update_book(book_repo):
    book = await book_repo.create({"title": "Old", "author": "X", "publisher": "Y", "year_publication": 2000})
    updated = await book_repo.update({"title": "New"}, conditions=[BookORM.id == book.id])
    assert updated.title == "New"

@pytest.mark.asyncio
async def test_delete_book(book_repo):
    book = await book_repo.create({"title": "ToDelete", "author": "X", "publisher": "Y", "year_publication": 2000})
    deleted = await book_repo.delete(conditions=[BookORM.id == book.id])
    assert deleted.id == book.id

    found = await book_repo.find([BookORM.id == book.id])
    assert found is None

@pytest.mark.asyncio
async def test_find_book(book_repo):
    book = await book_repo.create({"title": "FindMe", "author": "X", "publisher": "Y", "year_publication": 2000})
    found = await book_repo.find([BookORM.title == "FindMe"])
    assert found.id == book.id

@pytest.mark.asyncio
async def test_find_all_books(book_repo):
    await book_repo.create_multiple([
        {"title": "Book1", "author": "A", "publisher": "P", "year_publication": 2001},
        {"title": "Book2", "author": "B", "publisher": "P", "year_publication": 2002}
    ])
    from app.schemas.utils import Pagination
    books, total = await book_repo.find_all(pg=Pagination(limit=10, offset=0))
    assert total >= 2
    assert len(books) >= 2