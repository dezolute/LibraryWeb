import { useEffect, useState } from 'react';
import { Table, Button, message, Spin, Alert, Tooltip, Input, Select, DatePicker } from 'antd';
import { useNavigate } from 'react-router-dom';
import { 
  ClockCircleOutlined, 
  CheckCircleOutlined, 
  PauseCircleOutlined
} from '@ant-design/icons';
import type { Dayjs } from 'dayjs';

const { RangePicker } = DatePicker;

const API_BASE = 'http://127.0.0.1:8000/api';

interface Book {
  id: number;
  title: string;
  author: string;
  publisher: string;
  year_publication: number;
}

interface Reader {
  id: number;
  email: string;
  role: string;
  verified: boolean;
  profile?: {
    full_name: string;
  };
}

interface Request {
  id: number;
  reader_id: number;
  book_id: number;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  created_at: string;
  book?: Book;
  reader?: Reader;
  // Для обратной совместимости
  reader_email?: string;
  reader_name?: string;
  book_title?: string;
}

const RequestsManager = () => {
  const [requests, setRequests] = useState<Request[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState<string | undefined>(undefined);
  const [dateRange, setDateRange] = useState<[Dayjs | null, Dayjs | null] | null>(null);
  const navigate = useNavigate();

  const fetchRequests = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        navigate('/');
        return;
      }

      const params = new URLSearchParams();
      if (query) params.set('q', query);
      if (status) params.set('status', status);
      if (dateRange?.[0]) params.set('from', dateRange[0].toISOString());
      if (dateRange?.[1]) params.set('to', dateRange[1].toISOString());

      const url = params.toString() 
        ? `${API_BASE}/requests?${params.toString()}`
        : `${API_BASE}/requests`;

      const resp = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (resp.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_role');
        navigate('/');
        return;
      }

      if (!resp.ok) throw new Error('Не удалось загрузить запросы');

      const contentType = resp.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error(`Неверный формат ответа: ${contentType}`);
      }

      const text = await resp.text();
      console.log('Response text:', text);
      
      try {
        const data = JSON.parse(text);
        console.log('Parsed data:', data);
        
        // Проверяем, что данные - это массив
        if (!Array.isArray(data)) {
          if (data.items && Array.isArray(data.items)) {
            setRequests(data.items);
          } else {
            throw new Error('Данные не являются массивом');
          }
        } else {
          setRequests(data);
        }
      } catch (parseError) {
        console.error('JSON parse error:', parseError);
        throw new Error(`Ошибка парсинга JSON: ${parseError instanceof Error ? parseError.message : String(parseError)}`);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Неизвестная ошибка');
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (requestId: number) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        navigate('/');
        return;
      }

      const resp = await fetch(`${API_BASE}/requests/${requestId}/give`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!resp.ok) throw new Error('Не удалось обработать запрос');

      message.success('Выдача книги зафиксированна');
      fetchRequests();
    } catch (e) {
      message.error(e instanceof Error ? e.message : 'Неизвестная ошибка');
    }
  };

  const handleSearch = () => {
    fetchRequests();
  };

  useEffect(() => {
    fetchRequests();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading) return <div className="flex justify-center py-20"><Spin size="large" /></div>;
  if (error) return <Alert type="error" message="Ошибка" description={error} />;

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-semibold mb-6">Управление запросами</h1>
      
      <div className="flex flex-wrap gap-3 mb-4">
        <Input
          placeholder="Поиск (книга, читатель)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{ width: 240 }}
          allowClear
        />
        <Select
          allowClear
          placeholder="Статус"
          style={{ width: 180 }}
          value={status}
          onChange={(v) => setStatus(v)}
          options={[
            { label: 'Ожидает', value: 'PENDING' },
            { label: 'Одобрено', value: 'APPROVED' },
            { label: 'Отклонено', value: 'REJECTED' },
          ]}
        />
        <RangePicker 
          value={dateRange as any} 
          onChange={(v) => setDateRange(v as any)}
          placeholder={['Дата от', 'Дата до']}
        />
        <Button onClick={handleSearch} type="default">Фильтровать</Button>
      </div>

      <Table
        dataSource={requests}
        rowKey="id"
        columns={[
          {
            title: 'Читатель',
            key: 'reader',
            render: (_: unknown, record: Request) => {
              const email = record.reader?.email || record.reader_email || '—';
              const name = record.reader?.profile?.full_name || record.reader_name || email.split('@')[0] || '—';
              return (
                <div>
                  <div>{name}</div>
                  <div className="text-sm text-gray-500">{email}</div>
                </div>
              );
            },
          },
          {
            title: 'Книга',
            key: 'book',
            render: (_: unknown, record: Request) => {
              const title = record.book?.title || record.book_title || '—';
              return title;
            },
          },
          {
            title: 'Статус',
            dataIndex: 'status',
            key: 'status',
            render: (status: string) => {
              const config = {
                PENDING: {
                  icon: <ClockCircleOutlined style={{ fontSize: '18px' }} />,
                  color: '#faad14',
                  label: 'Ожидает',
                },
                FULFILLED: {
                  icon: <CheckCircleOutlined style={{ fontSize: '18px' }} />,
                  color: '#52c41a',
                  label: 'Одобрено',
                },
                QUEUED: {
                  icon: <PauseCircleOutlined style={{ fontSize: '18px' }} />,
                  color: '#1160AB',
                  label: 'В очереди',
                },
              };

              const statusConfig = config[status as keyof typeof config];
              
              if (!statusConfig) {
                return <span>{status}</span>;
              }
              
              return (
                <Tooltip title={statusConfig.label}>
                  <span style={{ color: statusConfig.color }}>
                    {statusConfig.icon}
                  </span>
                </Tooltip>
              );
            },
          },
          {
            title: 'Дата запроса',
            dataIndex: 'created_at',
            key: 'created_at',
            render: (date: string) => new Date(date).toLocaleDateString('ru-RU'),
          },
          {
            title: 'Действия',
            key: 'actions',
            render: (_: unknown, record: Request) => (
              record.status === 'PENDING' && (
                <Button
                  type="primary"
                  size="small"
                  onClick={() => handleAction(record.id)}
                >
                  Выдать кнгиу
                </Button>
              )
            ),
          },
        ]}
      />
    </div>
  );
};

export default RequestsManager;