import { useState } from 'react';
import { Modal, Tabs, Form, Input, Button, message } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, UserAddOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import CONFIG from '../consts/config';

interface AuthModalProps {
  open: boolean;
  onClose: () => void;
}

interface LoginForm {
  email: string;
  password: string;
}

interface RegisterForm extends LoginForm {
  name: string;
  passwordConfirm: string;
}

export const AuthModal = ({ open, onClose }: AuthModalProps) => {
  const [activeTab, setActiveTab] = useState<'login' | 'register'>('login');
  const [loginForm] = Form.useForm<LoginForm>();
  const [registerForm] = Form.useForm<RegisterForm>();
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const API_BASE = CONFIG.API_URL;

  const parseResponseBody = async (resp: Response) => {
    const contentType = resp.headers.get('content-type') || '';
    const text = await resp.text();
    if (contentType.includes('application/json')) {
      try {
        return JSON.parse(text);
      } catch {
        return text;
      }
    }
    try {
      return JSON.parse(text);
    } catch {
      return text;
    }
  };

  const handleLogin = async (values: LoginForm) => {
    setLoading(true);
    try {
      // Backend expects OAuth2 form-urlencoded with fields: username, password
      const params = new URLSearchParams();
      params.append('username', values.email);
      params.append('password', values.password);

      const response = await fetch(`${API_BASE}/auth`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: params.toString(),
      });

      if (!response.ok) {
        // Try to read error message from backend
        let errText = 'Неверный email или пароль';
        try {
          const e = await parseResponseBody(response);
          if (e && typeof e === 'object' && 'detail' in e) errText = (e as { detail?: string }).detail || errText;
          else if (typeof e === 'string' && e.trim()) errText = e;
        } catch {
          // ignore
        }
        throw new Error(errText);
      }

      const data = await parseResponseBody(response);
      const accessToken = data.access_token || data.accessToken || '';
      if (!accessToken) throw new Error('Не удалось получить токен');

      localStorage.setItem('access_token', accessToken);

      // Получаем профиль текущего пользователя, чтобы узнать роль
      try {
        const meResp = await fetch(`${API_BASE}/readers/me`, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });
        if (meResp.ok) {
          const me = await parseResponseBody(meResp);
          if (me && typeof me === 'object' && 'role' in me) {
            localStorage.setItem('user_role', (me as { role?: string }).role || 'READER');
          }
        }
      } catch {
        // Игнорируем ошибку получения роли — всё равно вошли
      }

      message.success('Добро пожаловать!');
      onClose();
      navigate('/account');
    } catch (error) {
      message.error(error instanceof Error ? error.message : 'Ошибка входа');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (values: RegisterForm) => {
    if (values.password !== values.passwordConfirm) {
      message.error('Пароли не совпадают');
      return;
    }

    setLoading(true);
    try {
      // Backend expects ReaderCreateDTO: full_name, email, password, confirm_password
      const body = {
        full_name: values.name,
        email: values.email,
        password: values.password,
        confirm_password: values.passwordConfirm,
      };

      const response = await fetch(`${API_BASE}/readers`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        let errText = 'Ошибка при регистрации';
        try {
          const e = await parseResponseBody(response);
          if (e && typeof e === 'object' && 'detail' in e) errText = (e as { detail?: string }).detail || errText;
          else if (typeof e === 'string' && e.trim()) errText = e;
        } catch {
          // ignore
        }
        throw new Error(errText);
      }

      message.success('Регистрация успешна! Теперь вы можете войти');
      setActiveTab('login');
      registerForm.resetFields();
    } catch (error) {
      message.error(error instanceof Error ? error.message : 'Ошибка регистрации');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    loginForm.resetFields();
    registerForm.resetFields();
    onClose();
  };

  const items = [
    {
      key: 'login',
      label: 'Вход',
      children: (
        <Form
          form={loginForm}
          name="login"
          onFinish={handleLogin}
          layout="vertical"
          size="large"
        >
          <Form.Item
            name="email"
            rules={[
              { required: true, message: 'Введите email' },
              { type: 'email', message: 'Введите корректный email' }
            ]}
          >
            <Input prefix={<MailOutlined />} placeholder="Email" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: 'Введите пароль' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="Пароль" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              Войти
            </Button>
          </Form.Item>
        </Form>
      ),
    },
    {
      key: 'register',
      label: 'Регистрация',
      children: (
        <Form
          form={registerForm}
          name="register"
          onFinish={handleRegister}
          layout="vertical"
          size="large"
        >
          <Form.Item
            name="name"
            rules={[{ required: true, message: 'Введите ваше имя' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="Имя" />
          </Form.Item>

          <Form.Item
            name="email"
            rules={[
              { required: true, message: 'Введите email' },
              { type: 'email', message: 'Введите корректный email' }
            ]}
          >
            <Input prefix={<MailOutlined />} placeholder="Email" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: 'Введите пароль' },
              { min: 6, message: 'Пароль должен быть не менее 6 символов' }
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="Пароль" />
          </Form.Item>

          <Form.Item
            name="passwordConfirm"
            dependencies={['password']}
            rules={[
              { required: true, message: 'Подтвердите пароль' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('Пароли не совпадают'));
                },
              }),
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="Подтвердите пароль" />
          </Form.Item>

          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading}
              icon={<UserAddOutlined />}
              block
            >
              Зарегистрироваться
            </Button>
          </Form.Item>
        </Form>
      ),
    },
  ];

  return (
    <Modal
      open={open}
      onCancel={handleCancel}
      footer={null}
      width={400}
      title="Авторизация"
      centered
    >
      <Tabs
        activeKey={activeTab}
        onChange={(key) => setActiveTab(key as 'login' | 'register')}
        items={items}
        centered
        className="auth-tabs"
      />
    </Modal>
  );
};