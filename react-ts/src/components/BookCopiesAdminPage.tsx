import { useEffect, useMemo, useState } from "react";
import { Button, Card, Form, Input, message, Modal, Select, Space, Table, Tag } from "antd";
import { useNavigate, useParams } from "react-router-dom";
import CONFIG from "./consts/config";

const API_BASE = CONFIG.API_URL;

type Copy = { serial_num: string; status: string; access_type: string };
type Book = { id: number; title: string; author: string; publisher: string; year_publication: number; copies: Copy[] };

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

export default function BookCopiesAdminPage() {
  const { id } = useParams();
  const bookId = Number(id);
  const navigate = useNavigate();

  const [book, setBook] = useState<Book | null>(null);
  const [loading, setLoading] = useState(false);

  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form] = Form.useForm<{ serials: string, access_type: string }>();

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
      const data = await api<Book>(`${API_BASE}/books/${bookId}`, { headers: { ...authHeaders() } });
      setBook(data);
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
    if (!Number.isFinite(bookId)) return;
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [bookId]);

  const addCopies = async () => {
    if (!ensureAuth()) return;

    const { serials, access_type } = await form.validateFields();

    const list = serials
      .split("\n")
      .map((s: string) => s.trim())
      .filter(Boolean);

    if (list.length === 0) {
      message.warning("Добавьте хотя бы один serial_num");
      return;
    }

    const payload = list.map((serial_num: string) => ({
      serial_num,
      access_type, // "READING_ROOM" | "TAKE_HOME"
    }));

    setSaving(true);
    try {
      await api(`${API_BASE}/books/${bookId}/copies`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...authHeaders(),
        },
        body: JSON.stringify(payload), // ✅ массив объектов
      });

      message.success("Копии добавлены");
      setModalOpen(false);
      form.resetFields();
      await load();
    } catch (e) {
      message.error(e instanceof Error ? e.message : "Ошибка добавления копий");
    } finally {
      setSaving(false);
    }
  };

  const columns = useMemo(
    () => [
      { title: "Serial", dataIndex: "serial_num", key: "serial_num" },
      {
        title: "Статус",
        dataIndex: "status",
        key: "status",
        render: (s: string) => {
          const color = s === "AVAILABLE" ? "green" : s === "RESERVED" ? "orange" : "red";
          return <Tag color={color}>{s}</Tag>;
        },
      },
      { title: "Доступ", dataIndex: "access_type", key: "access_type", render: (a: string) => <Tag>{a}</Tag> },
    ],
    []
  );

  return (
    <div className="max-w-6xl mx-auto px-4">
      <Card
        title={book ? `Копии: ${book.title}` : "Копии книги"}
        extra={
          <Space>
            <Button onClick={() => navigate("/employee/books")}>Назад к книгам</Button>
            <Button type="primary" onClick={() => setModalOpen(true)}>Добавить копии</Button>
          </Space>
        }
        loading={loading}
      >
        <Table<Copy>
          rowKey="serial_num"
          dataSource={book?.copies || []}
          columns={columns as any}
          pagination={false}
        />
      </Card>

      <Modal
        title="Добавить копии"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={addCopies}
        confirmLoading={saving}
        okText="Добавить"
        cancelText="Отмена"
      >
        <Form form={form} layout="vertical" initialValues={{ access_type: "READING_ROOM" }}>
          <Form.Item
            name="serials"
            label="Serial номера (по одному в строке)"
            rules={[{ required: true, message: "Введите хотя бы один serial_num" }]}
          >
            <Input.TextArea rows={6} placeholder={"001-01\n001-02\n001-03"} />
          </Form.Item>

          <Form.Item
            name="access_type"
            label="Тип доступа"
            rules={[{ required: true }]}
          >
            <Select
              options={[
                { value: "READING_ROOM", label: "Только читальный зал" },
                { value: "TAKE_HOME", label: "Можно домой" },
              ]}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
