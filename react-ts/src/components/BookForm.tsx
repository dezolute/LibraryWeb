import { useState } from 'react';
import { Form, Input, InputNumber, Button, Select, Space, message, Upload } from 'antd';
import { MinusCircleOutlined, PlusOutlined, UploadOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import CONFIG from './consts/config';

const API_BASE = CONFIG.API_URL;

interface BookCopy {
  serial_num: string;
  access_type: 'READING_ROOM' | 'TAKE_HOME';
}

interface BookFormData {
  title: string;
  author: string;
  publisher: string;
  year_publication: number;
  copies: BookCopy[];
}


const BookForm = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm<BookFormData>();
  const [loading, setLoading] = useState(false);
  const [createdBookId, setCreatedBookId] = useState<number | null>(null);
  const [coverFile, setCoverFile] = useState<File | null>(null);
  const [coverUploading, setCoverUploading] = useState(false);
  const [coverPreviewUrl, setCoverPreviewUrl] = useState<string | null>(null);

  const onFinish = async (values: BookFormData) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        message.error('Необходимо авторизоваться');
        return;
      }

      const response = await fetch(`${API_BASE}/books`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(values),
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || 'Не удалось добавить книгу');
      }

      // Попробуем получить id созданной книги из ответа
      let data: unknown = null;
      let bookId: number | null = null;
      try {
        data = await response.json();
      } catch {
        // если ответ не JSON — игнорируем
      }

      // Если пришёл объект с id — запоминаем
      if (data && typeof data === 'object') {
        if (Array.isArray(data)) {
          // если API вернул массив, берем первый элемент
          const first = data[0] as unknown as { id?: number };
          bookId = first?.id ?? null;
        } else {
          const obj = data as { id?: number };
          bookId = obj.id ?? null;
        }
      }

      setCreatedBookId(bookId);

      message.success('Книга успешно добавлена');
      // Если id не получен, редиректим на каталог через 1.5 секунды
      // Если id получен, пользователь может загрузить обложку, редирект произойдет после загрузки
      if (!bookId) {
        setTimeout(() => {
          navigate('/catalog');
        }, 1500);
      }
    } catch (error) {
      message.error(error instanceof Error ? error.message : 'Произошла ошибка');
    } finally {
      setLoading(false);
    }
  };

  const uploadCover = async () => {
    const targetId = createdBookId;
    if (!targetId) {
      message.error('Нет id книги для загрузки обложки. Введите id вручную.');
      return;
    }
    if (!coverFile) {
      message.error('Выберите файл обложки');
      return;
    }

    setCoverUploading(true);
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        message.error('Необходимо авторизоваться');
        return;
      }

      const formData = new FormData();
      formData.append('cover', coverFile);

      const resp = await fetch(`${API_BASE}/books/${targetId}`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
          // Content-Type не ставим — браузер сам установит multipart boundary
        },
        body: formData,
      });

      if (!resp.ok) {
        const text = await resp.text();
        throw new Error(text || 'Не удалось загрузить обложку');
      }

      // Попробуем получить URL обложки из ответа
      try {
        const body = await resp.json();
        // ожидаем поле cover_url
        const coverUrl = body?.cover_url as string | undefined;
        if (coverUrl) {
          // если адрес относительный — преобразуем
          setCoverPreviewUrl(coverUrl.startsWith('http') ? coverUrl : `${API_BASE}${coverUrl}`);
        } else {
          // если сервер не вернул URL, оставляем локальную превью (если было)
          if (coverFile) {
            setCoverPreviewUrl(URL.createObjectURL(coverFile));
          }
        }
      } catch {
        if (coverFile) {
          setCoverPreviewUrl(URL.createObjectURL(coverFile));
        }
      }

      message.success('Обложка успешно загружена');
  // Сбрасываем выбранный файл, но оставляем превью и id — можно заменить картинку позже
  setCoverFile(null);
      // Редирект на каталог после успешной загрузки обложки
      setTimeout(() => {
        navigate('/catalog');
      }, 1500);
    } catch (e) {
      message.error(e instanceof Error ? e.message : 'Ошибка загрузки');
    } finally {
      setCoverUploading(false);
    }
  };

  // no inline image upload inside the main form

  return (
    <div className="max-w-3xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-semibold mb-6">Добавление новой книги</h1>
      
      <Form
        form={form}
        layout="vertical"
        onFinish={onFinish}
        initialValues={{
          copies: [{ access_type: 'READING_ROOM' }]
        }}
      >
        <Form.Item
          name="title"
          label="Название книги"
          rules={[
            { required: true, message: 'Введите название книги' },
            { max: 100, message: 'Название не должно превышать 100 символов' }
          ]}
        >
          <Input />
        </Form.Item>

        <Form.Item
          name="author"
          label="Автор"
          rules={[
            { required: true, message: 'Введите автора' },
            { max: 100, message: 'Имя автора не должно превышать 100 символов' }
          ]}
        >
          <Input />
        </Form.Item>

        <Form.Item
          name="publisher"
          label="Издательство"
          rules={[
            { required: true, message: 'Введите издательство' },
            { max: 100, message: 'Название издательства не должно превышать 100 символов' }
          ]}
        >
          <Input />
        </Form.Item>

        <Form.Item
          name="year_publication"
          label="Год публикации"
          rules={[
            { required: true, message: 'Введите год публикации' },
            { type: 'number', min: 1900, message: 'Год должен быть не раньше 1900' }
          ]}
        >
          <InputNumber style={{ width: '100%' }} />
        </Form.Item>

        {/* Обложка загружается после создания книги */}
        
        <div className="mb-4">
          <label className="font-medium">Экземпляры книги</label>
        </div>

        <Form.List
          name="copies"
          rules={[
            {
              validator: async (_, copies) => {
                if (!copies || copies.length < 1) {
                  return Promise.reject(new Error('Добавьте хотя бы один экземпляр'));
                }
              },
            },
          ]}
        >
          {(fields, { add, remove }) => (
            <>
              {fields.map(({ key, name, ...restField }) => (
                <Space key={key} style={{ display: 'flex', marginBottom: 8 }} align="baseline">
                  <Form.Item
                    {...restField}
                    name={[name, 'serial_num']}
                    rules={[
                      { required: true, message: 'Введите серийный номер' },
                    ]}
                  >
                    <Input placeholder="Серийный номер" />
                  </Form.Item>
                  
                  <Form.Item
                    {...restField}
                    name={[name, 'access_type']}
                    rules={[{ required: true, message: 'Выберите тип доступа' }]}
                  >
                    <Select style={{ width: 200 }}>
                      <Select.Option value="READING_ROOM">Только в читальном зале</Select.Option>
                      <Select.Option value="TAKE_HOME">Выдача на дом</Select.Option>
                    </Select>
                  </Form.Item>
                  
                  {fields.length > 1 && (
                    <MinusCircleOutlined onClick={() => remove(name)} />
                  )}
                </Space>
              ))}
              
              <Form.Item>
                <Button
                  type="dashed"
                  onClick={() => add()}
                  block
                  icon={<PlusOutlined />}
                >
                  Добавить экземпляр
                </Button>
              </Form.Item>
            </>
          )}
        </Form.List>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} size="large">
              Добавить книгу
            </Button>
          </Form.Item>
        </Form>

        {(createdBookId) && (
          <div className="mt-6 max-w-3xl">
            <h3 className="text-lg font-medium mb-2">Загрузить обложку</h3>
            <div className="flex items-start gap-6">
              <Upload
                beforeUpload={(file) => {
                  // revoke previous local preview if any
                  if (coverPreviewUrl && coverPreviewUrl.startsWith('blob:')) {
                    URL.revokeObjectURL(coverPreviewUrl);
                  }
                  const f = file as File;
                  setCoverFile(f);
                  setCoverPreviewUrl(URL.createObjectURL(f));
                  // prevent auto upload
                  return false;
                }}
                showUploadList={false}
              >
                <div
                  role="button"
                  tabIndex={0}
                  className="flex items-center justify-center border-dashed border rounded-md cursor-pointer"
                  style={{
                    width: 180,
                    height: 260,
                    borderWidth: 2,
                    borderColor: '#e6e6e6',
                    background: '#fafafa',
                    overflow: 'hidden'
                  }}
                >
                  {coverPreviewUrl ? (
                    <img
                      src={coverPreviewUrl}
                      alt="cover preview"
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                  ) : (
                    <div className="flex flex-col items-center text-center px-4">
                      <UploadOutlined style={{ fontSize: 36, color: '#1890ff' }} />
                      <div className="mt-2">Нажмите, чтобы выбрать обложку</div>
                      <div className="text-sm text-gray-500">jpg, png, max 5MB</div>
                    </div>
                  )}
                </div>
              </Upload>

              <div className="flex flex-col justify-between">
                <div>
                  <Button type="primary" onClick={uploadCover} loading={coverUploading} disabled={!(createdBookId) || (!coverFile && !coverPreviewUrl)}>
                    Загрузить обложку
                  </Button>
                  <Button className="ml-2 mt-2" onClick={() => { setCoverFile(null); if (coverPreviewUrl && coverPreviewUrl.startsWith('blob:')) { URL.revokeObjectURL(coverPreviewUrl); } setCoverPreviewUrl(null); }}>
                    Убрать
                  </Button>
                  <Button className="ml-2 mt-2" type="default" onClick={() => navigate('/catalog')}>
                    Перейти в каталог
                  </Button>
                </div>
                {coverFile && <div className="mt-2 text-sm text-gray-600">Выбран файл: {coverFile.name}</div>}
              </div>
            </div>
          </div>
        )}
      </div>
  );
};

export default BookForm;