import { useEffect, useState } from 'react';
import { Avatar, Card, Spin, Alert, Button, Table, Tag, Tabs, Grid } from 'antd';
import { useNavigate } from 'react-router-dom';
import CONFIG from './consts/config';

const { useBreakpoint } = Grid;
const API_BASE = CONFIG.API_URL;

interface Profile {
  full_name: string;
  avatar_url?: string | null;
}

interface Book {
  id: number;
  title: string;
  author: string;
  publisher: string;
  year_publication: number;
}

interface BookCopy {
  serial_num: string;
  book: Book;
}

interface Request {
  id: number;
  book_id: number;
  reader_id: number;
  status: 'PENDING' | 'FULFILLED' | 'QUEUED' | 'APPROVED' | 'REJECTED';
  created_at: string;
  book?: Book;
  book_title?: string;
}

interface Loan {
  id: number;
  reader_id: number;
  copy_id: string;
  issue_date: string;
  due_date: string;
  return_date?: string | null;
  book_copy?: BookCopy;
  book_title?: string;
}

interface Reader {
  id: number;
  email: string;
  role: string;
  verified: boolean;
  profile: Profile;
  requests: Request[];
  loans: Loan[];
}

const Account = () => {
  const [reader, setReader] = useState<Reader | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const screens = useBreakpoint();
  const isMobile = !screens.md; // xs/sm — мобильный [web:112]

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      navigate('/');
      return;
    }

    const fetchMe = async () => {
      setLoading(true);
      setError(null);
      try {
        const resp = await fetch(`${API_BASE}/readers/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (resp.status === 401) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('user_role');
          navigate('/');
          return;
        }
        if (!resp.ok) throw new Error('Не удалось загрузить профиль');

        const contentType = resp.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
          throw new Error(`Неверный формат ответа: ${contentType}`);
        }

        const text = await resp.text();
        const data = JSON.parse(text);
        setReader(data);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchMe();
  }, [navigate]);

  if (loading) return <div className="flex justify-center py-20"><Spin size="large" /></div>;
  if (error) return <Alert type="error" message="Ошибка" description={error} />;
  if (!reader) return null;

  const requestsColumns = [
    {
      title: 'Книга',
      key: 'book',
      ellipsis: true,
      render: (_: unknown, record: Request) =>
        record.book?.title || record.book_title || '—',
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colors: Record<string, string> = {
          PENDING: 'gold',
          FULFILLED: 'green',
          QUEUED: 'blue',
          APPROVED: 'green',
          REJECTED: 'red',
        };
        const labels: Record<string, string> = {
          PENDING: 'Ожидает',
          FULFILLED: 'Выполнено',
          QUEUED: 'В очереди',
          APPROVED: 'Одобрено',
          REJECTED: 'Отклонено',
        };
        const color = colors[status] || 'default';
        const label = labels[status] || status;
        return <Tag color={color}>{label}</Tag>;
      },
    },
    {
      title: 'Дата',
      dataIndex: 'created_at',
      key: 'created_at',
      width: isMobile ? 110 : undefined,
      render: (date: string) => new Date(date).toLocaleDateString('ru-RU'),
    },
  ];

  const loansColumns = [
    {
      title: 'Книга',
      key: 'book',
      ellipsis: true,
      render: (_: unknown, record: Loan) =>
        record.book_copy?.book?.title || record.book_title || '—',
    },
    {
      title: 'Статус',
      key: 'status',
      render: (_: unknown, record: Loan) => {
        let status = 'ACTIVE';
        if (record.return_date) {
          status = 'RETURNED';
        } else {
          const dueDate = new Date(record.due_date);
          const today = new Date();
          today.setHours(0, 0, 0, 0);
          if (dueDate < today) status = 'OVERDUE';
        }
        const colors: Record<string, string> = {
          ACTIVE: 'processing',
          RETURNED: 'success',
          OVERDUE: 'error',
        };
        const labels: Record<string, string> = {
          ACTIVE: 'Активна',
          RETURNED: 'Возвращена',
          OVERDUE: 'Просрочена',
        };
        return <Tag color={colors[status]}>{labels[status]}</Tag>;
      },
    },
    {
      title: 'Выдана',
      dataIndex: 'issue_date',
      key: 'issue_date',
      width: isMobile ? 110 : undefined,
      render: (date: string) => new Date(date).toLocaleDateString('ru-RU'),
    },
    {
      title: 'Вернуть до',
      dataIndex: 'due_date',
      key: 'due_date',
      width: isMobile ? 110 : undefined,
      render: (date: string) => new Date(date).toLocaleDateString('ru-RU'),
    },
    {
      title: 'Возвращена',
      dataIndex: 'return_date',
      key: 'return_date',
      width: isMobile ? 110 : undefined,
      render: (date: string | null | undefined) =>
        date ? new Date(date).toLocaleDateString('ru-RU') : '-',
    },
  ];

  return (
    <div className="max-w-4xl mx-auto px-2 sm:px-4">
      <Card bodyStyle={{ padding: isMobile ? 16 : 24 }}>
        <div className={`flex ${isMobile ? 'flex-col items-start' : 'items-center'} gap-4 mb-6`}>
          <Avatar
            size={isMobile ? 72 : 96}
            src={
              reader.profile?.avatar_url
                ? (reader.profile.avatar_url.startsWith('http')
                    ? reader.profile.avatar_url
                    : `${API_BASE}${reader.profile.avatar_url}`)
                : undefined
            }
          />
          <div>
            <h2 className={`${isMobile ? 'text-xl' : 'text-2xl'} font-semibold`}>
              {reader.profile?.full_name || 'Пользователь'}
            </h2>
            <div className="text-sm text-gray-600 break-all">{reader.email}</div>
          </div>
        </div>

        <Tabs
          defaultActiveKey="requests"
          destroyInactiveTabPane
          tabBarGutter={isMobile ? 8 : 24}
          size={isMobile ? 'small' : 'middle'}
          items={[
            {
              key: 'requests',
              label: `Заявки (${reader.requests.length})`,
              children: (
                <Table<Request>
                  size={isMobile ? 'small' : 'middle'}
                  dataSource={reader.requests}
                  rowKey="id"
                  pagination={false}
                  columns={requestsColumns}
                  scroll={isMobile ? { x: 'max-content' } : undefined} // горизонтальный скролл [web:123]
                />
              ),
            },
            {
              key: 'loans',
              label: `Выданные книги (${reader.loans.length})`,
              children: (
                <Table<Loan>
                  size={isMobile ? 'small' : 'middle'}
                  dataSource={reader.loans}
                  rowKey="id"
                  pagination={false}
                  columns={loansColumns}
                  scroll={isMobile ? { x: 'max-content' } : undefined}
                />
              ),
            },
          ]}
        />

        <div className="mt-6 flex justify-end">
          <Button type="primary" onClick={() => navigate('/catalog')}>
            Просмотреть каталог
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default Account;