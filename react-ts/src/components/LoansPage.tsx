import { useEffect, useMemo, useState } from 'react';
import { Table, Button, DatePicker, Input, Spin, Alert, message, Empty } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import dayjs, { Dayjs } from 'dayjs';

const { RangePicker } = DatePicker;

interface Book {
  id: number;
  title: string;
  author: string;
  publisher: string;
  year_publication: number;
}

interface BookCopy {
  serial_num: string;
  book: Book;
}

interface Reader {
  id: number;
  email: string;
  role: string;
  verified: boolean;
  profile?: {
    full_name: string;
  };
}

type Loan = {
  id: number;
  reader_id: number;
  copy_id: string;
  issue_date: string; // ISO
  due_date: string; // ISO
  return_date?: string | null; // ISO | null
  book_copy?: BookCopy;
  reader?: Reader;
  // Для обратной совместимости
  serial_num?: string;
  book_title?: string;
  reader_name?: string;
  issued_at?: string;
  due_at?: string;
  returned_at?: string | null;
};

const API_BASE = 'http://127.0.0.1:8000/api';

const LoansPage = () => {
  const [loans, setLoans] = useState<Loan[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [total, setTotal] = useState(0);
  const [book, setBook] = useState('');
  const [reader, setReader] = useState('');
  const [dateRange, setDateRange] = useState<Dayjs[] | null>(null);
  const token = localStorage.getItem('access_token');

  const fetchLoans = async (currentPage = 1, currentPageSize = 10) => {
    setLoading(true);
    setError(null);
    try {
      const offset = (currentPage - 1) * currentPageSize;
      const params = new URLSearchParams();
      params.set('limit', String(currentPageSize));
      params.set('offset', String(offset));
      if (book) params.set('book', book);
      if (reader) params.set('reader', reader)
      if (dateRange) {
        params.set('at', dateRange[0].toISOString());
        params.set('to', dateRange[1].toISOString())
      }

      const resp = await fetch(`${API_BASE}/loans?${params.toString()}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!resp.ok) throw new Error('Не удалось получить список займов');
      const contentType = resp.headers.get('content-type') || '';
      const text = await resp.text();
      let data: unknown;
      if (contentType.includes('application/json')) {
        try { data = JSON.parse(text); } catch { data = text; }
      } else {
        try { data = JSON.parse(text); } catch { data = text; }
      }
      const parsed = data as { items?: Loan[]; total?: number };
      setLoans(parsed.items || []);
      setTotal(typeof parsed.total === 'number' ? parsed.total : (parsed.items || []).length);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLoans(page, pageSize);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, pageSize]);

  const columns: ColumnsType<Loan> = useMemo(() => [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 80,
    },
    {
      title: 'Серийный номер',
      key: 'serial_num',
      ellipsis: true,
      render: (_: unknown, record: Loan) => {
        const serial_num = record.book_copy?.serial_num || record.book_title || '—';
        return serial_num;
      },
    },
    {
      title: 'Книга',
      key: 'book',
      ellipsis: true,
      render: (_: unknown, record: Loan) => {
        const title = record.book_copy?.book?.title || record.book_title || '—';
        return title;
      },
    },
    {
      title: 'Читатель',
      key: 'reader',
      ellipsis: true,
      render: (_: unknown, record: Loan) => {
        const name = record.reader?.profile?.full_name || record.reader_name || record.reader?.email?.split('@')[0] || '—';
        return name;
      },
    },
    {
      title: 'Выдан',
      key: 'issue_date',
      render: (_: unknown, record: Loan) => {
        const date = record.issue_date || record.issued_at;
        return date ? dayjs(date).format('DD.MM.YYYY') : '—';
      },
      width: 120,
    },
    {
      title: 'Срок до',
      key: 'due_date',
      render: (_: unknown, record: Loan) => {
        const date = record.due_date || record.due_at;
        return date ? dayjs(date).format('DD.MM.YYYY') : '—';
      },
      width: 120,
    },
    {
      title: 'Возврат',
      key: 'return_date',
      render: (_: unknown, record: Loan) => {
        const date = record.return_date || record.returned_at;
        return date ? dayjs(date).format('DD.MM.YYYY') : '—';
      },
      width: 120,
    },
  ], []);

  const handleSearch = () => {
    setPage(1);
    fetchLoans(1, pageSize);
  };

  const downloadOverdueReport = async () => {
    try {
      const resp = await fetch(`${API_BASE}/loans/overdue/report`, {
        headers: { 
          Authorization: `Bearer ${token}`,
        },
      });
      if (!resp.ok) {
        const text = await resp.text();
        throw new Error(text || 'Не удалось получить отчет');
      }
      const blob = await resp.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const disposition = resp.headers.get('content-disposition') || '';
      const match = /filename="?([^";]+)"?/i.exec(disposition);
      a.download = match?.[1] || `${dayjs().format('DD.MM.YYYY')}_Задолженности.docx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      message.success('Отчет загружен');
    } catch (e) {
      message.error(e instanceof Error ? e.message : 'Ошибка загрузки отчета');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold">Займы</h2>
        <Button type="primary" onClick={downloadOverdueReport}>Отчет по просроченным</Button>
      </div>

      <div className="flex flex-wrap gap-3 mb-4">
        <Input
          placeholder="Книга"
          value={book}
          onChange={(e) => setBook(e.target.value)}
          style={{ width: 240 }}
          allowClear
        />
        <Input
          placeholder="Читатель"
          value={reader}
          onChange={(e) => setReader(e.target.value)}
          style={{ width: 240 }}
          allowClear
        />
        <RangePicker value={dateRange as any} onChange={(v) => setDateRange(v as any)} />
        <Button onClick={handleSearch} type="default">Фильтровать</Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-16"><Spin /></div>
      ) : error ? (
        <Alert type="error" message="Ошибка" description={error} />
      ) : loans.length === 0 ? (
        <div className="py-16"><Empty description="Займов не найдено" /></div>
      ) : (
        <Table
          rowKey="id"
          columns={columns}
          dataSource={loans}
          pagination={{
            current: page,
            pageSize,
            total,
            showSizeChanger: true,
            onChange: (p, ps) => { setPage(p); setPageSize(ps); },
          }}
        />
      )}
    </div>
  );
};

export default LoansPage;


