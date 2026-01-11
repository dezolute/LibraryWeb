import { useEffect, useMemo, useState } from "react";
import { Row, Col, Card, Pagination, Spin, Alert, Empty, Input, InputNumber, Button, Space, Select } from "antd";
import { Link } from "react-router-dom";
import CONFIG from "./consts/config";

const { Meta } = Card;
const BOOK_COVER = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn1.ozone.ru%2Fmultimedia%2Fc1200%2F1016455349.jpg&f=1&nofb=1&ipt=7c801e3df66770889cffc44b4742f072b4543c4dab123d2dfee47b02f08cde46";

interface Book {
  id: number;
  title: string;
  author: string;
  publisher: string;
  year_publication: number;
  cover_url?: string | null;
  copies?: unknown[];
}

const API_BASE = CONFIG.API_URL;

export const Catalog = () => {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Фильтры
  const [authorFilter, setAuthorFilter] = useState("");
  const [publisherFilter, setPublisherFilter] = useState("");
  const [yearFilter, setYearFilter] = useState<number | null>(null);

  // Поиск по названию
  const [searchQuery, setSearchQuery] = useState("");

  // Сортировка
  const [sortBy, setSortBy] = useState<keyof Book>("title");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  // Пагинация (клиентская)
  const [page, setPage] = useState(1);
  const [pageSize] = useState(12);

  const fetchBooks = async () => {
    setLoading(true);
    setError(null);
    try {
      // Грузим все книги без limit/offset — фильтрация будет на фронте
      const resp = await fetch(`${API_BASE}/books`);
      if (!resp.ok) throw new Error("Ошибка получения списка книг");

      const contentType = resp.headers.get("content-type") || "";
      const text = await resp.text();
      let data: unknown;
      if (contentType.includes("application/json")) {
        try { data = JSON.parse(text); } catch { data = text; }
      } else {
        try { data = JSON.parse(text); } catch { data = text; }
      }

      const parsed = data as { items?: Book[]; total?: number };
      setBooks(parsed.items || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBooks();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ---- ФИЛЬТРАЦИЯ, ПОИСК, СОРТИРОВКА ----
  const processedBooks = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();

    // 1. Фильтрация + поиск
    const filtered = books.filter((b) => {
      const matchesAuthor = !authorFilter || b.author.toLowerCase().includes(authorFilter.toLowerCase());
      const matchesPublisher = !publisherFilter || b.publisher.toLowerCase().includes(publisherFilter.toLowerCase());
      const matchesYear = !yearFilter || b.year_publication === yearFilter;
      const matchesSearch = !query || b.title.toLowerCase().includes(query);

      return matchesAuthor && matchesPublisher && matchesYear && matchesSearch;
    });

    // 2. Сортировка
    const sorted = [...filtered].sort((a, b) => {
      let aVal: any = a[sortBy];
      let bVal: any = b[sortBy];

      // Приведение к строке для сравнения
      if (typeof aVal === "string" && typeof bVal === "string") {
        aVal = aVal.toLowerCase();
        bVal = bVal.toLowerCase();
      }

      if (aVal < bVal) return sortOrder === "asc" ? -1 : 1;
      if (aVal > bVal) return sortOrder === "asc" ? 1 : -1;
      return 0;
    });

    return sorted;
  }, [books, authorFilter, publisherFilter, yearFilter, searchQuery, sortBy, sortOrder]);

  // Сброс страницы при изменении фильтров/поиска/сортировки
  useEffect(() => {
    setPage(1);
  }, [authorFilter, publisherFilter, yearFilter, searchQuery, sortBy, sortOrder]);

  // Пагинация
  const pagedBooks = useMemo(() => {
    const start = (page - 1) * pageSize;
    return processedBooks.slice(start, start + pageSize);
  }, [processedBooks, page, pageSize]);

  const handleClearFilters = () => {
    setAuthorFilter("");
    setPublisherFilter("");
    setYearFilter(null);
    setSearchQuery("");
    setSortBy("title");
    setSortOrder("asc");
  };

  return (
    <div className="max-w-6xl mx-auto px-4">
      <h2 className="text-2xl font-semibold my-6">Каталог книг</h2>

      {/* Панель фильтров, поиска и сортировки */}
      <div className="flex flex-wrap gap-3 mb-4">
        <Input
          placeholder="Поиск по названию"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{ width: 250 }}
          allowClear
        />
        <Input
          placeholder="Автор"
          value={authorFilter}
          onChange={(e) => setAuthorFilter(e.target.value)}
          style={{ width: 180 }}
          allowClear
        />
        <Input
          placeholder="Издательство"
          value={publisherFilter}
          onChange={(e) => setPublisherFilter(e.target.value)}
          style={{ width: 180 }}
          allowClear
        />
        <InputNumber
          placeholder="Год"
          value={yearFilter ?? undefined}
          onChange={(v) => setYearFilter(typeof v === "number" ? v : null)}
          style={{ width: 120 }}
          max={new Date().getFullYear()}
        />
        <Select
          value={sortBy}
          onChange={(v) => setSortBy(v as keyof Book)}
          style={{ width: 140 }}
          options={[
            { label: "Название", value: "title" },
            { label: "Автор", value: "author" },
            { label: "Издательство", value: "publisher" },
            { label: "Год", value: "year_publication" },
          ]}
        />
        <Select
          value={sortOrder}
          onChange={(v) => setSortOrder(v as "asc" | "desc")}
          style={{ width: 100 }}
          options={[
            { label: "↑", value: "asc" },
            { label: "↓", value: "desc" },
          ]}
        />
        <Space>
          <Button onClick={handleClearFilters} type="default">
            Сбросить
          </Button>
        </Space>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <Spin size="large" />
        </div>
      ) : error ? (
        <Alert type="error" message="Ошибка" description={error} />
      ) : processedBooks.length === 0 ? (
        <Empty description="Книг не найдено" />
      ) : (
        <>
          <Row gutter={[16, 16]}>
            {pagedBooks.map((book) => (
              <Col key={book.id} xs={24} sm={12} md={8} lg={6}>
                <Link to={`/book/${book.id}`} style={{ display: "block" }}>
                  <Card
                    hoverable
                    cover={
                      <img
                        className="h-[300px] object-cover"
                        alt={book.title}
                        src={book.cover_url ? book.cover_url : BOOK_COVER}
                      />
                    }
                  >
                    <Meta
                      title={book.title}
                      description={`${book.author} — ${book.publisher} (${book.year_publication})`}
                    />
                  </Card>
                </Link>
              </Col>
            ))}
          </Row>

          <div className="flex justify-center mt-8">
            <Pagination
              current={page}
              pageSize={pageSize}
              total={processedBooks.length}
              onChange={(p) => setPage(p)}
              showSizeChanger={false}
            />
          </div>
        </>
      )}
    </div>
  );
};

export default Catalog;