import { useEffect, useState } from 'react';
import { Table, Tag, Typography, Spin, Modal, Select, message } from 'antd';
import { CONFIG } from '../constants/config';

const { Title } = Typography;
const apiUrl = CONFIG.API_URL;
const accessToken = localStorage.getItem('access_token');
const statusOptions = ['GIVEN', 'RETURNED'];

const EmployeeRequestsPage = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRequests = async () => {
      if (!accessToken) {
        Modal.warning({
          title: 'Нет доступа',
          content: 'Вы не авторизованы.',
        });
        setLoading(false);
        return;
      }

      try {
        const userRes = await fetch(`${apiUrl}/users/me`, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
        });

        if (!userRes.ok) throw new Error('Ошибка авторизации');

        const user = await userRes.json();
        const role = user.role;

        if (role !== 'EMPLOYEE' && role !== 'ADMIN') {
          Modal.warning({
            title: 'Недостаточно прав',
            content: 'Эта страница доступна только для сотрудников или администраторов.',
          });
          setLoading(false);
          return;
        }

        const response = await fetch(`${apiUrl}/requests`, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) throw new Error('Ошибка загрузки запросов');

        const data = await response.json();
        setRequests(data.items || []);
      } catch (error) {
        Modal.error({
          title: 'Ошибка',
          content: error.message || 'Не удалось загрузить данные.',
        });
      } finally {
        setLoading(false);
      }
    };

    fetchRequests();
  }, []);

  const handleStatusChange = async (requestId, newStatus) => {
    try {
      const response = await fetch(`${apiUrl}/requests/${requestId}?new_status=${newStatus}`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) throw new Error('Ошибка при обновлении статуса');

      message.success('Статус обновлён');
      setRequests((prev) =>
        prev.map((req) =>
          req.id === requestId ? { ...req, status: newStatus } : req
        )
      );
    } catch (error) {
      message.error(error.message || 'Не удалось обновить статус');
    }
  };

  const columns = [
    {
      title: 'ID запроса',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: 'Пользователь',
      dataIndex: ['user', 'name'],
      key: 'user',
      render: (_, record) => (
        <div>
          <strong>{record.user.name}</strong>
          <br />
          <span>{record.user.email}</span>
        </div>
      ),
    },
    {
      title: 'Книга',
      dataIndex: ['book', 'title'],
      key: 'book',
      render: (_, record) => (
        <div>
          <strong>{record.book.title}</strong>
          <br />
          <span>{record.book.author} ({record.book.year_publication})</span>
        </div>
      ),
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      render: (status, record) => (
        <Select
          value={status}
          onChange={(value) => handleStatusChange(record.id, value)}
          style={{ width: 120 }}
          options={statusOptions.map((s) => ({
            label: s,
            value: s,
          }))}
        />
      ),
    },
    {
      title: 'Приоритет',
      dataIndex: ['book', 'priority'],
      key: 'priority',
      render: (priority) => {
        const color = priority === 'HIGH' ? 'red' : 'default';
        return <Tag color={color}>{priority}</Tag>;
      },
    },
    {
      title: 'Дата запроса',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => new Date(date).toLocaleString('ru-RU'),
    },
  ];

  if (loading) return <Spin tip="Загрузка запросов..." />;

  return (
    <div style={{ padding: '40px' }}>
      <Title level={3}>📚 Запросы пользователей</Title>
      <Table
        dataSource={requests}
        columns={columns}
        rowKey="id"
        pagination={{ pageSize: 20 }}
      />
    </div>
  );
};

export default EmployeeRequestsPage;
