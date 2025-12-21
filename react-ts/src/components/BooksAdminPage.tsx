import { useEffect, useMemo, useState } from "react";
import {
  Button,
  Card,
  Form,
  Input,
  InputNumber,
  message,
  Modal,
  Popconfirm,
  Space,
  Table,
  Upload,
} from "antd";
import type { UploadProps } from "antd";
import { UploadOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import CONFIG from "./consts/config";

const API_BASE = CONFIG.API_URL;

type Book = {
  id: number;
  title: string;
  author: string;
  publisher: string;
  year_publication: number;
  cover_url?: string | null;
};

type BooksResponse = { items: Book[]; total: number };

type BookFormValues = Omit<Book, "id">;

function getToken() {
  return localStorage.getItem("access_token");
}

const authHeaders = (): Record<string, string> => {
  const token = localStorage.getItem("access_token");
  const h: Record<string, string> = {};
  if (token) h.Authorization = `Bearer ${token}`;
  return h;
};


async function parseOrText(resp: Response) {
  const text = await resp.text();
  try {
    return text ? JSON.parse(text) : null;
  } catch {
    return text;
  }
}

async function api<T>(url: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(url, init);
  if (resp.status === 401) throw new Error("UNAUTHORIZED");
  const data = await parseOrText(resp);
  if (!resp.ok) throw new Error((data as any)?.detail || (data as any)?.message || "Request failed");
  return data as T;
}

export default function BooksAdminPage() {
  const navigate = useNavigate();

  const [rows, setRows] = useState<Book[]>([]);
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false);

  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState<Book | null>(null);
  const [form] = Form.useForm<BookFormValues>();

  const ensureAuth = () => {
    const token = getToken();
    if (!token) {
      navigate("/");
      return false;
    }
    return true;
  };

  const load = async () => {
    if (!ensureAuth()) return;
    setLoading(true);
    try {
      const data = await api<BooksResponse>(`${API_BASE}/books`, { headers: authHeaders() });
      setRows(data.items);
      setTotal(data.total)
    } catch (e) {
      if (e instanceof Error && e.message === "UNAUTHORIZED") {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user_role");
        navigate("/");
        return;
      }
      message.error(e instanceof Error ? e.message : "Ошибка загрузки");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const openEdit = (b: Book) => {
    setEditing(b);
    form.setFieldsValue({
      title: b.title,
      author: b.author,
      publisher: b.publisher,
      year_publication: b.year_publication,
      cover_url: b.cover_url ?? null,
    });
    setModalOpen(true);
  };

  const submit = async () => {
    if (!ensureAuth()) return;
    const values = await form.validateFields();
    setSaving(true);
    try {
      if (editing) {
        await api(`${API_BASE}/books/${editing.id}`, {
          method: "PUT", // если у вас PATCH — замените на PATCH
          headers: { "Content-Type": "application/json", ...authHeaders() },
          body: JSON.stringify(values),
        });
        message.success("Книга обновлена");
      } else {
        await api(`${API_BASE}/books`, {
          method: "POST",
          headers: { "Content-Type": "application/json", ...authHeaders() },
          body: JSON.stringify(values),
        });
        message.success("Книга создана");
      }
      setModalOpen(false);
      await load();
    } catch (e) {
      message.error(e instanceof Error ? e.message : "Ошибка сохранения");
    } finally {
      setSaving(false);
    }
  };

  const remove = async (bookId: number) => {
    if (!ensureAuth()) return;
    try {
      await api(`${API_BASE}/books/${bookId}`, { method: "DELETE", headers: { ...authHeaders() } });
      message.success("Книга удалена");
      await load();
    } catch (e) {
      message.error(e instanceof Error ? e.message : "Ошибка удаления");
    }
  };

  // Обложка: PATCH /books/{book_id} (Set Book Cover)
  // ВАЖНО: тут предполагается multipart/form-data с полем "file". Если у вас другое поле/формат — скажите, подстрою.
  const coverUploadProps = (bookId: number): UploadProps => ({
    showUploadList: false,
    customRequest: async ({ file, onSuccess, onError }) => {
      try {
        if (!ensureAuth()) return;
        const fd = new FormData();
        fd.append("file", file as Blob);

        const resp = await fetch(`${API_BASE}/books/${bookId}`, {
          method: "PATCH",
          headers: { ...authHeaders() }, // Content-Type не ставим — браузер сам поставит boundary
          body: fd,
        });

        if (!resp.ok) {
          const data = await parseOrText(resp);
          throw new Error((data as any)?.detail || (data as any)?.message || "Не удалось обновить обложку");
        }

        message.success("Обложка обновлена");
        onSuccess?.({}, resp as any);
        await load();
      } catch (err) {
        message.error(err instanceof Error ? err.message : "Ошибка");
        onError?.(err as any);
      }
    },
  });

  const columns = useMemo(
    () => [
      { title: "ID", dataIndex: "id", key: "id", width: 80 },
      { title: "Название", dataIndex: "title", key: "title" },
      { title: "Автор", dataIndex: "author", key: "author" },
      { title: "Издательство", dataIndex: "publisher", key: "publisher" },
      { title: "Год", dataIndex: "year_publication", key: "year_publication", width: 110 },
      {
        title: "Действия",
        key: "actions",
        width: 420,
        render: (_: unknown, record: Book) => (
          <Space wrap>
            <Button onClick={() => openEdit(record)}>Изменить</Button>
            <Button onClick={() => navigate(`/employee/books/${record.id}/copies`)}>Копии</Button>
            <Upload {...coverUploadProps(record.id)}>
              <Button icon={<UploadOutlined />}>Обложка</Button>
            </Upload>
            <Popconfirm
              title="Удалить книгу?"
              description="Это действие нельзя отменить."
              okText="Удалить"
              cancelText="Отмена"
              onConfirm={() => remove(record.id)}
            >
              <Button danger>Удалить</Button>
            </Popconfirm>
          </Space>
        ),
      },
    ],
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  return (
    <div className="max-w-6xl mx-auto px-4">
      <Card
        title="Управление книгами"
        extra={<Button type="primary" onClick={() => navigate("/employee/books/add")}>Добавить книгу</Button>}
      >
        <Table<Book>
          rowKey="id"
          loading={loading}
          dataSource={rows}
          columns={columns as any}
          pagination={{ total, pageSize: 10 }}
        />
      </Card>

      <Modal
        title={editing ? "Редактирование книги" : "Добавление книги"}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={submit}
        confirmLoading={saving}
        okText="Сохранить"
        cancelText="Отмена"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="title" label="Название" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="author" label="Автор" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="publisher" label="Издательство" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="year_publication" label="Год публикации" rules={[{ required: true }]}>
            <InputNumber min={0} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="cover_url" label="Cover URL (если используете url)">
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
