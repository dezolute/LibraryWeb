import '@ant-design/v5-patch-for-react-19';
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, Tag, Spin, Typography, Alert, Flex, Button, Divider, Modal } from 'antd';
import { CONFIG } from '../constants/config';


const { Title, Paragraph } = Typography;
const apiUrl = CONFIG.API_URL;

const fallbackCover = 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcovers.bookcoverzone.com%2Fimage%2Fpng24-front%2Fbookcover0027056.jpg%26height%3D1000&f=1&nofb=1&ipt=39b398c37a54c686bc438f711ad93f29840f7798ee8ea1bdbf57152b8046e533';

const priorityColor = {
  LOW: 'green',
  HIGH: 'red',
};

const BookPage = () => {
  const { id } = useParams();
  const [book, setBook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const navigate = useNavigate()

  useEffect(() => {
    const fetchBook = async () => {
      try {
        const response = await fetch(`${apiUrl}/books/${id}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`Ошибка: ${response.status}`);
        }

        const result = await response.json();
        setBook(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchBook();
  }, [id]);

  const confirmRequest = () => {
    Modal.confirm({
      title: 'Подтвердите запрос',
      content: 'Вы уверены, что хотите создать запрос на выдачу этой книги?',
      okText: 'Да',
      cancelText: 'Отмена',
      onOk: () => createRequest(),
    });
  };

  const createRequest = async () => {
    try {
      const response = await fetch(`${apiUrl}/readers/me/requests?book_id=${id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      if (response.status == 409) { throw new Error('Вы не можете создать больше 5 запросов') }
      if (response.status == 406) { throw new Error('Вы уже сделали запрос на эту книгу') }
      if (!response.ok) throw new Error('Не удалось создать запрос');
      Modal.success({
        title: 'Запрос создан',
        content: '📬 Ваш запрос на выдачу книги успешно отправлен!',
        onOk: () => navigate('/books'),
      });
    } catch (err) {
      Modal.error({
        title: 'Ошибка',
        content: `❌ ${err.message}`,
      });
    }
  };

  if (loading) return <Spin tip="📖 Загрузка книги..." style={{ marginTop: 50 }} />;
  if (error) return <Alert type="error" message="Ошибка загрузки" description={error} showIcon />;

  return (
    <Card
      title={<Title level={1}>📘 {book.title}</Title>}
      style={{
        maxWidth: 900,
        margin: '40px auto',
        padding: '40px',
        boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
        borderRadius: '16px',
        backgroundColor: '#fefefe',
        fontSize: '20px',
      }}
    >
      <Flex gap={50} align="start" justify="space-between">
        <div style={{ flex: 1 }}>
          <Paragraph style={{ fontSize: 22 }}><strong>👨‍💼 Автор:</strong> {book.author}</Paragraph>
          <Paragraph style={{ fontSize: 22 }}><strong>📅 Год издания:</strong> {book.year_publication}</Paragraph>
          <Paragraph style={{ fontSize: 22 }}><strong>🏢 Издательство:</strong> {book.publisher}</Paragraph>
          <Paragraph style={{ fontSize: 22 }}>
            <strong>📌 Приоритет:</strong>{' '}
            <Tag color={priorityColor[book.priority]} style={{ fontSize: 20, padding: '6px 14px' }}>
              {book.priority === 'HIGH' ? 'Высокий' : 'Низкий'}
            </Tag>
          </Paragraph>
          <Divider />
          <Button type="primary" size="large" style={{ fontSize: 18 }} onClick={confirmRequest}>
            📤 Создать запрос на выдачу
          </Button>
        </div>
        <img
          src={book.cover || fallbackCover}
          alt={`Обложка книги ${book.title}`}
          style={{
            width: 280,
            height: 340,
            borderRadius: 10,
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          }}
          loading="lazy"
        />
      </Flex>
    </Card>
  );
};

export default BookPage;