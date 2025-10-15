import { useEffect, useState } from 'react';
import { Spin } from 'antd';
import { Navigate } from 'react-router-dom';
import { CONFIG } from '../constants/config';

const apiUrl = CONFIG.API_URL;

const ProtectedRoute = ({ children }) => {
  const [allowed, setAllowed] = useState(null);
  const accessToken = localStorage.getItem('access_token');

  useEffect(() => {
    const checkAccess = async () => {
      if (!accessToken) {
        setAllowed(false);
        return;
      }

      try {
        const response = await fetch(`${apiUrl}/users/me`, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          setAllowed(false);
          return;
        }

        const user = await response.json();
        const hasAccess = user.role === 'EMPLOYEE' || user.role === 'ADMIN';
        setAllowed(hasAccess);
      } catch {
        setAllowed(false);
      }
    };

    checkAccess();
  }, []);

  if (allowed === null) return <Spin />;

  return allowed ? children : <Navigate to="/unauthorized" />;
};

export default ProtectedRoute;
