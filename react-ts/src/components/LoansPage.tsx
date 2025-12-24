import { useEffect, useMemo, useState } from 'react';
import { Table, Button, DatePicker, Input, Spin, Alert, message, Empty } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import dayjs, { Dayjs } from 'dayjs';
import { useNavigate } from 'react-router-dom';
import CONFIG from './consts/config';

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
  id: number
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

const API_BASE = CONFIG.API_URL;

const LoansPage = () => {
  const [loans, setLoans] = useState<Loan[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // теперь это только UI-пагинация
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const [book, setBook] = useState('');
  const [reader, setReader] = useState('');
  const [dateRange, setDateRange] = useState<Dayjs[] | null>(null);

  const navigate = useNavigate();
  const token = localStorage.getItem('access_token');

  // 1) Загружаем ВСЕ займы (или достаточно большой лимит)
  const fetchLoans = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      // Если API требует limit/offset, можно временно поставить большой limit:
      params.set('limit', '10000');
      params.set('offset', '0');

      const resp = await fetch(`${API_BASE}/loans?${params.toString()}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!resp.ok) throw new Error('Не удалось получить список займов');

      const contentType = resp.headers.get('content-type') || '';
      const text = await resp.text();
      const data = contentType.includes('application/json') ? JSON.parse(text) : JSON.parse(text);

      const parsed = data as { items?: Loan[] };
      setLoans(parsed.items || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  // загружаем один раз
  useEffect(() => {
    fetchLoans();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 2) Фильтрация на фронте (useMemo, чтобы не пересчитывать зря) [web:15]
  const filteredLoans = useMemo(() => {
    const bookQ = book.trim().toLowerCase();
    const readerQ = reader.trim().toLowerCase();

    const from = dateRange?.[0]?.startOf('day') ?? null;
    const to = dateRange?.[1]?.endOf('day') ?? null;

    return loans.filter((l) => {
      const title = (l.book_copy?.book?.title || l.book_title || '').toLowerCase();
      const serial = (l.book_copy?.serial_num || l.serial_num || '').toLowerCase();

      const readerName = (l.reader?.profile?.full_name || l.reader_name || '').toLowerCase();
      const readerEmail = (l.reader?.email || '').toLowerCase();

      // по книге ищем и по названию, и по серийному (если нужно)
      if (bookQ) {
        const okBook = title.includes(bookQ) || serial.includes(bookQ);
        if (!okBook) return false;
      }

      // по читателю ищем по имени и email
      if (readerQ) {
        const okReader = readerName.includes(readerQ) || readerEmail.includes(readerQ);
        if (!okReader) return false;
      }

      // фильтр по датам: обычно логично фильтровать по issue_date (выдан)
      const issueIso = l.issue_date || l.issued_at;
      if (from || to) {
        if (!issueIso) return false;
        const d = dayjs(issueIso);
        if (from && d.isBefore(from)) return false;
        if (to && d.isAfter(to)) return false;
      }

      return true;
    });
  }, [loans, book, reader, dateRange]);

  // 3) Клиентская пагинация: режем отфильтрованный массив
  const pagedLoans = useMemo(() => {
    const start = (page - 1) * pageSize;
    return filteredLoans.slice(start, start + pageSize);
  }, [filteredLoans, page, pageSize]);

  // если фильтры изменились — сброс страницы (чтобы не попасть на пустую) [web:10]
  useEffect(() => {
    setPage(1);
  }, [book, reader, dateRange]);

  const handleAction = async (loanId: number) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        navigate('/');
        return;
      }

      const resp = await fetch(`${API_BASE}/loans/${loanId}`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!resp.ok) throw new Error('Не удалось обработать запрос');

      message.success('Книга возвращенна');
      // обновляем список, чтобы статусы/return_date подтянулись
      fetchLoans();
    } catch (e) {
      message.error(e instanceof Error ? e.message : 'Неизвестная ошибка');
    }
  };

  const columns: ColumnsType<Loan> = useMemo(() => [
    {
      title: 'Читатель',
      key: 'reader',
      ellipsis: true,
      render: (_: unknown, record: Loan) => {
        const email = record.reader?.email || '—';
        const name = record.reader?.profile?.full_name || record.reader_name || '—';
        return (
          <div>
            <div>{name}</div>
            <div className="text-sm text-gray-500">{email}</div>
          </div>
        );
      },
    },
    {
      title: 'Серийный номер',
      key: 'serial_num',
      ellipsis: true,
      render: (_: unknown, record: Loan) => {
        const title = record.book_copy?.book?.title || record.book_title || '—';
        const serialNum = record.book_copy?.serial_num || record.serial_num || '—'; // <- фикс: было book_title
        return (
          <div>
            <div>{serialNum}</div>
            <div className="text-sm text-gray-500">{title}</div>
          </div>
        );
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
    {
      title: 'Действия',
      key: 'actions',
      render: (_: unknown, record: Loan) => (
        record.return_date === null && (
          <Button type="primary" size="small" onClick={() => handleAction(record.id)}>
            Забрать кнгиу
          </Button>
        )
      ),
    },
  ], []);

  // кнопка "Фильтровать" больше не обязана делать fetch — можно оставить просто сброс page
  const handleSearch = () => setPage(1);

  const downloadOverdueReport = async () => {
    try {
      const resp = await fetch(`${API_BASE}/loans/overdue/report`, {
        headers: { Authorization: `Bearer ${token}` },
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
        <h2 className="text-2xl font-semibold">Выданные книги</h2>
        <Button type="primary" onClick={downloadOverdueReport}>Отчет по проссроченым долгам</Button>
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
        <Button onClick={fetchLoans} type="default">Обновить</Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-16"><Spin /></div>
      ) : error ? (
        <Alert type="error" message="Ошибка" description={error} />
      ) : filteredLoans.length === 0 ? (
        <div className="py-16"><Empty description="Займов не найдено" /></div>
      ) : (
        <Table
          rowKey="id"
          columns={columns}
          dataSource={pagedLoans}
          pagination={{
            current: page,
            pageSize,
            total: filteredLoans.length,
            showSizeChanger: true,
            onChange: (p, ps) => {
              setPage(p);
              setPageSize(ps);
            },
          }}
        />
      )}
    </div>
  );
};

export default LoansPage;