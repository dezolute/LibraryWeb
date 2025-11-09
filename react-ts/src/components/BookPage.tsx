import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Row, Col, Typography, Spin, Alert, Card, Descriptions, Button, message, Modal } from 'antd';
import { BookOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

type Book = {
  id: number;
  title: string;
  author: string;
  publisher: string;
  year_publication: number;
  cover_url?: string | null;
};

const API_BASE = 'http://127.0.0.1:8000/api';

const BookPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [book, setBook] = useState<Book | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [requestLoading, setRequestLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    const fetchBook = async () => {
      if (!id) return;
      setLoading(true);
      setError(null);
      try {
        const resp = await fetch(`${API_BASE}/books/${id}`);
        if (!resp.ok) throw new Error('Не удалось получить данные книги');
        const contentType = resp.headers.get('content-type') || '';
        const text = await resp.text();
        let data: unknown;
        if (contentType.includes('application/json')) {
          try { data = JSON.parse(text); } catch { data = text; }
        } else {
          try { data = JSON.parse(text); } catch { data = text; }
        }
        setBook(data as Book);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };
    fetchBook();
  }, [id]);

  const handleOpenModal = () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      message.warning('Необходимо авторизоваться для создания запроса');
      return;
    }
    setIsModalOpen(true);
  };

  const handleModalCancel = () => {
    setIsModalOpen(false);
  };

  const handleCreateRequest = async () => {
    if (!id) return;
    
    const token = localStorage.getItem('access_token');
    if (!token) {
      message.warning('Необходимо авторизоваться для создания запроса');
      setIsModalOpen(false);
      return;
    }

    setRequestLoading(true);
    try {
      const params = new URLSearchParams();
      params.set('book_id', id);

      const resp = await fetch(`${API_BASE}/readers/me/requests?${params.toString()}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (resp.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_role');
        message.error('Сессия истекла. Пожалуйста, войдите снова');
        navigate('/');
        return;
      }

      if (!resp.ok) {
        const text = await resp.text();
        let errorMsg = 'Не удалось создать запрос';
        try {
          const errorData = JSON.parse(text);
          errorMsg = errorData.detail || errorData.message || errorMsg;
        } catch {
          errorMsg = text || errorMsg;
        }
        throw new Error(errorMsg);
      }

      message.success('Запрос на книгу успешно создан');
      setIsModalOpen(false);
    } catch (e) {
      message.error(e instanceof Error ? e.message : 'Произошла ошибка');
    } finally {
      setRequestLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return <Alert type="error" message="Ошибка" description={error} />;
  }

  if (!book) {
    return <Paragraph>Книга не найдена.</Paragraph>;
  }

  const coverSrc = book.cover_url
    ? (book.cover_url.startsWith('http') ? book.cover_url : `${API_BASE}${book.cover_url}`)
    : undefined;

  return (
    <div className="max-w-5xl mx-auto px-4">
      <Title level={2} className="mb-6">{book.title}</Title>
      <Row gutter={[24, 24]}>
        <Col xs={24} md={8}>
          <Card
            cover={
              coverSrc ? (
                <img 
                  alt={book.title} 
                  src={coverSrc} 
                  style={{ width: '100%', height: 'auto', maxHeight: 420, objectFit: 'contain', backgroundColor: '#fff' }} 
                />
              ) : undefined
            }
          >
            {!coverSrc && <Paragraph className="text-center text-gray-500">Обложка отсутствует</Paragraph>}
          </Card>
        </Col>
        <Col xs={24} md={16}>
          <Descriptions bordered column={1} size="middle">
            <Descriptions.Item label="Автор">{book.author}</Descriptions.Item>
            <Descriptions.Item label="Издательство">{book.publisher}</Descriptions.Item>
            <Descriptions.Item label="Год публикации">{book.year_publication}</Descriptions.Item>
            <Descriptions.Item label="ID">{book.id}</Descriptions.Item>
          </Descriptions>
          <div className="mt-4">
            <Button
              type="primary"
              size="large"
              icon={<BookOutlined />}
              onClick={handleOpenModal}
            >
              Запросить книгу
            </Button>
          </div>
        </Col>
      </Row>

      <Modal
        title="Подтверждение запроса"
        open={isModalOpen}
        onOk={handleCreateRequest}
        onCancel={handleModalCancel}
        confirmLoading={requestLoading}
        okText="Подтвердить"
        cancelText="Отмена"
      >
        <div className="py-4">
          <p>Вы уверены, что хотите создать запрос на книгу:</p>
          <p className="font-semibold text-lg mt-2">{book.title}</p>
          <p className="text-gray-600 mt-1">Автор: {book.author}</p>
          <p className="text-gray-600">Издательство: {book.publisher}</p>
        </div>
      </Modal>
    </div>
  );
};

export default BookPage;


