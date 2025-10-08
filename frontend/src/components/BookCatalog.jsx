import { useEffect, useState } from 'react';
import { Card, Flex, Tag, Typography, Pagination, Spin, Button, Alert } from 'antd';
import { useNavigate } from 'react-router-dom';

const { Title } = Typography;

const priorityColor = {
  high: 'red',
  low: 'green',
};

const icon = 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fimg.freepik.com%2Fpremium-vector%2Fvector-illustration-for-the-cover-of-the-koran-with-arabic-calligraphy_700449-80.jpg%3Fw%3D2000&f=1&nofb=1&ipt=692a83ba91427161456ef53f22bd838527bb8339300cea444a2e81ab56f05929'

const BookCatalog = () => {
  const [books, setBooks] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [error, setError] = useState(null);
  const [limit] = useState(8);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate()


  const fetchBooks = async (page) => {
    setLoading(true);
    try {
      const offset = (page - 1) * limit
      const response = await fetch(`http://localhost/api/books?limit=${limit}&offset=${offset}&order_by=id`);
      const data = await response.json();
      setBooks(data.items);
      setTotal(data.total);
    } catch (error) {
      console.error('Ошибка загрузки книг:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBooks(page);
  }, [page]);

  const handlePageChange = (newPage) => {
    setPage(newPage);
  };

  const createRequest = async (book_id) => {
    
    const response = await fetch(`http://localhost/api/users/me/requests?book_id=${book_id}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    const body = response.json()
    console.log(body)
  }

  const goToBookPage = (book_id) => {
    navigate(`/book/${book_id}`)
  }

  if (loading) return <Spin tip='Загрузка книг' />
  if (error) return <Alert type='error' message='Ошибка загрузки' description={error} />

  return (
    <div>
      <>
        <Title level={2} style={{ textAlign: 'center'}}>Каталог книг</Title>
        <Flex wrap gap='large' justify='space-evenly'>
          {books.map((book) => (
            <Card
              hoverable
              title={book.title}
              onClick={() => goToBookPage(book.id)}
              key={book.id}
            >
              <Flex gap='large'>
                <Flex vertical gap={50}>
                  <Flex vertical gap={15} style={{ fontSize: 16 }}>
                    <span><strong>Автор:</strong> {book.author}</span>
                    <span><strong>Год издания:</strong> {book.year_publication}</span>
                    <span><strong>В наличии:</strong> {book.count}</span>
                    <span><strong>Приоритет</strong> <Tag style={{ padding: 1 fontSize: 14 }} color={priorityColor[book.priority]}>{book.priority}</Tag></span>
                  </Flex>
                  <div>
                    <Button 
                      type='primary'
                      key={book.id}
                      onClick={() => createRequest(book.id)}
                      style={{ alignSelf: 'end', marginRight: 5}}>
                        Забронировать
                    </Button>
                  </div>
                </Flex>
                <img style={{
                  width: 150,
                  height: 200,
                  margin: 0,
                  float: 'left',
                }}
                loading='lazy'
                src={icon}></img>
              </Flex>
            </Card>
          ))}
        </Flex>
        <Pagination
          current={page}
          pageSize={limit}
          showQuickJumper
          hideOnSinglePage
          showSizeChanger={false}
          total={total}
          onChange={handlePageChange}
          style={{ marginTop: '30px', textAlign: 'center', display: 'block', alignSelf: 'center' }}
        />
      </>
    </div>
  );
};

export default BookCatalog;
