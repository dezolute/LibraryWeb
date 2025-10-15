import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from './components/MainLayout';
import Home from './components/Home';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import BookCatalog from './components/BookCatalog';
import UserAccount from './components/UserAccount';
import BookPage from './components/BookPage';
import UnauthorizedPage from './components/UnauthorizedPage';
import EmployeeRequestsPage from './components/EmployeeRequestsPage';
import ProtectedRoute from './components/ProtectedRoute';

const App = () => (
  <Router>
    <Routes>
      <Route path="/" element={<MainLayout><Home /></MainLayout>} />

      <Route path="/login" element={<MainLayout><LoginForm /></MainLayout>} />
      <Route path="/register" element={<MainLayout><RegisterForm /></MainLayout>} />
      <Route path="/account" element={<MainLayout><UserAccount /></MainLayout>} />

      <Route path="/books" element={<MainLayout><BookCatalog /></MainLayout>} />
      <Route path="/book/:id" element={<MainLayout><BookPage /></MainLayout>} />

      <Route path="/employee/requests" 
        element={
          <MainLayout><ProtectedRoute><EmployeeRequestsPage /></ProtectedRoute></MainLayout>} />
      <Route path="/unauthorized" element={<MainLayout><UnauthorizedPage /></MainLayout>} />
    </Routes>
  </Router>
);

export default App;