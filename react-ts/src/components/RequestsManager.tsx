import { useEffect, useMemo, useState } from 'react';
import { Table, Button, message, Spin, Alert, Tooltip, Input, Select, DatePicker } from 'antd';
import { useNavigate } from 'react-router-dom';
import {
  ClockCircleOutlined,
  CheckCircleOutlined,
  PauseCircleOutlined
} from '@ant-design/icons';
import dayjs, { type Dayjs } from 'dayjs';
import CONFIG from './consts/config';

const { RangePicker } = DatePicker;
const API_BASE = CONFIG.API_URL;

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
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | string; // у тебя в UI ещё FULFILLED/QUEUED
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

  // фильтры (только UI)
  const [book, setBook] = useState('');
  const [reader, setReader] = useState('');
  const [status, setStatus] = useState<string | undefined>(undefined);
  const [dateRange, setDateRange] = useState<[Dayjs | null, Dayjs | null] | null>(null);

  // клиентская пагинация
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const navigate = useNavigate();

  // 1) грузим данные без фильтров с сервера
  const fetchRequests = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        navigate('/');
        return;
      }

      const resp = await fetch(`${API_BASE}/requests`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (resp.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_role');
        navigate('/');
        return;
      }

      if (!resp.ok) throw new Error('Не удалось загрузить запросы');

      const contentType = resp.headers.get('content-type') || '';
      const text = await resp.text();

      let data: any;
      if (contentType.includes('application/json')) data = JSON.parse(text);
      else data = JSON.parse(text); // оставил твою логику "на всякий случай"

      if (Array.isArray(data)) setRequests(data);
      else if (data.items && Array.isArray(data.items)) setRequests(data.items);
      else throw new Error('Данные не являются массивом');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Неизвестная ошибка');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 2) фильтрация на фронте
  const filteredRequests = useMemo(() => {
    const bookQ = book.trim().toLowerCase();
    const readerQ = reader.trim().toLowerCase();

    const from = dateRange?.[0] ? dateRange[0].startOf('day') : null;
    const to = dateRange?.[1] ? dateRange[1].endOf('day') : null;

    return requests.filter((r) => {
      const title = (r.book?.title || r.book_title || '').toLowerCase();

      const readerName = (r.reader?.profile?.full_name || r.reader_name || '').toLowerCase();
      const readerEmail = (r.reader?.email || r.reader_email || '').toLowerCase();

      if (bookQ && !title.includes(bookQ)) return false;

      if (readerQ) {
        const ok = readerName.includes(readerQ) || readerEmail.includes(readerQ);
        if (!ok) return false;
      }

      if (status && r.status !== status) return false;

      if (from || to) {
        const d = dayjs(r.created_at);
        if (!d.isValid()) return false;
        if (from && d.isBefore(from)) return false;
        if (to && d.isAfter(to)) return false;
      }

      return true;
    });
  }, [requests, book, reader, status, dateRange]);

  // сброс страницы при изменении фильтров
  useEffect(() => {
    setPage(1);
  }, [book, reader, status, dateRange]);

  // 3) клиентская пагинация (режем filteredRequests)
  const pagedRequests = useMemo(() => {
    const start = (page - 1) * pageSize;
    return filteredRequests.slice(start, start + pageSize);
  }, [filteredRequests, page, pageSize]);

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
      fetchRequests(); // чтобы статусы обновились
    } catch (e) {
      message.error(e instanceof Error ? e.message : 'Неизвестная ошибка');
    }
  };

  // "Фильтровать" теперь не ходит в API — только сбрасывает страницу (можно вообще удалить кнопку)
  const handleSearch = () => setPage(1);

  if (loading) return <div className="flex justify-center py-20"><Spin size="large" /></div>;
  if (error) return <Alert type="error" message="Ошибка" description={error} />;

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-semibold mb-6">Управление заявками</h1>

      <div className="flex flex-wrap gap-3 mb-4">
        <Input
          placeholder="Книга"
          value={book}
          onChange={(e) => setBook(e.target.value)}
          style={{ width: 200 }}
          allowClear
        />
        <Input
          placeholder="Читатель"
          value={reader}
          onChange={(e) => setReader(e.target.value)}
          style={{ width: 200 }}
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
            { label: 'Завершён', value: 'FULFILLED' },
            { label: 'В очереди', value: 'QUEUED' },
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
        dataSource={pagedRequests}
        rowKey="id"
        pagination={{
          current: page,
          pageSize,
          total: filteredRequests.length,
          showSizeChanger: true,
          onChange: (p, ps) => { setPage(p); setPageSize(ps); },
        }}
        columns={[
          {
            title: 'Читатель',
            key: 'reader',
            render: (_: unknown, record: Request) => {
              const email = record.reader?.email || record.reader_email || '—';
              const name = record.reader?.profile?.full_name || record.reader_name || '—';
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
            render: (_: unknown, record: Request) => record.book?.title || record.book_title || '—',
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
              } as const;

              const statusConfig = (config as any)[status];
              if (!statusConfig) return <span>{status}</span>;

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
                <Button type="primary" size="small" onClick={() => handleAction(record.id)}>
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