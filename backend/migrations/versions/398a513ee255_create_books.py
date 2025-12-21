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
        ("Война и мир", "Лев Толстой", "Эксмо", "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.litres.ru%2Fpub%2Fc%2Fcover%2F66691848.jpg&f=1&nofb=1&ipt=73b36ce957e7e6292a6605419b31e5d44f912dd9998e69a9fcff0f2f82544aa5", 1869),
        ("Преступление и наказание", "Фёдор Достоевский", "АСТ", "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.mann-ivanov-ferber.ru%2Fassets%2Fimages%2Fcovers%2F58%2F30558%2F2.00x-thumb.png&f=1&nofb=1&ipt=40d7fdeaef30006b9bd8670d51df8f778dd861c5120bc8975b409433a753b840", 1866),
        ("Мастер и Маргарита", "Михаил Булгаков", "Азбука", "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn.azbooka.ru%2Fcv%2Fw1100%2F6d73aca1-712d-4da0-996b-9ce977e1fe99.jpg&f=1&nofb=1&ipt=04d857fcbae9b2fe3525f6479d5ae9817f7ee6f4be77883e023de0c3d7d17475", 1967),
        ("1984", "Джордж Оруэлл", "АСТ", "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fm.media-amazon.com%2Fimages%2FI%2F71sOSrd%2BJxL._SL1500_.jpg&f=1&nofb=1&ipt=b385426052f1113407ff5b43fb632fd74de5d0e63d00bb50c73f827547eafab7", 1949),
        ("Гарри Поттер и философский камень", "Дж. К. Роулинг", "Росмэн", "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn.azbooka.ru%2Fcv%2Fw1100%2F3f68a41d-d7ec-4f1b-ae7b-36376eb66430.jpg&f=1&nofb=1&ipt=97ca51d13861e6e8a8886cd8a3ee21ed0bcc102aef2e501bd68b997d56602823", 1997),
        ("Властелин колец: Братство кольца", "Дж. Р. Р. Толкин", "АСТ", "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn1.ozone.ru%2Fmultimedia%2Fc1200%2F1021773602.jpg&f=1&nofb=1&ipt=09ec39ddb20d5c12217243eef23ddbd94b1be6a232b3b901404eef935236ff57", 1954),
        ("Алхимик", "Пауло Коэльо", "София", "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fimg3.labirint.ru%2Frc%2F48ed52f9054ffe12498a4aff26d403a0%2F363x561q80%2Fbooks47%2F466513%2Fcover.png%3F1612675722&f=1&nofb=1&ipt=434be89bfddd61d1813b197e73e2c489d042df517db531e8c080d8f596ebd489", 1988),
        ("Маленький принц", "Антуан де Сент-Экзюпери", "АСТ", "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fimages-na.ssl-images-amazon.com%2Fimages%2FS%2Fcompressed.photo.goodreads.com%2Fbooks%2F1671122775i%2F68006096.jpg&f=1&nofb=1&ipt=508972df62aeb1ba5640dfd0fc5c51bf17ee6c6f890e1c939f7ffe4769bb382c", 1943),
        ("451 градус по Фаренгейту", "Рэй Брэдбери", "Эксмо", "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse3.mm.bing.net%2Fth%2Fid%2FOIP.l2GkYPNF1ggbCnEy521SbQHaKI%3Fcb%3Ducfimg2%26pid%3DApi%26ucfimg%3D1&f=1&ipt=77aa2274b5c2a7566b6347ef0cafa45368743795f78911dd0fd8d53af15581d0", 1953),
        ("Над пропастью во ржи", "Дж. Д. Сэлинджер", "Азбука", "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn.eksmo.ru%2Fv2%2FITD000000000936146%2FCOVER%2Fcover1__w820.jpg&f=1&nofb=1&ipt=757fd706b92290083f56fa01e60e75a55adcc5ae0fae93ec5be36aecdeb6f3a3", 1951),
        ("Анна Каренина", "Лев Толстой", "Эксмо", "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn.azbooka.ru%2Fcv%2Fw1100%2Fa7fa791d-1eaa-40e5-9418-1c84d01a69b9.jpg&f=1&nofb=1&ipt=04f75ee63d1ba029da35526f9e04508192d9a4d37c2d0fb868b8b466a515fd1f", 1877),
        ("Братья Карамазовы", "Фёдор Достоевский", "АСТ", "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn.librarius.md%2Fimg%2Foriginal%2Fbratiya-karamazovy-tom-2_1734349630.jpg&f=1&nofb=1&ipt=fcfdf6b72722e57e873b452b1bc5c5d5bb09fbb8d8375965db73da4d44f2c695", 1880),
        ("Грозовой перевал", "Эмили Бронте", "Азбука", "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.mann-ivanov-ferber.ru%2Fassets%2Fimages%2Fcovers%2F52%2F30552%2F1.00x-thumb.png&f=1&nofb=1&ipt=61e4cf8e77e6ec00841ec249d2999c664aec0791e665e2c1de2ea3b4e302ca7a", 1847),
        ("Убить пересмешника", "Харпер Ли", "АСТ", "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fmaniac-book.ru%2Fuploads%2Fposts%2F2019-03%2F1551790140_ubit-peresmeshnika-skachat.jpg&f=1&nofb=1&ipt=13f98651b6f591221166a9b600cf9d6bc825db46df0f13983dea96c452149a5e", 1960),
        ("Великий Гэтсби", "Фрэнсис Скотт Фицджеральд", "Азбука", "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcv2.litres.ru%2Fpub%2Fc%2Fcover_max1500%2F42575523.jpg&f=1&nofb=1&ipt=c874851714675387d496300d93a88a36836e8cbd4d821add6d52a8d9d3c394e9", 1925),
        ("Хоббит", "Дж. Р. Р. Толкин", "АСТ", "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fimages-na.ssl-images-amazon.com%2Fimages%2FS%2Fcompressed.photo.goodreads.com%2Fbooks%2F1560102057i%2F46225501.jpg&f=1&nofb=1&ipt=57e0b3a3427bc7f9a9b63a9b8b1c9be7ab04af40d39ad790f7f1f266b731ffc0", 1937),
        ("Дюна", "Фрэнк Герберт", "Эксмо", "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse2.mm.bing.net%2Fth%2Fid%2FOIP.KqYHzOJSdNyIih2O3HpKMgHaLO%3Fcb%3Ducfimg2%26pid%3DApi%26ucfimg%3D1&f=1&ipt=f727e4c2c03bad9539026d7cd8a83126b8ec6dd5de18811d712b9c92d5b8b49b", 1965),
        ("Игра престолов", "Джордж Мартин", "АСТ", "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcv1.litres.ru%2Fpub%2Fc%2Fcover%2F248812.jpg&f=1&nofb=1&ipt=82fc3a6782f643dd2fde48f29309cc87cee9095d97663239573da538c17d4859", 1996),
        ("Шантарам", "Грегори Дэвид Робертс", "Азбука", "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn.azbooka.ru%2Fcv%2Fw1100%2F9bd23728-b062-4793-b234-648bb7022245.jpg&f=1&nofb=1&ipt=797fbcfc7d3d311327be2c9c6442bb3e2030ef2fe7984e40a2c58e7c09a5d3e8", 2003),
        ("Тень ветра", "Карлос Руис Сафон", "АСТ", "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fimages-na.ssl-images-amazon.com%2Fimages%2FS%2Fcompressed.photo.goodreads.com%2Fbooks%2F1450546503i%2F17254641.jpg&f=1&nofb=1&ipt=b8d7710907d1b20bcce8b67e4f4be6621c4e1ce6c7eeddecde811d61274edf65", 2001),
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
