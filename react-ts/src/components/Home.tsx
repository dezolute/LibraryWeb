import { useState } from 'react';
import { Typography, Button, Card, Row, Col, Space } from 'antd';
import { BookOutlined, UserOutlined, TeamOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { AuthModal } from './auth/AuthModal';

const { Title, Paragraph } = Typography;

export const Home = () => {
  const navigate = useNavigate();
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  const features = [
    {
      icon: <BookOutlined className="text-4xl text-blue-600" />,
      title: 'Огромная коллекция',
      description: 'Тысячи книг различных жанров и авторов в нашей библиотеке'
    },
    {
      icon: <UserOutlined className="text-4xl text-green-600" />,
      title: 'Личный кабинет',
      description: 'Удобное управление заказами и история чтения'
    },
    {
      icon: <TeamOutlined className="text-4xl text-purple-600" />,
      title: 'Сообщество',
      description: 'Присоединяйтесь к сообществу любителей чтения'
    }
  ];

  return (
    <div className="max-w-6xl mx-auto px-4">
      {/* Hero секция */}
      <div className="text-center py-16">
        <Title>
          Добро пожаловать в LibraryWeb
        </Title>
        <Paragraph className="text-lg text-gray-600 mb-8">
          Ваша онлайн библиотека с удобным поиском и доступом к книгам
        </Paragraph>
        <Space size="large">
          <Button type="primary" size="large" onClick={() => navigate('/catalog')}>
            Просмотреть каталог
          </Button>
          <Button size="large" onClick={() => setIsAuthModalOpen(true)}>
            Зарегистрироваться
          </Button>
        </Space>
      </div>

      {/* Секция особенностей */}
      <Row gutter={[32, 32]} className="py-16">
        {features.map((feature, index) => (
          <Col key={index} xs={24} md={8}>
            <Card hoverable className="text-center h-full">
              <div className="mb-4">
                {feature.icon}
              </div>
              <Title level={4} className="mb-4">
                {feature.title}
              </Title>
              <Paragraph className="text-gray-600">
                {feature.description}
              </Paragraph>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Призыв к действию */}
      <div className="text-center py-16 bg-gray-50 rounded-lg mb-16">
        <Title level={2}>
          Начните читать уже сегодня
        </Title>
        <Paragraph className="text-lg text-gray-600 mb-8">
          Присоединяйтесь к нашей библиотеке и получите доступ к тысячам книг
        </Paragraph>
        <Button type="primary" size="large" onClick={() => setIsAuthModalOpen(true)}>
          Создать аккаунт
        </Button>
      </div>
      <AuthModal 
        open={isAuthModalOpen} 
        onClose={() => setIsAuthModalOpen(false)}
      />
    </div>
  );
};