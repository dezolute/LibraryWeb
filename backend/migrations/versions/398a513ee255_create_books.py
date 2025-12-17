"""create_books

Revision ID: 398a513ee255
Revises: d147f996025c
Create Date: 2025-12-17 22:44:53.188222

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision: str = "398a513ee255"
down_revision: Union[str, Sequence[str], None] = "d147f996025c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Добавление 20 книг с экземплярами"""
    
    conn = op.get_bind()
    
    # Список книг: (title, author, publisher, cover_url, year)
    books_data = [
        ("Война и мир", "Лев Толстой", "Эксмо", "https://example.com/war_peace.jpg", 1869),
        ("Преступление и наказание", "Фёдор Достоевский", "АСТ", "https://example.com/crime.jpg", 1866),
        ("Мастер и Маргарита", "Михаил Булгаков", "Азбука", "https://example.com/master.jpg", 1967),
        ("1984", "Джордж Оруэлл", "АСТ", "https://example.com/1984.jpg", 1949),
        ("Гарри Поттер и философский камень", "Дж. К. Роулинг", "Росмэн", "https://example.com/hp1.jpg", 1997),
        ("Властелин колец: Братство кольца", "Дж. Р. Р. Толкин", "АСТ", "https://example.com/lotr1.jpg", 1954),
        ("Алхимик", "Пауло Коэльо", "София", "https://example.com/alchemist.jpg", 1988),
        ("Маленький принц", "Антуан де Сент-Экзюпери", "АСТ", "https://example.com/prince.jpg", 1943),
        ("451 градус по Фаренгейту", "Рэй Брэдбери", "Эксмо", "https://example.com/f451.jpg", 1953),
        ("Над пропастью во ржи", "Дж. Д. Сэлинджер", "Азбука", "https://example.com/catcher.jpg", 1951),
        ("Анна Каренина", "Лев Толстой", "Эксмо", "https://example.com/anna.jpg", 1877),
        ("Братья Карамазовы", "Фёдор Достоевский", "АСТ", "https://example.com/karamazov.jpg", 1880),
        ("Грозовой перевал", "Эмили Бронте", "Азбука", "https://example.com/wuthering.jpg", 1847),
        ("Убить пересмешника", "Харпер Ли", "АСТ", "https://example.com/mockingbird.jpg", 1960),
        ("Великий Гэтсби", "Фрэнсис Скотт Фицджеральд", "Азбука", "https://example.com/gatsby.jpg", 1925),
        ("Хоббит", "Дж. Р. Р. Толкин", "АСТ", "https://example.com/hobbit.jpg", 1937),
        ("Дюна", "Фрэнк Герберт", "Эксмо", "https://example.com/dune.jpg", 1965),
        ("Игра престолов", "Джордж Мартин", "АСТ", "https://example.com/got.jpg", 1996),
        ("Шантарам", "Грегори Дэвид Робертс", "Азбука", "https://example.com/shantaram.jpg", 2003),
        ("Тень ветра", "Карлос Руис Сафон", "АСТ", "https://example.com/shadow.jpg", 2001),
    ]
    
    print("📚 Добавляем 20 книг с экземплярами...")
    
    for idx, (title, author, publisher, cover_url, year) in enumerate(books_data, 1):
        # Проверяем существование книги
        result = conn.execute(
            sa.text("SELECT id FROM books WHERE title = :title AND author = :author"),
            {"title": title, "author": author}
        ).fetchone()
        
        if result:
            print(f"   ⏭️  Книга '{title}' уже существует (ID: {result[0]})")
            continue
        
        # **ИСПРАВЛЕНИЕ: Вставляем книгу**
        result = conn.execute(
            sa.text("""
                INSERT INTO books (title, author, publisher, cover_url, year_publication) 
                VALUES (:title, :author, :publisher, :cover_url, :year) 
                RETURNING id
            """),
            {
                "title": title,
                "author": author,
                "publisher": publisher,
                "cover_url": cover_url,
                "year": year,
            }
        ).fetchone()
        
        book_id = result[0] # type: ignore
        print(f"   📖 {idx}. '{title}' добавлена (ID: {book_id})")
        
        # Добавляем 2-3 экземпляра каждой книги
        num_copies = 3 if book_id % 2 == 0 else 2
        
        for copy_num in range(1, num_copies + 1):
            serial_num = f"{book_id:03d}-{copy_num:02d}"
            
            # **КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: Приведение к PostgreSQL ENUM типам**
            conn.execute(
                sa.text("""
                    INSERT INTO book_copies (serial_num, book_id, status, access_type) 
                    VALUES (
                        :serial_num, 
                        :book_id, 
                        :status,
                        :access_type
                    )
                """),
                {
                    "serial_num": serial_num,
                    "book_id": book_id,
                    "status": "AVAILABLE",  # Ваше значение enum
                    "access_type": "TAKE_HOME",  # Ваше значение enum
                }
            )
        
        print(f"      📄 Добавлено {num_copies} экземпляра(ов)")
    
    print("✅ Миграция завершена! Добавлено 20 книг.")


def downgrade() -> None:
    """Удаление тестовых книг"""
    conn = op.get_bind()
    
    print("🗑️  Удаляем тестовые книги...")
    
    book_titles = [
        "Война и мир", "Преступление и наказание", "Мастер и Маргарита",
        "1984", "Гарри Поттер и философский камень", "Властелин колец: Братство кольца",
        "Алхимик", "Маленький принц", "451 градус по Фаренгейту", "Над пропастью во ржи",
        "Анна Каренина", "Братья Карамазовы", "Грозовой перевал", "Убить пересмешника",
        "Великий Гэтсби", "Хоббит", "Дюна", "Игра престолов", "Шантарам", "Тень ветра"
    ]
    
    for title in book_titles:
        conn.execute(
            sa.text("DELETE FROM books WHERE title = :title"),
            {"title": title}
        )
    
    print("✅ Тестовые данные удалены (CASCADE удалит и book_copies)")
