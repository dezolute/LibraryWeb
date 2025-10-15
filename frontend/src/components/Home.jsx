import '@ant-design/v5-patch-for-react-19';
import { Layout, Typography, Space, Card } from 'antd';

const { Content } = Layout;
const { Title, Paragraph, Text } = Typography;

const features = [
  {
    icon: '📚',
    title: 'Каталог книг',
    description: 'Просматривайте коллекцию и находите интересные издания.',
  },
  {
    icon: '📥',
    title: 'Запросы на получение',
    description: 'Оформляйте запросы на выдачу книг и отслеживайте их статус.',
  },
  {
    icon: '🔍',
    title: 'Поиск',
    description: 'Находите книги по автору, названию или году издания.',
  },
  {
    icon: '👤',
    title: 'Профиль пользователя',
    description: 'Просматривайте свою активность и историю запросов.',
  },
];

const Home = () => {
  return (
    <Content style={{ padding: '60px 40px', maxWidth: 1000, margin: '0 auto' }}>
      <Card
        bordered={false}
        style={{
          background: 'linear-gradient(135deg, #f0f2f5 0%, #ffffff 100%)',
          padding: '40px',
          borderRadius: '16px',
          boxShadow: '0 4px 20px rgba(0,0,0,0.05)',
        }}
      >
        <Title level={1} style={{ textAlign: 'center', marginBottom: 20 }}>
          📖 Добро пожаловать в <span style={{ color: '#1677ff' }}>LibraryWeb</span>
        </Title>

        <Paragraph style={{ fontSize: 18, textAlign: 'center', marginBottom: 40 }}>
          Это главная страница вашего приложения для работы с библиотекой. Ниже — ключевые возможности:
        </Paragraph>

        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {features.map((feature, index) => (
            <Card
              key={index}
              hoverable
              style={{
                borderRadius: 12,
                backgroundColor: '#fafafa',
                border: '1px solid #f0f0f0',
                transition: 'transform 0.2s ease',
              }}
              bodyStyle={{ padding: '20px 24px' }}
              onMouseEnter={(e) => (e.currentTarget.style.transform = 'scale(1.01)')}
              onMouseLeave={(e) => (e.currentTarget.style.transform = 'scale(1.0)')}
            >
              <Paragraph style={{ fontSize: 16, margin: 0 }}>
                <span style={{ fontSize: 20 }}>{feature.icon}</span>{' '}
                <Text strong>{feature.title}</Text> — {feature.description}
              </Paragraph>
            </Card>
          ))}
        </Space>
      </Card>
    </Content>
  );
};

export default Home;
