import { Layout, Menu, Button, Space, theme, Drawer, Grid } from "antd";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useMemo, useState } from "react";
import {
  UserOutlined,
  LoginOutlined,
  LogoutOutlined,
  MenuOutlined,
  BookTwoTone,
  HomeTwoTone,
  ProfileTwoTone,
  ContainerTwoTone,
  ScheduleTwoTone,
} from "@ant-design/icons";
import { AuthModal } from "../auth/AuthModal";

const { Header, Content, Footer } = Layout;
const { useBreakpoint } = Grid;

type Props = { children: React.ReactNode };

const MainLayout = ({ children }: Props) => {
  const navigate = useNavigate();
  const location = useLocation();
  const screens = useBreakpoint();

  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const isAuthenticated = !!localStorage.getItem("access_token");
  const userRole = localStorage.getItem("user_role");
  const isEmployee = userRole === "EMPLOYEE" || userRole === "ADMIN";

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_role");
    navigate("/");
  };

  const isMobile = !screens.md; // xs/sm -> mobile, md+ -> desktop [web:112]

  const menuItems = useMemo(
    () => [
      { key: "/", icon: <HomeTwoTone />, label: <Link to="/">Главная</Link> },
      { key: "/catalog", icon: <ContainerTwoTone />, label: <Link to="/catalog">Каталог</Link> },
      ...(isEmployee
        ? [
            {
              key: "/employee/books/",
              icon: <BookTwoTone />,
              label: <Link to="/employee/books/">Книги</Link>,
            },
            {
              key: "/employee/requests",
              icon: <ProfileTwoTone />,
              label: <Link to="/employee/requests">Заявки</Link>,
            },
            { 
              key: "/employee/loans",
              icon: <ScheduleTwoTone />,
              label: <Link to="/employee/loans">Выданные книги</Link>
            },
          ]
        : []),
    ],
    [isEmployee]
  );

  return (
    <Layout className="min-h-screen flex flex-col">
      <Header className="flex items-center justify-between px-4 md:px-6 bg-white h-16 fixed w-full z-10 shadow-sm">
        {/* Left */}
        <div className="flex items-center min-w-0">
          <Link to="/" className="flex items-center shrink-0">
            <img src="/LibraryWeb.svg" className="w-10 h-10" alt="LibraryWeb Logo" />
            {/* на мобилке можно скрыть текст, чтобы не ломал хедер */}
            <span className="hidden sm:inline text-2xl font-semibold text-blue-600 ml-2">
              LibraryWeb
            </span>
          </Link>

          {/* Desktop menu */}
          {!isMobile && (
            <Menu
              mode="horizontal"
              selectedKeys={[location.pathname]}
              items={menuItems}
              className="ml-6"
              style={{ minWidth: 0, flex: "auto" }} // чтобы ужималось во flex [web:133]
            />
          )}
        </div>

        {/* Right */}
        <Space>
          {/* Mobile burger */}
          {isMobile && (
            <Button
              icon={<MenuOutlined />}
              onClick={() => setMobileMenuOpen(true)}
              aria-label="Open menu"
            />
          )}

          {isAuthenticated ? (
            <>
              <Button icon={<UserOutlined />} onClick={() => navigate("/account")}>
                {!isMobile ? "Мой аккаунт" : null}
              </Button>
              <Button icon={<LogoutOutlined />} onClick={handleLogout}>
                {!isMobile ? "Выйти" : null}
              </Button>
            </>
          ) : (
            <Button
              type="primary"
              icon={<LoginOutlined />}
              onClick={() => setIsAuthModalOpen(true)}
            >
              {!isMobile ? "Войти" : null}
            </Button>
          )}
        </Space>

        <AuthModal open={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)} />
      </Header>

      {/* Mobile Drawer menu */}
      <Drawer
        title="Меню"
        placement="left"
        open={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
        bodyStyle={{ padding: 0 }}
      >
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={() => setMobileMenuOpen(false)}
        />
      </Drawer>

      <Content className="flex-grow mt-16 p-3 sm:p-4 md:p-6">
        <div
          style={{
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
            padding: isMobile ? 12 : 24,
            minHeight: "calc(100vh - 16rem)",
          }}
          className="w-full max-w-7xl mx-auto"
        >
          {children}
        </div>
      </Content>

      <Footer className="text-center mt-auto py-6 bg-white">
        <Space direction="vertical" size="small">
          <div className="text-gray-600">© 2025 LibraryWeb. Все права защищены.</div>
          <Space wrap split={<span className="text-gray-300">|</span>}>
            <Link to="/about" className="text-gray-600 hover:text-blue-600">О нас</Link>
            <Link to="/privacy" className="text-gray-600 hover:text-blue-600">Конфиденциальность</Link>
            <Link to="/terms" className="text-gray-600 hover:text-blue-600">Условия использования</Link>
          </Space>
        </Space>
      </Footer>
    </Layout>
  );
};

export default MainLayout;