import { Layout, Typography } from 'antd';

const { Content } = Layout;
const { Title } = Typography;

const Home = () => {
  return (
      <Content style={{ padding: '50px', textAlign: 'center' }}>
        <Title>Добро пожаловать!</Title>
        <p>Это главная страница вашего приложения.</p>
      </Content>
  );
};

export default Home;
