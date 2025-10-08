import { Form, Input, Button, Typography, Card } from 'antd';
import { MailOutlined, LockOutlined, UserOutlined } from '@ant-design/icons';
import { useNavigate, Link } from 'react-router-dom';

const { Title } = Typography;

const RegisterForm = () => {
  const navigate = useNavigate()
  const onFinish = async (values) => {
    try {
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      });

      const result = await response.json();
      console.log('Регистрация успешна:', result);
      navigate('/login')
    } catch (error) {
      alert('Ошибка регистрации:', error.message);
    }
  };

  return (
      <Card style={{ width: 400 }}>
        <Title level={3} style={{ textAlign: 'center', marginTop: 10 }}>Регистрация</Title>
        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item
            name="name"
            label="Имя"
            rules={[{ required: true, message: 'Введите имя!' }]}
          >
            <Input prefix={<UserOutlined />} size='large' placeholder="Ваше имя" />
          </Form.Item>

          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: 'Введите email!' },
              { type: 'email', message: 'Некорректный формат email!' },
            ]}
          >
            <Input prefix={<MailOutlined />} size='large' placeholder="Email" />
          </Form.Item>

          <Form.Item
            name="password"
            label="Пароль"
            rules={[
              { required: true, message: 'Введите пароль!' },
              () => ({
                validator(_, value) {
                  if (value.length >= 8) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('Не менее 8 символов!'))
                }
              })
            ]}
            hasFeedback
          >
            <Input.Password prefix={<LockOutlined />} size='large' placeholder="Пароль" />
          </Form.Item>

          <Form.Item
            name="confirm_password"
            label="Подтвердите пароль"
            dependencies={['password']}
            hasFeedback
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
                  if (value.length >= 8) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('Не менее 8 символов!'))
                }
              })
            ]}
          >
            <Input.Password placeholder="Повторите пароль" />
          </Form.Item>

          <Form.Item style={{ textAlign: 'center', marginBottom: 5}}>
            <Button type="primary" size='large' htmlType="submit">
              Зарегистрироваться
            </Button>
          </Form.Item>
          <Form.Item style={{ textAlign: 'center' }}>
            Есть аккаунт? <Link to="/login">Войдите</Link>
          </Form.Item>
        </Form>
      </Card>
  );
};

export default RegisterForm;
