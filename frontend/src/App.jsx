import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from './components/MainLayout';
import Home from './components/Home';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import BookCatalog from './components/BookCatalog';
import UserAccount from './components/UserAccount';
import BookPage from './components/BookPage';

const App = () => (
  <Router>
    <Routes>
      <Route path="/" element={<MainLayout><Home /></MainLayout>} />
      <Route path="/login" element={<MainLayout><LoginForm /></MainLayout>} />
      <Route path="/register" element={<MainLayout><RegisterForm /></MainLayout>} />
      <Route path="/books" element={<MainLayout><BookCatalog /></MainLayout>} />
      <Route path="/account" element={<MainLayout><UserAccount /></MainLayout>} />
      <Route path="/book/:id" element={<MainLayout><BookPage /></MainLayout>} />
      <Route path="/auth/google"/>
    </Routes>
  </Router>
);

export default App;
