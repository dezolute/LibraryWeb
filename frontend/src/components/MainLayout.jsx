import { Layout, Menu } from 'antd';
import { Link, useLocation } from 'react-router-dom';

const { Header, Content, Footer } = Layout;

const MainLayout = ({ children }) => {
  const location = useLocation();
  const selectedKey = location.pathname === '/' ? 'home' : location.pathname.slice(1);
  const menuItems = [
      {
        key: 'home',
        label: <Link to="/">Главная</Link>,
      },
      {
        key: 'login',
        label: <Link to="/login">Вход</Link>,
      },
      {
        key: 'register',
        label: <Link to="/register">Регистрация</Link>,
      },
      {
        key: 'account',
        label: <Link to="/account">Личный профиль</Link>,
      },
      {
        key: 'books',
        label: <Link to="/books">Книги</Link>,
      },
    ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center' }}>
        <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold', marginRight: '30px' }}>
          LibraryWeb
        </div>
        <Menu theme="dark" mode="horizontal" selectedKeys={[selectedKey]} items={menuItems} />
      </Header>

      <Content style={{ padding: '50px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        {children}
      </Content>

      <Footer style={{ textAlign: 'center' }}>
        © {new Date().getFullYear()} LibraryWeb
      </Footer>
    </Layout>
  );
};

export default MainLayout;
