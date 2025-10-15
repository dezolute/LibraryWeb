import { Result, Button } from 'antd';
import { useNavigate } from 'react-router-dom';

const UnauthorizedPage = () => {
  const navigate = useNavigate();

  return (
    <Result
      status="403"
      title="Доступ запрещён"
      subTitle="У вас нет прав для просмотра этой страницы"
      extra={
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
          <Button type="primary" onClick={() => navigate('/')}>
            На главную
          </Button>
        </div>
      }
    />
  );
};

export default UnauthorizedPage;