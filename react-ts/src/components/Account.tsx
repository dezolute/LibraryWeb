import { useEffect, useState } from 'react';
import { Avatar, Card, Spin, Alert, Button, Table, Tag, Tabs } from 'antd';
import { useNavigate } from 'react-router-dom';
import CONFIG from './consts/config';

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
  book_title?: string; // для обратной совместимости
}

interface Loan {
  id: number;
  reader_id: number;
  copy_id: string;
  issue_date: string;
  due_date: string;
  return_date?: string | null;
  book_copy?: BookCopy;
  book_title?: string; // для обратной совместимости
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
          // токен недействителен — редирект на главную
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
        console.log('Response text:', text);
        try {
          const data = JSON.parse(text);
          setReader(data);
        } catch (parseError) {
          console.error('JSON parse error:', parseError);
          throw new Error(`Ошибка парсинга JSON: ${parseError instanceof Error ? parseError.message : String(parseError)}`);
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchMe();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading) return <div className="flex justify-center py-20"><Spin size="large" /></div>;
  if (error) return <Alert type="error" message="Ошибка" description={error} />;
  if (!reader) return null;

  return (
    <div className="max-w-4xl mx-auto px-4">
      <Card>
        <div className="flex items-center gap-6 mb-6">
          <Avatar size={96} src={reader.profile?.avatar_url ? (reader.profile.avatar_url.startsWith('http') ? reader.profile.avatar_url : `${API_BASE}${reader.profile.avatar_url}`) : undefined} />
          <div>
            <h2 className="text-2xl font-semibold">{reader.profile?.full_name || 'Пользователь'}</h2>
            <div className="text-sm text-gray-600">{reader.email}</div>
          </div>
        </div>

        <Tabs
          defaultActiveKey="requests"
          items={[
            {
              key: 'requests',
              label: `Заявки (${reader.requests.length})`,
              children: (
                <Table
                  dataSource={reader.requests}
                  rowKey="id"
                  pagination={false}
                  columns={[
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
                      render: (date: string) => new Date(date).toLocaleDateString('ru-RU'),
                    },
                  ]}
                />
              ),
            },
            {
              key: 'loans',
              label: `Выданные книги (${reader.loans.length})`,
              children: (
                <Table
                  dataSource={reader.loans}
                  rowKey="id"
                  pagination={false}
                  columns={[
                    {
                      title: 'Книга',
                      key: 'book',
                      render: (_: unknown, record: Loan) => {
                        const title = record.book_copy?.book?.title || record.book_title || '—';
                        return title;
                      },
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
                          if (dueDate < today) {
                            status = 'OVERDUE';
                          }
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
                        const color = colors[status] || 'default';
                        const label = labels[status] || status;
                        return <Tag color={color}>{label}</Tag>;
                      },
                    },
                    {
                      title: 'Выдана',
                      dataIndex: 'issue_date',
                      key: 'issue_date',
                      render: (date: string) => new Date(date).toLocaleDateString('ru-RU'),
                    },
                    {
                      title: 'Вернуть до',
                      dataIndex: 'due_date',
                      key: 'due_date',
                      render: (date: string) => new Date(date).toLocaleDateString('ru-RU'),
                    },
                    {
                      title: 'Возвращена',
                      dataIndex: 'return_date',
                      key: 'return_date',
                      render: (date: string | null | undefined) => date ? new Date(date).toLocaleDateString('ru-RU') : '-',
                    },
                  ]}
                />
              ),
            },
          ]}
        />

        <div className="mt-6">
          <Button type="primary" onClick={() => navigate('/catalog')}>Просмотреть каталог</Button>
        </div>
      </Card>
    </div>
  );
};

export default Account;
