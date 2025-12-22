import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Row, Col, Typography, Spin, Alert, Card, Descriptions, Button, message, Modal, Table, Tag, Space } from 'antd';
import { BookOutlined, CopyOutlined } from '@ant-design/icons';
import CONFIG from './consts/config';

const { Title, Paragraph } = Typography;

type BookCopy = {
  serial_num: string;
  status: string;
  access_type: string;
};

type Book = {
  id: number;
  title: string;
  author: string;
  publisher: string;
  year_publication: number;
  cover_url?: string | null;
  copies: BookCopy[];
};

const API_BASE = CONFIG.API_URL;

const BookPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [book, setBook] = useState<Book | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [requestLoading, setRequestLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchBook = async (id: string | undefined) => {
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

  useEffect(() => {
    fetchBook(id);
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

      fetchBook(id)
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

  const copyColumns = [
    {
      title: 'Серийный номер',
      dataIndex: 'serial_num',
      key: 'serial_num',
      render: (serial_num: string) => (
        <Space>
          <CopyOutlined />
          <span>{serial_num}</span>
        </Space>
      ),
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const color = status === 'AVAILABLE' ? 'green' : status === 'RESERVED' ? 'orange' : 'red';
        return <Tag color={color}>{status}</Tag>;
      },
    },
    {
      title: 'Тип доступа',
      dataIndex: 'access_type',
      key: 'access_type',
      render: (access_type: string) => (
        <Tag>{access_type}</Tag>
      ),
    },
  ];

  const availableCopies = book.copies.filter(copy => copy.status === 'AVAILABLE').length;

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <Title level={2} className="mb-6">{book.title}</Title>
      
      <Row gutter={[24, 24]}>
        <Col xs={24} md={8}>
          <Card
            cover={
              coverSrc ? (
                <img 
                  alt={book.title} 
                  src={coverSrc}
                  className='w-full h-auto, max-[420px] object-cover bg-white' 
                />
              ) : undefined
            }
          >
            {!coverSrc && <Paragraph className="text-center text-gray-500">Обложка отсутствует</Paragraph>}
          </Card>
        </Col>

        <Col xs={24} md={16}>
          <Descriptions bordered column={1} size="middle" className="mb-6">
            <Descriptions.Item label="Автор">{book.author}</Descriptions.Item>
            <Descriptions.Item label="Издательство">{book.publisher}</Descriptions.Item>
            <Descriptions.Item label="Год публикации">{book.year_publication}</Descriptions.Item>
            <Descriptions.Item label="ID">{book.id}</Descriptions.Item>
            <Descriptions.Item label="Экземпляров всего">
              <Tag color="blue">{book.copies.length}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Доступно">
              <Tag color="green">{availableCopies}</Tag>
            </Descriptions.Item>
          </Descriptions>

          <div className="mb-6">
            <Button
              type="primary"
              size="large"
              icon={<BookOutlined />}
              onClick={handleOpenModal}
            >
              Запросить книгу ({availableCopies} доступно)
            </Button>
          </div>
        </Col>
      </Row>

      <Card 
        title={
          <Space>
            <CopyOutlined />
            Экземпляры книги ({book.copies.length})
          </Space>
        } 
        className="mt-6"
      >
        <Table
          dataSource={book.copies}
          columns={copyColumns}
          rowKey="serial_num"
          pagination={false}
          size="middle"
          scroll={{ x: 600 }}
        />
        
        {book.copies.length === 0 && (
          <div className="text-center py-8">
            <Paragraph type="secondary">Экземпляры отсутствуют</Paragraph>
          </div>
        )}
      </Card>

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
          <p className="text-gray-600">
            Доступно экземпляров: <Tag color="green">{availableCopies}</Tag>
          </p>
        </div>
      </Modal>
    </div>
  );
};

export default BookPage;
