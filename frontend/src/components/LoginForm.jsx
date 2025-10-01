import { Form, Input, Button, Checkbox, Typography, Card } from 'antd';
import { MailOutlined, LockOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';

const { Title } = Typography;

const LoginForm = () => {
  const navigate = useNavigate();
  const onFinish = async (values) => {
    try {
      const request = `grant_type=password&username=${values.email}&password=${values.password}&scope=&client_id=string&client_secret=secret_key`
      
      const response = await fetch('/api/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: request,
      });

      const result = await response.json();
      localStorage.setItem('access_token', result['access_token'])
      navigate('/account')
    } catch (error) {
      alert('Ошибка при отправке:', error.message);
    }
  };

  return (
      <Card style={{ width: 400 }}>
        <Title level={3} style={{ textAlign: 'center' }}>Вход</Title>
        <Form
          name="login"
          initialValues={{ remember: true }}
          onFinish={onFinish}
          layout="vertical"
        >
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
          >
            <Input.Password prefix={<LockOutlined />} size='large' placeholder="Пароль" />
          </Form.Item>

          <Form.Item style={{ marginBottom: 5, textAlign: 'center' }}>
            <Button type="primary" size='large' htmlType="submit">
              Войти
            </Button>
          </Form.Item>
          <Form.Item style={{ textAlign: 'center' }}>
            Нет аккаунта? <Link to="/register">Зарегистрируйтесь</Link>
          </Form.Item>
        </Form>
      </Card>
  );
};

export default LoginForm;