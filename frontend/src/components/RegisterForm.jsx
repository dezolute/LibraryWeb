import '@ant-design/v5-patch-for-react-19';
import { Form, Input, Button, Typography, Card, Modal } from 'antd';
import { MailOutlined, LockOutlined, UserOutlined, UserAddOutlined } from '@ant-design/icons';
import { useNavigate, Link } from 'react-router-dom';
import { CONFIG } from '../constants/config';

const { Title, Text } = Typography;
const apiUrl = CONFIG.API_URL;

const RegisterForm = () => {
  const navigate = useNavigate();

  const onFinish = async (values) => {
    try {
      const response = await fetch(`${apiUrl}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      });

      const result = await response.json();
      console.log('Регистрация успешна:', result);
      navigate('/login');
    } catch (error) {
      Modal.error({
        title: 'Ошибка регистрации',
        content: error.message || 'Не удалось создать аккаунт.',
      });
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 80 }}>
      <Card
        bordered={false}
        style={{
          width: 440,
          padding: '32px 24px',
          borderRadius: 16,
          boxShadow: '0 4px 20px rgba(0,0,0,0.05)',
          background: 'linear-gradient(135deg, #ffffff 0%, #f0f2f5 100%)',
        }}
      >
        <Title level={3} style={{ textAlign: 'center', marginBottom: 30 }}>
          <UserAddOutlined style={{ marginRight: 8 }} />
          Регистрация
        </Title>

        <Form layout="vertical" onFinish={onFinish} requiredMark={false}>
          <Form.Item
            name="name"
            label="ФИО"
            rules={[{ required: true, message: 'Введите ФИО!' }]}
          >
            <Input
              prefix={<UserOutlined />}
              size="large"
              placeholder="Ваше ФИО"
              autoComplete="name"
            />
          </Form.Item>

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
              placeholder="Email"
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
            hasFeedback
          >
            <Input.Password
              prefix={<LockOutlined />}
              size="large"
              placeholder="Пароль"
              autoComplete="new-password"
            />
          </Form.Item>

          <Form.Item
            name="confirm_password"
            label="Подтвердите пароль"
            dependencies={['password']}
            rules={[
              { required: true, message: 'Подтвердите пароль!' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('Пароли не совпадают!'));
                },
              }),
              () => ({
                validator(_, value) {
                  if (!value || value.length >= 8) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('Пароль должен быть не менее 8 символов'));
                },
              }),
            ]}
            hasFeedback
          >
            <Input.Password
              prefix={<LockOutlined />}
              size="large"
              placeholder="Повторите пароль"
              autoComplete="new-password"
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 12 }}>
            <Button type="primary" size="large" block htmlType="submit">
              Зарегистрироваться
            </Button>
          </Form.Item>

          <Form.Item style={{ textAlign: 'center', marginBottom: 0 }}>
            <Text type="secondary">
              Уже есть аккаунт? <Link to="/login">Войдите</Link>
            </Text>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default RegisterForm;
