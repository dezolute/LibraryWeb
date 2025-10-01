import { useEffect, useState } from 'react';
import { Card, Typography, Descriptions, Button, Table, Tag, Spin, Flex } from 'antd';
import { useNavigate } from 'react-router-dom';

const { Title } = Typography;

const statusColor = {
  PENDING: 'orange',
  APPROVED: 'green',
  REJECTED: 'red',
};

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
      render: (status) => <Tag color={statusColor[status]}>{status}</Tag>,
    },
    {
      title: 'Создано',
      dataIndex: 'created_at',
      key: 'created_at',
    },
    {
      title: 'Обновлено',
      dataIndex: 'updated_at',
      key: 'updated_at',
    },
  ];

const UserAccount = () => {
  const [user, setUser] = useState(null);
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch('/api/users/me', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
      }).then((res) => res.json()),
    ])
      .then(([userData]) => {
        setUser(userData);
        setRequests(userData.requests);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading || !user) return <Spin />;

  return (
    <div style={{ display: 'flex', gap: '24px', alignItems: 'flex-start' }}>
      <div style={{ width: '400px', textAlign: 'center' }}>
        <Title level={2}>Аккаунт пользователя</Title>
        <Card>
          <Descriptions bordered column={1}>
            <Descriptions.Item label="Имя">{user.name}</Descriptions.Item>
            <Descriptions.Item label="Email">{user.email}</Descriptions.Item>
            <Descriptions.Item label="Роль">{user.role}</Descriptions.Item>
            <Descriptions.Item label="Дата регистрации">{user.created_at}</Descriptions.Item>
          </Descriptions>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 20 }}>
            <Button type='primary'>Создать запрос</Button>
            <Button>Выйти из аккаунта</Button>
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
