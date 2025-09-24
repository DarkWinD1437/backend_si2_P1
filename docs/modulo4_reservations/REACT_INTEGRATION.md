# 📱 EJEMPLOS REACT - MÓDULO RESERVACIONES

## Configuración del Proyecto

### **1. Instalar Dependencias**
```bash
npm install axios react-router-dom @types/react-router-dom
```

### **2. Configuración de Axios**
```javascript
// src/services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// Interceptor para agregar token automáticamente
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## 🔐 **Autenticación**

### **Componente de Login**
```javascript
// src/components/Auth/Login.js
import React, { useState } from 'react';
import api from '../../services/api';

const Login = ({ onLogin }) => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/auth/login/', credentials);
      const { token, user } = response.data;

      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));

      onLogin(user);
    } catch (err) {
      setError('Credenciales inválidas');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit} className="login-form">
        <h2>Iniciar Sesión</h2>

        {error && <div className="error-message">{error}</div>}

        <div className="form-group">
          <label htmlFor="username">Usuario:</label>
          <input
            type="text"
            id="username"
            name="username"
            value={credentials.username}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">Contraseña:</label>
          <input
            type="password"
            id="password"
            name="password"
            value={credentials.password}
            onChange={handleChange}
            required
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Iniciando...' : 'Iniciar Sesión'}
        </button>
      </form>
    </div>
  );
};

export default Login;
```

---

## 🏢 **Gestión de Áreas Comunes**

### **Hook Personalizado para Áreas**
```javascript
// src/hooks/useAreas.js
import { useState, useEffect } from 'react';
import api from '../services/api';

export const useAreas = () => {
  const [areas, setAreas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAreas = async () => {
    try {
      setLoading(true);
      const response = await api.get('/reservations/areas/');
      setAreas(response.data);
      setError(null);
    } catch (err) {
      setError('Error al cargar áreas comunes');
      console.error('Error fetching areas:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAreas();
  }, []);

  return {
    areas,
    loading,
    error,
    refetch: fetchAreas
  };
};
```

### **Componente Lista de Áreas**
```javascript
// src/components/Areas/AreasList.js
import React from 'react';
import { useAreas } from '../../hooks/useAreas';
import { Link } from 'react-router-dom';

const AreasList = () => {
  const { areas, loading, error } = useAreas();

  if (loading) return <div className="loading">Cargando áreas...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="areas-container">
      <h1>Áreas Comunes Disponibles</h1>

      <div className="areas-grid">
        {areas.map(area => (
          <div key={area.id} className="area-card">
            <h3>{area.nombre}</h3>
            <p>{area.descripcion}</p>

            <div className="area-details">
              <span>Capacidad: {area.capacidad_maxima} personas</span>
              <span>Costo por hora: ${area.costo_por_hora}</span>
              <span>Costo reserva: ${area.costo_reserva}</span>
            </div>

            <div className="area-actions">
              <Link to={`/areas/${area.id}/disponibilidad`} className="btn-primary">
                Ver Disponibilidad
              </Link>
              <Link to={`/areas/${area.id}/reservar`} className="btn-secondary">
                Reservar
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AreasList;
```

---

## 📅 **Sistema de Reservas**

### **Componente de Disponibilidad**
```javascript
// src/components/Reservations/AvailabilityCalendar.js
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../../services/api';

const AvailabilityCalendar = () => {
  const { areaId } = useParams();
  const [availability, setAvailability] = useState(null);
  const [selectedDate, setSelectedDate] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchAvailability = async (date) => {
    if (!date) return;

    setLoading(true);
    try {
      const response = await api.get(
        `/reservations/areas/${areaId}/disponibilidad/?fecha=${date}`
      );
      setAvailability(response.data);
    } catch (error) {
      console.error('Error fetching availability:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedDate) {
      fetchAvailability(selectedDate);
    }
  }, [selectedDate]);

  const handleDateChange = (e) => {
    setSelectedDate(e.target.value);
  };

  return (
    <div className="availability-container">
      <h2>Disponibilidad de Área</h2>

      <div className="date-selector">
        <label htmlFor="fecha">Seleccionar Fecha:</label>
        <input
          type="date"
          id="fecha"
          value={selectedDate}
          onChange={handleDateChange}
          min={new Date().toISOString().split('T')[0]}
        />
      </div>

      {loading && <div className="loading">Cargando disponibilidad...</div>}

      {availability && (
        <div className="availability-results">
          <h3>{availability.area.nombre} - {availability.fecha}</h3>

          <div className="slots-grid">
            {availability.slots_disponibles.map((slot, index) => (
              <div
                key={index}
                className={`slot ${slot.disponible ? 'available' : 'unavailable'}`}
              >
                <span className="time">
                  {slot.hora_inicio} - {slot.hora_fin}
                </span>
                {!slot.disponible && (
                  <span className="reason">{slot.motivo_no_disponible}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AvailabilityCalendar;
```

### **Componente de Creación de Reserva**
```javascript
// src/components/Reservations/CreateReservation.js
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';

const CreateReservation = () => {
  const { areaId } = useParams();
  const navigate = useNavigate();
  const [area, setArea] = useState(null);
  const [availability, setAvailability] = useState([]);
  const [formData, setFormData] = useState({
    fecha_reserva: '',
    hora_inicio: '',
    hora_fin: '',
    numero_personas: 1,
    observaciones: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAreaDetails();
  }, [areaId]);

  const fetchAreaDetails = async () => {
    try {
      const response = await api.get(`/reservations/areas/${areaId}/`);
      setArea(response.data);
    } catch (error) {
      console.error('Error fetching area details:', error);
    }
  };

  const fetchAvailability = async (date) => {
    if (!date) return;

    try {
      const response = await api.get(
        `/reservations/areas/${areaId}/disponibilidad/?fecha=${date}`
      );
      const availableSlots = response.data.slots_disponibles.filter(
        slot => slot.disponible
      );
      setAvailability(availableSlots);
    } catch (error) {
      console.error('Error fetching availability:', error);
    }
  };

  const handleDateChange = (e) => {
    const date = e.target.value;
    setFormData({ ...formData, fecha_reserva: date });
    fetchAvailability(date);
  };

  const handleSlotSelect = (slot) => {
    setFormData({
      ...formData,
      hora_inicio: slot.hora_inicio,
      hora_fin: slot.hora_fin
    });
  };

  const calculateCost = () => {
    if (!area || !formData.hora_inicio || !formData.hora_fin) return 0;

    const start = new Date(`2000-01-01T${formData.hora_inicio}`);
    const end = new Date(`2000-01-01T${formData.hora_fin}`);
    const hours = (end - start) / (1000 * 60 * 60);

    return (hours * parseFloat(area.costo_por_hora)) + parseFloat(area.costo_reserva);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const reservationData = {
        area_comun_id: parseInt(areaId),
        ...formData
      };

      const response = await api.post('/reservations/reservas/', reservationData);

      navigate('/reservas', {
        state: {
          message: 'Reserva creada exitosamente',
          reservation: response.data
        }
      });
    } catch (err) {
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else {
        setError('Error al crear la reserva');
      }
    } finally {
      setLoading(false);
    }
  };

  if (!area) return <div className="loading">Cargando...</div>;

  return (
    <div className="reservation-form-container">
      <h2>Reservar {area.nombre}</h2>

      <form onSubmit={handleSubmit} className="reservation-form">
        {error && <div className="error-message">{error}</div>}

        <div className="form-group">
          <label htmlFor="fecha_reserva">Fecha de Reserva:</label>
          <input
            type="date"
            id="fecha_reserva"
            value={formData.fecha_reserva}
            onChange={handleDateChange}
            min={new Date().toISOString().split('T')[0]}
            required
          />
        </div>

        {availability.length > 0 && (
          <div className="form-group">
            <label>Horarios Disponibles:</label>
            <div className="slots-selection">
              {availability.map((slot, index) => (
                <button
                  key={index}
                  type="button"
                  className={`slot-button ${
                    formData.hora_inicio === slot.hora_inicio ? 'selected' : ''
                  }`}
                  onClick={() => handleSlotSelect(slot)}
                >
                  {slot.hora_inicio} - {slot.hora_fin}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="form-group">
          <label htmlFor="numero_personas">Número de Personas:</label>
          <input
            type="number"
            id="numero_personas"
            value={formData.numero_personas}
            onChange={(e) => setFormData({
              ...formData,
              numero_personas: parseInt(e.target.value)
            })}
            min="1"
            max={area.capacidad_maxima}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="observaciones">Observaciones:</label>
          <textarea
            id="observaciones"
            value={formData.observaciones}
            onChange={(e) => setFormData({
              ...formData,
              observaciones: e.target.value
            })}
            rows="3"
          />
        </div>

        <div className="cost-summary">
          <h3>Resumen de Costos</h3>
          <p>Costo por hora: ${area.costo_por_hora}</p>
          <p>Costo fijo: ${area.costo_reserva}</p>
          <p><strong>Total: ${calculateCost().toFixed(2)}</strong></p>
        </div>

        <button
          type="submit"
          disabled={loading || !formData.hora_inicio}
          className="btn-submit"
        >
          {loading ? 'Creando Reserva...' : 'Confirmar Reserva'}
        </button>
      </form>
    </div>
  );
};

export default CreateReservation;
```

---

## 📋 **Gestión de Mis Reservas**

### **Componente Lista de Reservas**
```javascript
// src/components/Reservations/MyReservations.js
import React, { useState, useEffect } from 'react';
import api from '../../services/api';

const MyReservations = () => {
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('todas');

  const fetchReservations = async () => {
    try {
      setLoading(true);
      const params = filter !== 'todas' ? { estado: filter } : {};
      const response = await api.get('/reservations/reservas/', { params });
      setReservations(response.data);
    } catch (error) {
      console.error('Error fetching reservations:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReservations();
  }, [filter]);

  const cancelReservation = async (reservationId) => {
    if (!window.confirm('¿Está seguro de que desea cancelar esta reserva?')) {
      return;
    }

    try {
      await api.put(`/reservations/reservas/${reservationId}/cancelar/`, {
        motivo_cancelacion: 'Cancelado por el usuario'
      });
      fetchReservations(); // Recargar lista
    } catch (error) {
      console.error('Error canceling reservation:', error);
      alert('Error al cancelar la reserva');
    }
  };

  const getStatusColor = (estado) => {
    const colors = {
      PENDIENTE: 'warning',
      CONFIRMADA: 'info',
      PAGADA: 'success',
      CANCELADA: 'danger',
      USADA: 'secondary'
    };
    return colors[estado] || 'secondary';
  };

  if (loading) return <div className="loading">Cargando reservas...</div>;

  return (
    <div className="my-reservations-container">
      <h1>Mis Reservas</h1>

      <div className="filter-controls">
        <label htmlFor="filter">Filtrar por estado:</label>
        <select
          id="filter"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="todas">Todas</option>
          <option value="PENDIENTE">Pendientes</option>
          <option value="CONFIRMADA">Confirmadas</option>
          <option value="PAGADA">Pagadas</option>
          <option value="CANCELADA">Canceladas</option>
          <option value="USADA">Usadas</option>
        </select>
      </div>

      <div className="reservations-list">
        {reservations.length === 0 ? (
          <p>No tienes reservas {filter !== 'todas' ? `en estado ${filter}` : ''}</p>
        ) : (
          reservations.map(reservation => (
            <div key={reservation.id} className="reservation-card">
              <div className="reservation-header">
                <h3>{reservation.area_comun.nombre}</h3>
                <span className={`status ${getStatusColor(reservation.estado)}`}>
                  {reservation.estado}
                </span>
              </div>

              <div className="reservation-details">
                <p><strong>Fecha:</strong> {reservation.fecha_reserva}</p>
                <p><strong>Horario:</strong> {reservation.hora_inicio} - {reservation.hora_fin}</p>
                <p><strong>Personas:</strong> {reservation.numero_personas}</p>
                <p><strong>Costo Total:</strong> ${reservation.costo_total}</p>
                {reservation.observaciones && (
                  <p><strong>Observaciones:</strong> {reservation.observaciones}</p>
                )}
              </div>

              <div className="reservation-actions">
                {reservation.estado === 'PENDIENTE' && (
                  <button
                    onClick={() => cancelReservation(reservation.id)}
                    className="btn-cancel"
                  >
                    Cancelar
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default MyReservations;
```

---

## 🎨 **Estilos CSS**

### **Archivo CSS Principal**
```css
/* src/styles/reservations.css */

.areas-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.areas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.area-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.area-details {
  margin: 15px 0;
}

.area-details span {
  display: block;
  margin: 5px 0;
  color: #666;
}

.area-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

.btn-primary, .btn-secondary {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.reservation-form-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.reservation-form {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.slots-selection {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
  margin-top: 10px;
}

.slot-button {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #f8f9fa;
  cursor: pointer;
}

.slot-button.selected {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.cost-summary {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  margin: 20px 0;
}

.btn-submit {
  width: 100%;
  padding: 12px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.btn-submit:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.my-reservations-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.reservations-list {
  margin-top: 20px;
}

.reservation-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 15px;
  background: white;
}

.reservation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.status {
  padding: 4px 8px;
  border-radius: 4px;
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.status.warning { background: #ffc107; }
.status.info { background: #17a2b8; }
.status.success { background: #28a745; }
.status.danger { background: #dc3545; }
.status.secondary { background: #6c757d; }

.reservation-details p {
  margin: 5px 0;
}

.reservation-actions {
  margin-top: 15px;
}

.btn-cancel {
  background: #dc3545;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.loading {
  text-align: center;
  padding: 20px;
  font-size: 18px;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
}
```

---

## 🚀 **Configuración de Rutas (React Router)**

### **App.js con Rutas**
```javascript
// src/App.js
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Auth/Login';
import AreasList from './components/Areas/AreasList';
import AvailabilityCalendar from './components/Reservations/AvailabilityCalendar';
import CreateReservation from './components/Reservations/CreateReservation';
import MyReservations from './components/Reservations/MyReservations';
import './styles/reservations.css';

function App() {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('user');
    return savedUser ? JSON.parse(savedUser) : null;
  });

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <Router>
      <div className="App">
        {user ? (
          <>
            <nav className="navbar">
              <div className="nav-brand">
                <h1>SmartCondominium</h1>
              </div>
              <div className="nav-links">
                <a href="/areas">Áreas Comunes</a>
                <a href="/reservas">Mis Reservas</a>
                <button onClick={handleLogout} className="btn-logout">
                  Cerrar Sesión ({user.username})
                </button>
              </div>
            </nav>

            <main className="main-content">
              <Routes>
                <Route path="/" element={<Navigate to="/areas" />} />
                <Route path="/areas" element={<AreasList />} />
                <Route path="/areas/:areaId/disponibilidad" element={<AvailabilityCalendar />} />
                <Route path="/areas/:areaId/reservar" element={<CreateReservation />} />
                <Route path="/reservas" element={<MyReservations />} />
              </Routes>
            </main>
          </>
        ) : (
          <Login onLogin={handleLogin} />
        )}
      </div>
    </Router>
  );
}

export default App;
```

---

**💡 Consejos para Implementación:**

1. **Manejo de Errores**: Implementa manejo de errores consistente en todos los componentes
2. **Loading States**: Muestra indicadores de carga durante las operaciones asíncronas
3. **Validación**: Valida los datos del formulario antes de enviarlos
4. **Responsive Design**: Asegúrate de que la interfaz funcione en dispositivos móviles
5. **Notificaciones**: Implementa un sistema de notificaciones para feedback al usuario
6. **Caché**: Considera cachear datos que no cambian frecuentemente

**🔗 Recursos Adicionales:**
- [React Documentation](https://reactjs.org/docs/)
- [Axios Documentation](https://axios-http.com/docs/)
- [React Router Documentation](https://reactrouter.com/)