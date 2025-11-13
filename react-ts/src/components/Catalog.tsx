import { useEffect, useState } from 'react';
import { Row, Col, Card, Pagination, Spin, Alert, Empty, Input, InputNumber, Button, Space } from 'antd';
import { Link } from 'react-router-dom';
import CONFIG from './consts/config';

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
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(12);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [authorFilter, setAuthorFilter] = useState('');
  const [publisherFilter, setPublisherFilter] = useState('');
  const [yearFilter, setYearFilter] = useState<number | null>(null);

  const fetchBooks = async (pageIndex = 1, filters?: { author?: string; publisher?: string; year?: number | null }) => {
    setLoading(true);
    setError(null);
    try {
      const offset = (pageIndex - 1) * limit;
      const params = new URLSearchParams();
      params.set('limit', String(limit));
      params.set('offset', String(offset));
      
      const author = filters?.author ?? authorFilter;
      const publisher = filters?.publisher ?? publisherFilter;
      const year = filters?.year ?? yearFilter;
      
      if (author) params.set('author', author);
      if (publisher) params.set('publisher', publisher);
      if (year) params.set('year_publication', String(year));

      const resp = await fetch(`${API_BASE}/books?${params.toString()}`);
      if (!resp.ok) throw new Error('Ошибка получения списка книг');
      const contentType = resp.headers.get('content-type') || '';
      const text = await resp.text();
      let data: unknown;
      if (contentType.includes('application/json')) {
        try { data = JSON.parse(text); } catch { data = text; }
      } else {
        try { data = JSON.parse(text); } catch { data = text; }
      }

  const parsed = data as { items?: Book[]; total?: number };
  setBooks(parsed.items || []);
  setTotal(typeof parsed.total === 'number' ? parsed.total : (parsed.items || []).length);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    fetchBooks(1);
  };

  const handleClearFilters = () => {
    setAuthorFilter('');
    setPublisherFilter('');
    setYearFilter(null);
    setPage(1);
    fetchBooks(1, { author: '', publisher: '', year: null });
  };

  useEffect(() => {
    fetchBooks(page);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page]);

  return (
    <div className="max-w-6xl mx-auto px-4">
      <h2 className="text-2xl font-semibold my-6">Каталог книг</h2>

      <div className="flex flex-wrap gap-3 mb-4">
        <Input
          placeholder="Автор"
          value={authorFilter}
          onChange={(e) => setAuthorFilter(e.target.value)}
          style={{ width: 200 }}
          allowClear
        />
        <Input
          placeholder="Издательство"
          value={publisherFilter}
          onChange={(e) => setPublisherFilter(e.target.value)}
          style={{ width: 200 }}
          allowClear
        />
        <InputNumber
          placeholder="Год публикации"
          value={yearFilter ?? undefined}
          onChange={(v) => setYearFilter(typeof v === 'number' ? v : null)}
          style={{ width: 180 }}
          min={1900}
          max={new Date().getFullYear()}
        />
        <Space>
          <Button onClick={handleSearch} type="default">Фильтровать</Button>
          <Button onClick={handleClearFilters} type="default">Сбросить</Button>
        </Space>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <Spin size="large" />
        </div>
      ) : error ? (
        <Alert type="error" message="Ошибка" description={error} />
      ) : books.length === 0 ? (
        <Empty description="Книг не найдено" />
      ) : (
        <>
          <Row gutter={[16, 16]}>
            {books.map((book) => (
              <Col key={book.id} xs={24} sm={12} md={8} lg={6}>
                <Link to={`/book/${book.id}`} style={{ display: 'block' }}>
                  <Card
                    hoverable
                    cover={
                      <img
                        className='h-[300px]'
                        alt={book.title}
                        src={book.cover_url? book.cover_url : BOOK_COVER}
                      />
                    }
                  >
                    <Meta title={book.title} description={`${book.author} — ${book.publisher} (${book.year_publication})`} />
                  </Card>
                </Link>
              </Col>
            ))}
          </Row>

          <div className="flex justify-center mt-8">
            <Pagination
              current={page}
              pageSize={limit}
              total={total}
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
