import '@ant-design/v5-patch-for-react-19';
import { useEffect, useState } from 'react';
import { Card, Flex, Tag, Typography, Pagination, Spin, Button, Alert } from 'antd';
import { useNavigate } from 'react-router-dom';
import { CONFIG } from '../constants/config';

const { Title } = Typography;
const apiUrl = CONFIG.API_URL;

const priorityColor = {
  HIGH: 'red',
  LOW: 'green',
};

const fallbackCover = 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcovers.bookcoverzone.com%2Fimage%2Fpng24-front%2Fbookcover0027056.jpg%26height%3D1000&f=1&nofb=1&ipt=39b398c37a54c686bc438f711ad93f29840f7798ee8ea1bdbf57152b8046e533';

const BookCatalog = () => {
  const [books, setBooks] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [error, setError] = useState(null);
  const [limit] = useState(8);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchBooks = async (page) => {
    setLoading(true);
    try {
      const offset = (page - 1) * limit;
      const response = await fetch(`${apiUrl}/books?limit=${limit}&offset=${offset}&order_by=id`);
      const data = await response.json();
      setBooks(data.items);
      setTotal(data.total);
    } catch (error) {
      setError('Ошибка загрузки данных');
      console.error('Ошибка загрузки книг:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBooks(page);
  }, [page]);

  const handlePageChange = (newPage) => {
    setPage(newPage);
  };

  const goToBookPage = (book_id) => {
    navigate(`/book/${book_id}`);
  };

  if (loading) return <Spin tip='Загрузка книг' style={{ display: 'block', marginTop: 50 }} />;
  if (error) return <Alert type='error' message='Ошибка загрузки' description={error} showIcon />;

  return (
    <div>
      <Title level={2} style={{ textAlign: 'center', marginTop: 0, marginBottom: 40 }}>
        📚 Каталог книг
      </Title>

      <Flex wrap gap='large' justify='center'>
        {books.map((book) => (
          <Card
            key={book.id}
            title={<span style={{ fontWeight: 600 }}>{book.title}</span>}
            style={{
              width: 400,
              textAlign: 'center',
              borderRadius: 12,
              boxShadow: '0 2px 12px rgba(0,0,0,0.05)',
              transition: 'transform 0.2s ease',
            }}
            onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.02)'}
            onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1.0)'}
            actions={[
              <Button type='primary' onClick={() => goToBookPage(book.id)}>📖 Посмотреть</Button>
            ]}
          >
            <Flex gap='middle' align='start' style={{ textAlign: 'left' }}>
              <div>
                <img
                  src={book.cover || fallbackCover}
                  alt={`Обложка ${book.title}`}
                  style={{
                    width: 120,
                    height: 160,
                    borderRadius: 8,
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  }}
                  loading='lazy'
                />
              </div>
              <Flex vertical gap={10} style={{ fontSize: 14, lineHeight: 1.6 }}>
                <div><strong>👤 Автор:</strong> {book.author}</div>
                <div><strong>📅 Год:</strong> {book.year_publication}</div>
                <div><strong>🏢 Издательство:</strong> {book.publisher || '—'}</div>
                <div>
                  <strong>⚡ Приоритет:</strong>{' '}
                  <Tag
                    color={priorityColor[book.priority]}
                    style={{ fontWeight: 500, borderRadius: 8 }}
                  >
                    {book.priority === 'HIGH' ? 'Высокий' : 'Низкий'}
                  </Tag>
                </div>
              </Flex>
            </Flex>
          </Card>
        ))}
      </Flex>
      <Pagination
        current={page}
        pageSize={limit}
        total={total}
        onChange={handlePageChange}
        showQuickJumper
        hideOnSinglePage
        showSizeChanger={false}
        style={{ marginTop: 40, display: 'flex', justifyContent: 'center' }}
      />
    </div>
  );
};

export default BookCatalog;
