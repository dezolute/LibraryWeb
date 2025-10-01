import React, { useEffect, useState } from 'react';
import { Card, Col, Row, Tag, Typography, Pagination, Spin } from 'antd';

const { Title } = Typography;

const url = 'http://localhost'

const priorityColor = {
  HIGH: 'red',
  MEDIUM: 'orange',
  LOW: 'green',
};

const BookCatalog = () => {
  const [books, setBooks] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(9);
  const [loading, setLoading] = useState(true);

  const fetchBooks = async (page) => {
    setLoading(true);
    try {
      const offset = (page - 1) * limit
      const response = await fetch(`${url}/api/books?limit=${limit}&offset=${offset}`);
      const data = await response.json();
      setBooks(data.items);       // предполагается, что API возвращает { items: [...], total: number }
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

  return (
    <div>
      <Title level={2} style={{ textAlign: 'center'}}>Каталог книг</Title>
      {loading ? (
        <Spin />
      ) : (
        <>
          <Row gutter={[16, 16]} style={{ margin: 100, marginTop: 50, marginBottom: 50 }}>
            {books.map((book) => (
              <Col xs={24} sm={12} md={8} key={book.id}>
                <Card
                  title={book.title}
                  style={{
                    height: 250,
                    width: 400,
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                  }}
                >
                  <div>
                    <p><strong>Автор:</strong> {book.author}</p>
                    <p><strong>Год издания:</strong> {book.year_publication}</p>
                    <p><strong>В наличии:</strong> {book.count}</p>
                  </div>
                  <Tag color={priorityColor[book.prioryti]}>{book.prioryti}</Tag>
                </Card>
              </Col>
            ))}
          </Row>
          <Pagination
            current={page}
            pageSize={limit}
            total={total}
            onChange={handlePageChange}
            style={{ marginTop: '30px', textAlign: 'center', display: 'block', alignSelf: 'center' }}
          />
        </>
      )}
    </div>
  );
};

export default BookCatalog;
