import '@ant-design/v5-patch-for-react-19';
import { Form, Input, Button, Typography, Card, Modal } from 'antd';
import { MailOutlined, LockOutlined, LoginOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { CONFIG } from '../constants/config';

const { Title, Text } = Typography;
const apiUrl = CONFIG.API_URL;

const LoginForm = () => {
  const navigate = useNavigate();

  const onFinish = async (values) => {
    try {
      const request = new URLSearchParams({
        grant_type: 'password',
        username: values.email,
        password: values.password,
        scope: '',
        client_id: 'string',
        client_secret: 'secret_key',
      });

      const response = await fetch(`${apiUrl}/auth`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: request.toString(),
      });

      const result = await response.json();

      if (!response.ok || !result.access_token) {
        throw new Error(result.detail || response.statusText);
      }

      localStorage.setItem('access_token', result.access_token);
      navigate('/account');
    } catch (error) {
      Modal.error({
        title: 'Ошибка входа',
        content: error.message || 'Не удалось авторизоваться.',
      });
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 80 }}>
      <Card
        bordered={false}
        style={{
          width: 420,
          padding: '32px 24px',
          borderRadius: 16,
          boxShadow: '0 4px 20px rgba(0,0,0,0.05)',
          background: 'linear-gradient(135deg, #ffffff 0%, #f0f2f5 100%)',
        }}
      >
        <Title level={3} style={{ textAlign: 'center', marginBottom: 30 }}>
          <LoginOutlined style={{ marginRight: 8 }} />
          Вход в систему
        </Title>

        <Form
          name="login"
          layout="vertical"
          onFinish={onFinish}
          requiredMark={false}
        >
          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: 'Введите email!' },
              { type: 'email', message: 'Некорректный формат email!' },
            ]}
          >
            <Input
              prefix={<MailOutlined />}
              size="large"
              placeholder="Введите email"
              autoComplete="email"
            />
          </Form.Item>

          <Form.Item
            name="password"
            label="Пароль"
            rules={[
              { required: true, message: 'Введите пароль!' },
              () => ({
                validator(_, value) {
                  if (!value || value.length >= 8) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('Пароль должен быть не менее 8 символов'));
                },
              }),
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              size="large"
              placeholder="Введите пароль"
              autoComplete="current-password"
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 12 }}>
            <Button type="primary" size="large" block htmlType="submit">
              Войти
            </Button>
          </Form.Item>

          <Form.Item style={{ textAlign: 'center', marginBottom: 0 }}>
            <Text type="secondary">
              Нет аккаунта? <Link to="/register">Зарегистрируйтесь</Link>
            </Text>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default LoginForm;