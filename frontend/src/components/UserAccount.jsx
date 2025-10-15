import '@ant-design/v5-patch-for-react-19';
import { useEffect, useRef, useState } from 'react';
import { Card, Typography, Descriptions, Button, Table, Tag, Spin, Modal, Popconfirm } from 'antd';
import { useNavigate } from 'react-router-dom';
import { CONFIG } from '../constants/config';

const { Title } = Typography;
const apiUrl = CONFIG.API_URL;

const icon = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%2Fid%2FOIP._wBb0zSW4SrlHG1jCjL2xQHaHa%3Fcb%3D12%26pid%3DApi&f=1&ipt=fe2589cb6fa4c7f72366e4e99b1f815178d7e52c33941d66ee25a51165187993&ipo=images";

const statusColor = {
  ACCEPTED: 'orange',
  IN_QUEUED: 'purple',
  AWAITING: 'blue',
  GIVEN: 'green',
};

const titleStatus = {
  ACCEPTED: 'Принят',
  IN_QUEUED: 'В очереди',
  AWAITING: 'Ожидает вас',
  GIVEN: 'Отдан',
};

const roleTranslation = {
  USER: 'Пользователь',
  EMPLOYEE: 'Работник',
  ADMIN: 'Администратор',
}

const roleColorMap = {
  ADMIN: '#f7ba2a',
  EMPLOYEE: '#52c41a',
  USER: '#1890ff',
};

const dateParse = (raw) => {
  const dateOnly = raw.split('T')[0];
  const [year, month, day] = dateOnly.split('-');
  return `${day}.${month}.${year}`;
};

const UserAccount = () => {
  const accessToken = useRef(localStorage.getItem('access_token'));
  const [user, setUser] = useState(null);
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const logout = () => {
    localStorage.removeItem('access_token');
    navigate('/login');
  };

  const goBooks = () => {
    navigate('/books');
  };

  const deleteRequest = async (id) => {
    try {
      const response = await fetch(`${apiUrl}/requests/${id}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${accessToken.current}`,
        },
      });

      if (!response.ok) throw new Error('Ошибка при удалении запроса');

      setRequests((prev) => prev.filter((r) => r.id !== id));
    } catch (err) {
      Modal.error({
        title: 'Ошибка удаления',
        content: err.message || 'Не удалось удалить запрос.',
      });
    }
  };

  useEffect(() => {
    const fetchUser = async () => {
      if (!accessToken) {
        Modal.warning({
          title: 'Не авторизован',
          content: 'Пожалуйста, войдите в систему.',
        });
        navigate('/login');
        return;
      }

      try {
        const response = await fetch(`${apiUrl}/users/me`, {
          headers: {
            Authorization: `Bearer ${accessToken.current}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) throw new Error('Ошибка загрузки пользователя');

        const data = await response.json();
        setUser(data);

        const filtered = (data.requests || []).filter((r) => r.status !== 'RETURNED');
        setRequests(filtered);
      } catch (err) {
        Modal.error({
          title: 'Ошибка авторизации',
          content: err.message || 'Не удалось загрузить данные пользователя.',
        });
        logout();
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  const columns = [
    {
      title: 'Книга',
      dataIndex: ['book', 'title'],
      key: 'book',
    },
    {
      title: 'Автор',
      dataIndex: ['book', 'author'],
      key: 'author',
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      render: (status) => <Tag color={statusColor[status]}>{titleStatus[status]}</Tag>,
    },
    {
      title: 'Создано',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (created_at) => dateParse(created_at),
    },
    {
      title: 'Удалить',
      key: 'action',
      render: (_, record) => (
        <Popconfirm
          title="Удалить запрос?"
          onConfirm={() => deleteRequest(record.id)}
          okText="Да"
          cancelText="Нет"
          disabled={record.status === 'GIVEN'}
        >
          <Button danger disabled={record.status === 'GIVEN'}>
            ❌ Удалить
          </Button>
        </Popconfirm>
      ),
    },
  ];

  if (loading || !user) return <Spin tip="Загрузка профиля..." />;

  return (
    <div style={{ display: 'flex', gap: '24px', alignItems: 'flex-start' }}>
      <div style={{ width: '400px', textAlign: 'center' }}>
        <Title level={3}>Аккаунт пользователя</Title>
        <Card>
          <Descriptions
            bordered
            column={1}
            size="middle"
            labelStyle={{ fontWeight: 'bold', backgroundColor: '#f0f2f5', padding: '12px' }}
            contentStyle={{ padding: '12px' }}
          >
            <Descriptions.Item label="ФИО">
              <span style={{ fontSize: '16px', fontWeight: 500 }}>{user.name}</span>
            </Descriptions.Item>

            <Descriptions.Item label="Аватарка">
              <img
                src={user.icon ?? icon}
                alt="Аватар пользователя"
                loading="lazy"
                style={{
                  width: 100,
                  height: 100,
                  objectFit: 'cover',
                  borderRadius: '8px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                }}
              />
            </Descriptions.Item>

            <Descriptions.Item label="Email">
              <a href={`mailto:${user.email}`} style={{ color: '#1677ff' }}>
                {user.email}
              </a>
            </Descriptions.Item>

            <Descriptions.Item label="Роль">
              <span style={{
                display: 'inline-block',
                padding: '4px 12px',
                backgroundColor: roleColorMap[user.role],
                borderRadius: '16px',
                fontWeight: 500,
                color: '#fff',
              }}>
                {roleTranslation[user.role]}
              </span>
            </Descriptions.Item>

            <Descriptions.Item label="Дата регистрации">
              <span style={{ fontStyle: 'italic', color: '#888' }}>
                {dateParse(user.created_at)}
              </span>
            </Descriptions.Item>
          </Descriptions>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 20 }}>
            <Button type="primary" onClick={goBooks}>Смотреть каталог</Button>
            <Button onClick={logout}>Выйти из аккаунта</Button>
          </div>
        </Card>
      </div>
      <div style={{ flex: 1, textAlign: 'center' }}>
        <Title level={3}>Запросы на книги</Title>
        <Table dataSource={requests} columns={columns} rowKey="id" pagination={false} />
      </div>
    </div>
  );
};

export default UserAccount;