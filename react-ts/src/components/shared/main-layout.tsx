import { Layout, Menu, Button, Space, theme } from "antd";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useState } from "react";
import { 
  HomeOutlined, 
  BookOutlined, 
  UserOutlined, 
  LoginOutlined,
  LogoutOutlined,
  PlusCircleOutlined
} from "@ant-design/icons";
import { AuthModal } from "../auth/AuthModal";

const { Header, Content, Footer } = Layout;

type Props = {
  children: React.ReactNode;
}

const MainLayout = ({ children }: Props) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const isAuthenticated = !!localStorage.getItem('access_token');
  const userRole = localStorage.getItem('user_role');
  const isEmployee = userRole === 'EMPLOYEE' || userRole === 'ADMIN';

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_role');
    navigate('/');
  };

  return (
    <Layout className="min-h-screen flex flex-col">
      <Header className="flex items-center justify-between px-6 bg-white h-16 fixed w-full z-10 shadow-sm">
        <div className="flex items-center">
          <Link to="/" className="flex items-center">
            <img src="/LibraryWeb.svg" className="w-10 h-10" alt="LibraryWeb Logo" />
            <span className="text-2xl font-semibold text-blue-600 ml-2">LibraryWeb</span>
          </Link>
          <Menu
            mode="horizontal"
            selectedKeys={[location.pathname]}
            className="ml-8"
            items={[
              {
                key: '/',
                icon: <HomeOutlined />,
                label: <Link to="/">Главная</Link>,
              },
              {
                key: '/catalog',
                icon: <BookOutlined />,
                label: <Link to="/catalog">Каталог</Link>,
              },
              ...(isEmployee ? [
                {
                  key: '/employee/book/add',
                  icon: <PlusCircleOutlined />,
                  label: <Link to="/employee/book/add">Добавить книгу</Link>,
                },
                {
                  key: '/loans',
                  icon: <BookOutlined />,
                  label: <Link to="/loans">Выданные книги</Link>,
                },
                {
                  key: '/employee/requests',
                  icon: <BookOutlined />,
                  label: <Link to="/employee/requests">Запросы</Link>,
                },
              ] : []),
            ]}
          />
        </div>
        <Space className="mr-6">
          {isAuthenticated ? (
            <>
              <Button 
                icon={<UserOutlined />}
                onClick={() => navigate('/account')}
              >
                Мой аккаунт
              </Button>
              <Button 
                icon={<LogoutOutlined />}
                onClick={handleLogout}
              >
                Выйти
              </Button>
            </>
          ) : (
            <Button 
              type="primary" 
              icon={<LoginOutlined />}
              onClick={() => setIsAuthModalOpen(true)}
            >
              Войти
            </Button>
          )}
        </Space>
        <AuthModal 
          open={isAuthModalOpen} 
          onClose={() => setIsAuthModalOpen(false)}
        />
      </Header>

      <Content className="flex-grow mt-16 p-6">
        <div
          style={{
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
            padding: 24,
            minHeight: 'calc(100vh - 16rem)'
          }}
          className="w-full max-w-7xl mx-auto"
        >
          {children}
        </div>
      </Content>

      <Footer className="text-center mt-auto py-6 bg-white">
        <Space direction="vertical" size="small">
          <div className="text-gray-600">
            © 2025 LibraryWeb. Все права защищены.
          </div>
          <Space split={<span className="text-gray-300">|</span>}>
            <Link to="/about" className="text-gray-600 hover:text-blue-600">О нас</Link>
            <Link to="/privacy" className="text-gray-600 hover:text-blue-600">Конфиденциальность</Link>
            <Link to="/terms" className="text-gray-600 hover:text-blue-600">Условия использования</Link>
          </Space>
        </Space>
      </Footer>
    </Layout>
  );
}

export default MainLayout;