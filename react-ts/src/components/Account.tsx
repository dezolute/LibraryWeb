import { useEffect, useMemo, useState } from 'react';
import { Avatar, Card, Spin, Alert, Button, Table, Tag, Tabs, Grid, message, Popconfirm, Space } from 'antd';
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

const authHeaders = (): Record<string, string> => {
  const token = localStorage.getItem('access_token');
  const h: Record<string, string> = {};
  if (token) h.Authorization = `Bearer ${token}`;
  return h;
};

async function parseOrText(resp: Response) {
  const text = await resp.text();
  try {
    return text ? JSON.parse(text) : null;
  } catch {
    return text;
  }
}

const Account = () => {
  const [reader, setReader] = useState<Reader | null>(null);
  const [loading, setLoading] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();
  const screens = useBreakpoint();
  const isMobile = !screens.md;

  const ensureAuth = () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      navigate('/');
      return false;
    }
    return true;
  };

  const fetchMe = async () => {
    if (!ensureAuth()) return;

    setLoading(true);
    setError(null);
    try {
      const resp = await fetch(`${API_BASE}/readers/me`, {
        headers: { ...authHeaders() },
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

      const data = await resp.json();
      setReader(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const deleteRequest = async (requestId: number) => {
    if (!ensureAuth()) return;

    setDeletingId(requestId);
    try {
      const resp = await fetch(`${API_BASE}/readers/me/requests/${requestId}`, {
        method: 'DELETE',
        headers: { ...authHeaders() },
      });

      if (resp.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_role');
        navigate('/');
        return;
      }

      if (!resp.ok) {
        const data = await parseOrText(resp);
        throw new Error((data as any)?.detail || (data as any)?.message || 'Не удалось удалить заявку');
      }

      message.success('Заявка удалена');
      await fetchMe();
    } catch (e) {
      message.error(e instanceof Error ? e.message : 'Ошибка удаления');
    } finally {
      setDeletingId(null);
    }
  };

  // ✅ ХУКИ ДОЛЖНЫ БЫТЬ ДО РАННИХ return
  const requestsColumns = useMemo(() => {
    return [
      {
        title: 'Книга',
        key: 'book',
        ellipsis: true,
        render: (_: unknown, record: Request) => record.book?.title || record.book_title || '—',
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
          return <Tag color={colors[status] || 'default'}>{labels[status] || status}</Tag>;
        },
      },
      {
        title: 'Дата',
        dataIndex: 'created_at',
        key: 'created_at',
        width: isMobile ? 110 : undefined,
        render: (date: string) => new Date(date).toLocaleDateString('ru-RU'),
      },
      {
        title: 'Действия',
        key: 'actions',
        width: isMobile ? 120 : 160,
        render: (_: unknown, record: Request) => {
          const canDelete = record.status === 'PENDING' || record.status === 'QUEUED';
          if (!canDelete) return <span className="text-gray-400">—</span>;

          return (
            <Popconfirm
              title="Удалить заявку?"
              description="Действие нельзя отменить."
              okText="Удалить"
              cancelText="Отмена"
              onConfirm={() => deleteRequest(record.id)}
            >
              <Button danger size={isMobile ? 'small' : 'middle'} loading={deletingId === record.id}>
                Удалить
              </Button>
            </Popconfirm>
          );
        },
      },
    ];
  }, [isMobile, deletingId]);

  const loansColumns = useMemo(() => {
    return [
      {
        title: 'Книга',
        key: 'book',
        ellipsis: true,
        render: (_: unknown, record: Loan) => record.book_copy?.book?.title || record.book_title || '—',
      },
      {
        title: 'Статус',
        key: 'status',
        render: (_: unknown, record: Loan) => {
          let status = 'ACTIVE';
          if (record.return_date) status = 'RETURNED';
          else {
            const dueDate = new Date(record.due_date);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            if (dueDate < today) status = 'OVERDUE';
          }
          const colors: Record<string, string> = { ACTIVE: 'processing', RETURNED: 'success', OVERDUE: 'error' };
          const labels: Record<string, string> = { ACTIVE: 'Активна', RETURNED: 'Возвращена', OVERDUE: 'Просрочена' };
          return <Tag color={colors[status] || 'default'}>{labels[status] || status}</Tag>;
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
        render: (date: string | null | undefined) => (date ? new Date(date).toLocaleDateString('ru-RU') : '-'),
      },
    ];
  }, [isMobile]);

  useEffect(() => {
    fetchMe();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [navigate]);

  if (loading) return <div className="flex justify-center py-20"><Spin size="large" /></div>;
  if (error) return <Alert type="error" message="Ошибка" description={error} />;
  if (!reader) return null;

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
                  columns={requestsColumns as any}
                  scroll={isMobile ? { x: 'max-content' } : undefined}
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
                  columns={loansColumns as any}
                  scroll={isMobile ? { x: 'max-content' } : undefined}
                />
              ),
            },
          ]}
        />

        <div className="mt-6 flex justify-end">
          <Space>
            <Button onClick={() => fetchMe()} disabled={loading}>
              Обновить
            </Button>
            <Button type="primary" onClick={() => navigate('/catalog')}>
              Просмотреть каталог
            </Button>
          </Space>
        </div>
      </Card>
    </div>
  );
};

export default Account;