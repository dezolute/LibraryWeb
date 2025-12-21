import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import MainLayout from './components/shared/main-layout';
import { Home } from './components/Home';
import Catalog from './components/Catalog';
import Account from './components/Account';
import RequestsManager from './components/RequestsManager';
import BookForm from './components/BookForm';
import BookPage from './components/BookPage';
import LoansPage from './components/LoansPage';
import BooksAdminPage from './components/BooksAdminPage';
import BookCopiesAdminPage from './components/BookCopiesAdminPage';

const theme = {
  components: {
    Layout: {
      colorBgHeader: '#ffffff',
      colorBgBody: '#f0f2f5',
      colorBgFooter: '#f7f7f7'
    },
    Menu: {
      fontSize: 16,
      colorItemBg: 'transparent'
    }
  },
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 6,
    fontFamily: 'Inter, system-ui, sans-serif'
  }
};

function App() {
  return (
    <ConfigProvider theme={theme}>
      <div className="min-h-screen flex flex-col">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<MainLayout><Home /></MainLayout>} />
            <Route path="/catalog" element={<MainLayout><Catalog /></MainLayout>} />
            <Route path="/book/:id" element={<MainLayout><BookPage /></MainLayout>} />
            <Route path="/account" element={<MainLayout><Account /></MainLayout>} />
            <Route path="/about" element={<MainLayout><div>О нас</div></MainLayout>} />
            <Route path="/privacy" element={<MainLayout><div>Политика конфиденциальности</div></MainLayout>} />
            <Route path="/terms" element={<MainLayout><div>Условия использования</div></MainLayout>} />
            
            <Route path="/employee/loans" element={<MainLayout><LoansPage /></MainLayout>} />
            <Route path="/employee/books/add" element={<MainLayout><BookForm /></MainLayout>} />
            <Route path="/employee/requests" element={<MainLayout><RequestsManager /></MainLayout>} />
            <Route path="/employee/books/" element={<MainLayout><BooksAdminPage/></MainLayout>} />
            <Route path="/employee/books/:id/copies" element={<MainLayout><BookCopiesAdminPage/></MainLayout>} />
          </Routes>
        </BrowserRouter>
      </div>
    </ConfigProvider>
  );
}

export default App
