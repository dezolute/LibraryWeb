import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Card, Tag, Spin, Typography, Alert } from 'antd';
import { CONFIG } from '../constants/config'

const { Title } = Typography;
const apiUrl = CONFIG.API_URL

const icon = 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fimg.freepik.com%2Fpremium-vector%2Fvector-illustration-for-the-cover-of-the-koran-with-arabic-calligraphy_700449-80.jpg%3Fw%3D2000&f=1&nofb=1&ipt=692a83ba91427161456ef53f22bd838527bb8339300cea444a2e81ab56f05929'

const priorityColor = {
  low: 'green',
  high: 'red',
};

const BookPage = () => {
  const { id } = useParams();
  const [book, setBook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchBook = async () => {
      try {
        const response = await fetch(`${apiUrl}/books/${id}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`Ошибка: ${response.status}`);
        }

        const result = await response.json();
        setBook(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchBook();
  }, [id]);

  if (loading) return <Spin tip="Загрузка книги..." />;
  if (error) return <Alert type="error" message="Ошибка загрузки" description={error} />;

  return (
    <Card
      title={<Title level={2}>{book.title}</Title>}
      style={{
        width: '600px',
        margin: '40px auto',
        padding: '32px',
        boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
        borderRadius: '12px',
        backgroundColor: '#fafafa',
        fontSize: '24px',
        textAlign: 'center' 
      }}
    >
      <div style={{float: 'left', textAlign: 'left'}}>
        <p><strong>Автор:</strong> {book.author}</p>
        <p><strong>Год издания:</strong> {book.year_publication}</p>
        <p><strong>Количество:</strong> {book.count}</p>
        <p><strong>Приоритет:</strong> <Tag style={{fontSize: 24, padding: 10}} color={priorityColor[book.priority]}>{book.priority}</Tag></p>
      </div>
      <img src={icon} style={{float: 'right', width: 200}} />
    </Card>
  );
};

export default BookPage;