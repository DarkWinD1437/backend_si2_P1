# 🔌 Guía de Integración API - Módulo Financiero
## Ejemplos para React-Vite y Flutter

---

## 🌐 React-Vite (Administradores)

### 🏗️ Configuración Base

```javascript
// services/financesAPI.js
const BASE_URL = 'http://127.0.0.1:8000/api/finances';

const getAuthHeaders = (token) => ({
  'Authorization': `Token ${token}`,
  'Content-Type': 'application/json',
});

const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`HTTP ${response.status}: ${error}`);
  }
  return await response.json();
};
```

### 📋 Gestión de Conceptos Financieros

#### Listar Conceptos
```javascript
// services/financesAPI.js
export const getConceptos = async (token, filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await fetch(`${BASE_URL}/conceptos/?${params}`, {
    headers: getAuthHeaders(token),
  });
  return handleResponse(response);
};

// components/ConceptosList.jsx
import React, { useState, useEffect } from 'react';
import { getConceptos } from '../services/financesAPI';

const ConceptosList = ({ token }) => {
  const [conceptos, setConceptos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ vigente: 'true' });

  useEffect(() => {
    loadConceptos();
  }, [filters]);

  const loadConceptos = async () => {
    try {
      setLoading(true);
      const data = await getConceptos(token, filters);
      setConceptos(data.results || data);
    } catch (error) {
      console.error('Error loading conceptos:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Cargando conceptos...</div>;

  return (
    <div className="conceptos-list">
      <div className="filters">
        <select 
          value={filters.tipo || ''} 
          onChange={(e) => setFilters({...filters, tipo: e.target.value})}
        >
          <option value="">Todos los tipos</option>
          <option value="cuota_mensual">Cuota Mensual</option>
          <option value="cuota_extraordinaria">Cuota Extraordinaria</option>
          <option value="multa_ruido">Multa por Ruido</option>
          <option value="multa_estacionamiento">Multa Estacionamiento</option>
        </select>
      </div>

      <div className="conceptos-grid">
        {conceptos.map(concepto => (
          <div key={concepto.id} className={`concepto-card ${concepto.esta_vigente ? 'vigente' : 'no-vigente'}`}>
            <h3>{concepto.nombre}</h3>
            <p className="tipo">{concepto.tipo_display}</p>
            <p className="monto">${concepto.monto}</p>
            <p className="estado">{concepto.estado_display}</p>
            {concepto.esta_vigente ? 
              <span className="badge vigente">✓ Vigente</span> : 
              <span className="badge no-vigente">✗ No vigente</span>
            }
          </div>
        ))}
      </div>
    </div>
  );
};

export default ConceptosList;
```

#### Crear Concepto
```javascript
// services/financesAPI.js
export const createConcepto = async (token, conceptoData) => {
  const response = await fetch(`${BASE_URL}/conceptos/`, {
    method: 'POST',
    headers: getAuthHeaders(token),
    body: JSON.stringify(conceptoData),
  });
  return handleResponse(response);
};

// components/ConceptoForm.jsx
import React, { useState } from 'react';
import { createConcepto } from '../services/financesAPI';

const ConceptoForm = ({ token, onSuccess }) => {
  const [formData, setFormData] = useState({
    nombre: '',
    descripcion: '',
    tipo: 'cuota_mensual',
    monto: '',
    es_recurrente: false,
    aplica_a_todos: true,
    fecha_vigencia_desde: new Date().toISOString().split('T')[0],
    fecha_vigencia_hasta: '',
  });

  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const newConcepto = await createConcepto(token, formData);
      console.log('Concepto creado:', newConcepto);
      onSuccess(newConcepto);
      // Reset form
      setFormData({
        nombre: '',
        descripcion: '',
        tipo: 'cuota_mensual',
        monto: '',
        es_recurrente: false,
        aplica_a_todos: true,
        fecha_vigencia_desde: new Date().toISOString().split('T')[0],
        fecha_vigencia_hasta: '',
      });
    } catch (error) {
      console.error('Error creating concepto:', error);
      alert(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="concepto-form">
      <h2>Crear Nuevo Concepto Financiero</h2>
      
      <div className="form-group">
        <label>Nombre:</label>
        <input
          type="text"
          value={formData.nombre}
          onChange={(e) => setFormData({...formData, nombre: e.target.value})}
          required
        />
      </div>

      <div className="form-group">
        <label>Descripción:</label>
        <textarea
          value={formData.descripcion}
          onChange={(e) => setFormData({...formData, descripcion: e.target.value})}
        />
      </div>

      <div className="form-group">
        <label>Tipo:</label>
        <select
          value={formData.tipo}
          onChange={(e) => setFormData({...formData, tipo: e.target.value})}
        >
          <option value="cuota_mensual">Cuota Mensual</option>
          <option value="cuota_extraordinaria">Cuota Extraordinaria</option>
          <option value="multa_ruido">Multa por Ruido</option>
          <option value="multa_areas_comunes">Multa Áreas Comunes</option>
          <option value="multa_estacionamiento">Multa Estacionamiento</option>
          <option value="multa_mascota">Multa por Mascota</option>
          <option value="otros">Otros</option>
        </select>
      </div>

      <div className="form-group">
        <label>Monto ($):</label>
        <input
          type="number"
          step="0.01"
          min="0.01"
          value={formData.monto}
          onChange={(e) => setFormData({...formData, monto: e.target.value})}
          required
        />
      </div>

      <div className="form-group checkbox-group">
        <label>
          <input
            type="checkbox"
            checked={formData.es_recurrente}
            onChange={(e) => setFormData({...formData, es_recurrente: e.target.checked})}
          />
          Es recurrente (se aplica automáticamente cada mes)
        </label>
      </div>

      <div className="form-group checkbox-group">
        <label>
          <input
            type="checkbox"
            checked={formData.aplica_a_todos}
            onChange={(e) => setFormData({...formData, aplica_a_todos: e.target.checked})}
          />
          Aplica a todos los residentes
        </label>
      </div>

      <div className="form-group">
        <label>Vigente desde:</label>
        <input
          type="date"
          value={formData.fecha_vigencia_desde}
          onChange={(e) => setFormData({...formData, fecha_vigencia_desde: e.target.value})}
          required
        />
      </div>

      <div className="form-group">
        <label>Vigente hasta (opcional):</label>
        <input
          type="date"
          value={formData.fecha_vigencia_hasta}
          onChange={(e) => setFormData({...formData, fecha_vigencia_hasta: e.target.value})}
        />
      </div>

      <button type="submit" disabled={loading} className="btn-primary">
        {loading ? 'Creando...' : 'Crear Concepto'}
      </button>
    </form>
  );
};

export default ConceptoForm;
```

### 💰 Gestión de Cargos Financieros

#### Aplicar Cargo a Residente
```javascript
// services/financesAPI.js
export const createCargo = async (token, cargoData) => {
  const response = await fetch(`${BASE_URL}/cargos/`, {
    method: 'POST',
    headers: getAuthHeaders(token),
    body: JSON.stringify(cargoData),
  });
  return handleResponse(response);
};

export const getResidentes = async (token) => {
  const response = await fetch('http://127.0.0.1:8000/api/users/', {
    headers: getAuthHeaders(token),
  });
  return handleResponse(response);
};

// components/AplicarCargoForm.jsx
const AplicarCargoForm = ({ token, conceptos, onSuccess }) => {
  const [formData, setFormData] = useState({
    concepto: '',
    residente: '',
    monto: '',
    fecha_vencimiento: '',
    observaciones: '',
  });
  
  const [residentes, setResidentes] = useState([]);

  useEffect(() => {
    loadResidentes();
  }, []);

  const loadResidentes = async () => {
    try {
      const data = await getResidentes(token);
      setResidentes(data.results || data);
    } catch (error) {
      console.error('Error loading residentes:', error);
    }
  };

  const handleConceptoChange = (conceptoId) => {
    const concepto = conceptos.find(c => c.id === parseInt(conceptoId));
    setFormData({
      ...formData,
      concepto: conceptoId,
      monto: concepto ? concepto.monto : '',
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const newCargo = await createCargo(token, formData);
      console.log('Cargo aplicado:', newCargo);
      onSuccess(newCargo);
    } catch (error) {
      console.error('Error aplicando cargo:', error);
      alert(`Error: ${error.message}`);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="cargo-form">
      <h2>Aplicar Cargo a Residente</h2>
      
      <div className="form-group">
        <label>Concepto:</label>
        <select
          value={formData.concepto}
          onChange={(e) => handleConceptoChange(e.target.value)}
          required
        >
          <option value="">Seleccionar concepto</option>
          {conceptos.map(concepto => (
            <option key={concepto.id} value={concepto.id}>
              {concepto.nombre} - ${concepto.monto}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Residente:</label>
        <select
          value={formData.residente}
          onChange={(e) => setFormData({...formData, residente: e.target.value})}
          required
        >
          <option value="">Seleccionar residente</option>
          {residentes.filter(r => r.role === 'resident' || !r.is_superuser).map(residente => (
            <option key={residente.id} value={residente.id}>
              {residente.first_name} {residente.last_name} ({residente.username})
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Monto ($):</label>
        <input
          type="number"
          step="0.01"
          min="0.01"
          value={formData.monto}
          onChange={(e) => setFormData({...formData, monto: e.target.value})}
          required
        />
      </div>

      <div className="form-group">
        <label>Fecha de vencimiento:</label>
        <input
          type="date"
          value={formData.fecha_vencimiento}
          onChange={(e) => setFormData({...formData, fecha_vencimiento: e.target.value})}
          min={new Date().toISOString().split('T')[0]}
        />
      </div>

      <div className="form-group">
        <label>Observaciones:</label>
        <textarea
          value={formData.observaciones}
          onChange={(e) => setFormData({...formData, observaciones: e.target.value})}
          placeholder="Detalles adicionales sobre el cargo..."
        />
      </div>

      <button type="submit" className="btn-primary">
        Aplicar Cargo
      </button>
    </form>
  );
};
```

---

## 📱 Flutter (Residentes y Seguridad)

### 🏗️ Configuración Base

```dart
// services/finances_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class FinancesService {
  static const String baseUrl = 'http://127.0.0.1:8000/api/finances';
  
  static Map<String, String> _getHeaders(String token) {
    return {
      'Authorization': 'Token $token',
      'Content-Type': 'application/json',
    };
  }
  
  static Future<T> _handleResponse<T>(http.Response response) async {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return json.decode(response.body);
    } else {
      throw Exception('HTTP ${response.statusCode}: ${response.body}');
    }
  }
}
```

### 💰 Ver Mis Cargos (Residentes)

```dart
// services/finances_service.dart
static Future<List<dynamic>> getMisCargos(String token) async {
  final response = await http.get(
    Uri.parse('$baseUrl/cargos/mis_cargos/'),
    headers: _getHeaders(token),
  );
  return _handleResponse(response);
}

static Future<Map<String, dynamic>> getResumenFinanciero(String token, int userId) async {
  final response = await http.get(
    Uri.parse('$baseUrl/cargos/resumen/$userId/'),
    headers: _getHeaders(token),
  );
  return _handleResponse(response);
}

// screens/mis_cargos_screen.dart
import 'package:flutter/material.dart';
import '../services/finances_service.dart';
import '../services/auth_service.dart';

class MisCargosScreen extends StatefulWidget {
  @override
  _MisCargosScreenState createState() => _MisCargosScreenState();
}

class _MisCargosScreenState extends State<MisCargosScreen> {
  List<dynamic> cargos = [];
  Map<String, dynamic>? resumen;
  bool loading = true;
  String? error;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      setState(() {
        loading = true;
        error = null;
      });

      final token = await AuthService.getToken();
      final userInfo = await AuthService.getUserInfo();
      
      if (token != null && userInfo != null) {
        final [cargosData, resumenData] = await Future.wait([
          FinancesService.getMisCargos(token),
          FinancesService.getResumenFinanciero(token, userInfo['id']),
        ]);
        
        setState(() {
          cargos = cargosData;
          resumen = resumenData;
          loading = false;
        });
      }
    } catch (e) {
      setState(() {
        error = 'Error cargando datos: $e';
        loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Mis Cargos'),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: _loadData,
          ),
        ],
      ),
      body: loading 
        ? Center(child: CircularProgressIndicator())
        : error != null
          ? _buildErrorWidget()
          : _buildContent(),
    );
  }

  Widget _buildErrorWidget() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.error_outline, size: 64, color: Colors.red),
          SizedBox(height: 16),
          Text(error!, textAlign: TextAlign.center),
          SizedBox(height: 16),
          ElevatedButton(
            onPressed: _loadData,
            child: Text('Reintentar'),
          ),
        ],
      ),
    );
  }

  Widget _buildContent() {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: Column(
        children: [
          if (resumen != null) _buildResumen(),
          Expanded(child: _buildCargosList()),
        ],
      ),
    );
  }

  Widget _buildResumen() {
    return Container(
      margin: EdgeInsets.all(16),
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 2,
            blurRadius: 5,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Resumen Financiero',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildResumenItem(
                'Pendiente',
                '\$${resumen!['total_pendiente']}',
                Colors.orange,
                Icons.schedule,
              ),
              _buildResumenItem(
                'Vencido',
                '\$${resumen!['total_vencido']}',
                Colors.red,
                Icons.warning,
              ),
              _buildResumenItem(
                'Pagado este mes',
                '\$${resumen!['total_pagado_mes']}',
                Colors.green,
                Icons.check_circle,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildResumenItem(String label, String value, Color color, IconData icon) {
    return Column(
      children: [
        Icon(icon, color: color, size: 24),
        SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: TextStyle(fontSize: 12, color: Colors.grey[600]),
        ),
      ],
    );
  }

  Widget _buildCargosList() {
    if (cargos.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.receipt_long, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text('No tienes cargos registrados'),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: EdgeInsets.symmetric(horizontal: 16),
      itemCount: cargos.length,
      itemBuilder: (context, index) {
        final cargo = cargos[index];
        return _buildCargoCard(cargo);
      },
    );
  }

  Widget _buildCargoCard(Map<String, dynamic> cargo) {
    final isPendiente = cargo['estado'] == 'pendiente';
    final isPagado = cargo['estado'] == 'pagado';
    final isVencido = cargo['esta_vencido'] == true;
    
    Color statusColor = Colors.grey;
    IconData statusIcon = Icons.info;
    
    if (isPagado) {
      statusColor = Colors.green;
      statusIcon = Icons.check_circle;
    } else if (isVencido) {
      statusColor = Colors.red;
      statusIcon = Icons.warning;
    } else if (isPendiente) {
      statusColor = Colors.orange;
      statusIcon = Icons.schedule;
    }

    return Card(
      margin: EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    cargo['concepto_nombre'],
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Row(
                  children: [
                    Icon(statusIcon, color: statusColor, size: 20),
                    SizedBox(width: 4),
                    Text(
                      cargo['estado_display'],
                      style: TextStyle(color: statusColor),
                    ),
                  ],
                ),
              ],
            ),
            SizedBox(height: 8),
            Text(
              'Tipo: ${cargo['concepto_tipo']}',
              style: TextStyle(color: Colors.grey[600]),
            ),
            SizedBox(height: 4),
            Text(
              'Monto: \$${cargo['monto']}',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Theme.of(context).primaryColor,
              ),
            ),
            SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Aplicado: ${_formatDate(cargo['fecha_aplicacion'])}',
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
                Text(
                  'Vence: ${_formatDate(cargo['fecha_vencimiento'])}',
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
              ],
            ),
            if (isPendiente && !isVencido) ...[
              SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () => _mostrarDialogoPago(cargo),
                  icon: Icon(Icons.payment),
                  label: Text('Pagar'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                  ),
                ),
              ),
            ],
            if (isVencido) ...[
              SizedBox(height: 8),
              Container(
                padding: EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(Icons.warning, color: Colors.red, size: 20),
                    SizedBox(width: 8),
                    Text(
                      'Este cargo está vencido',
                      style: TextStyle(color: Colors.red),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  String _formatDate(String dateStr) {
    try {
      final date = DateTime.parse(dateStr);
      return '${date.day}/${date.month}/${date.year}';
    } catch (e) {
      return dateStr;
    }
  }

  void _mostrarDialogoPago(Map<String, dynamic> cargo) {
    showDialog(
      context: context,
      builder: (context) => PagoDialog(
        cargo: cargo,
        onPagoExitoso: () {
          _loadData(); // Recargar datos después del pago
        },
      ),
    );
  }
}
```

### 💳 Procesar Pago

```dart
// services/finances_service.dart
static Future<Map<String, dynamic>> pagarCargo(
  String token,
  int cargoId,
  String referenciaPago,
  String? observaciones,
) async {
  final response = await http.post(
    Uri.parse('$baseUrl/cargos/$cargoId/pagar/'),
    headers: _getHeaders(token),
    body: json.encode({
      'referencia_pago': referenciaPago,
      'observaciones': observaciones ?? '',
    }),
  );
  return _handleResponse(response);
}

// widgets/pago_dialog.dart
import 'package:flutter/material.dart';
import '../services/finances_service.dart';
import '../services/auth_service.dart';

class PagoDialog extends StatefulWidget {
  final Map<String, dynamic> cargo;
  final VoidCallback onPagoExitoso;

  PagoDialog({required this.cargo, required this.onPagoExitoso});

  @override
  _PagoDialogState createState() => _PagoDialogState();
}

class _PagoDialogState extends State<PagoDialog> {
  final _referenciaController = TextEditingController();
  final _observacionesController = TextEditingController();
  bool _procesando = false;

  @override
  void initState() {
    super.initState();
    // Generar referencia automática
    _referenciaController.text = 'APP-${DateTime.now().millisecondsSinceEpoch}';
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('Procesar Pago'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Concepto: ${widget.cargo['concepto_nombre']}'),
            SizedBox(height: 8),
            Text(
              'Monto: \$${widget.cargo['monto']}',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Theme.of(context).primaryColor,
              ),
            ),
            SizedBox(height: 16),
            TextField(
              controller: _referenciaController,
              decoration: InputDecoration(
                labelText: 'Referencia de Pago',
                hintText: 'Número de transacción, etc.',
              ),
            ),
            SizedBox(height: 12),
            TextField(
              controller: _observacionesController,
              decoration: InputDecoration(
                labelText: 'Observaciones (opcional)',
                hintText: 'Detalles adicionales...',
              ),
              maxLines: 3,
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: _procesando ? null : () => Navigator.pop(context),
          child: Text('Cancelar'),
        ),
        ElevatedButton(
          onPressed: _procesando ? null : _procesarPago,
          child: _procesando 
            ? SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            : Text('Confirmar Pago'),
        ),
      ],
    );
  }

  Future<void> _procesarPago() async {
    if (_referenciaController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('La referencia de pago es requerida')),
      );
      return;
    }

    setState(() => _procesando = true);

    try {
      final token = await AuthService.getToken();
      if (token != null) {
        final resultado = await FinancesService.pagarCargo(
          token,
          widget.cargo['id'],
          _referenciaController.text.trim(),
          _observacionesController.text.trim(),
        );

        Navigator.pop(context);
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('✅ Pago procesado exitosamente'),
            backgroundColor: Colors.green,
          ),
        );

        widget.onPagoExitoso();
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error procesando pago: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      if (mounted) {
        setState(() => _procesando = false);
      }
    }
  }

  @override
  void dispose() {
    _referenciaController.dispose();
    _observacionesController.dispose();
    super.dispose();
  }
}
```

### 📋 Ver Conceptos (Solo lectura)

```dart
// services/finances_service.dart
static Future<List<dynamic>> getConceptosVigentes(String token) async {
  final response = await http.get(
    Uri.parse('$baseUrl/conceptos/vigentes/'),
    headers: _getHeaders(token),
  );
  return _handleResponse(response);
}

// screens/conceptos_screen.dart
class ConceptosScreen extends StatefulWidget {
  @override
  _ConceptosScreenState createState() => _ConceptosScreenState();
}

class _ConceptosScreenState extends State<ConceptosScreen> {
  List<dynamic> conceptos = [];
  bool loading = true;

  @override
  void initState() {
    super.initState();
    _loadConceptos();
  }

  Future<void> _loadConceptos() async {
    try {
      setState(() => loading = true);
      final token = await AuthService.getToken();
      if (token != null) {
        final data = await FinancesService.getConceptosVigentes(token);
        setState(() {
          conceptos = data;
          loading = false;
        });
      }
    } catch (e) {
      setState(() => loading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error cargando conceptos: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Conceptos de Cobro')),
      body: loading
        ? Center(child: CircularProgressIndicator())
        : ListView.builder(
            padding: EdgeInsets.all(16),
            itemCount: conceptos.length,
            itemBuilder: (context, index) {
              final concepto = conceptos[index];
              return Card(
                margin: EdgeInsets.only(bottom: 12),
                child: ListTile(
                  title: Text(concepto['nombre']),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(concepto['descripcion'] ?? ''),
                      SizedBox(height: 4),
                      Text('Tipo: ${concepto['tipo_display']}'),
                    ],
                  ),
                  trailing: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        '\$${concepto['monto']}',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Theme.of(context).primaryColor,
                        ),
                      ),
                      if (concepto['es_recurrente'])
                        Text(
                          'Recurrente',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.blue,
                          ),
                        ),
                    ],
                  ),
                ),
              );
            },
          ),
    );
  }
}
```

---

## 🔧 Manejo de Errores y Estados

### React-Vite
```javascript
// hooks/useFinances.js
import { useState, useEffect } from 'react';
import * as FinancesAPI from '../services/financesAPI';

export const useConceptos = (token, filters = {}) => {
  const [conceptos, setConceptos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadConceptos = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await FinancesAPI.getConceptos(token, filters);
      setConceptos(data.results || data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      loadConceptos();
    }
  }, [token, JSON.stringify(filters)]);

  return { conceptos, loading, error, reload: loadConceptos };
};
```

### Flutter
```dart
// providers/finances_provider.dart
import 'package:flutter/foundation.dart';
import '../services/finances_service.dart';
import '../services/auth_service.dart';

class FinancesProvider with ChangeNotifier {
  List<dynamic> _cargos = [];
  Map<String, dynamic>? _resumen;
  bool _loading = false;
  String? _error;

  List<dynamic> get cargos => _cargos;
  Map<String, dynamic>? get resumen => _resumen;
  bool get loading => _loading;
  String? get error => _error;

  Future<void> loadMisCargos() async {
    try {
      _loading = true;
      _error = null;
      notifyListeners();

      final token = await AuthService.getToken();
      if (token != null) {
        _cargos = await FinancesService.getMisCargos(token);
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  Future<bool> pagarCargo(int cargoId, String referencia, String? observaciones) async {
    try {
      final token = await AuthService.getToken();
      if (token != null) {
        await FinancesService.pagarCargo(token, cargoId, referencia, observaciones);
        await loadMisCargos(); // Recargar datos
        return true;
      }
      return false;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }
}
```

---

## 📊 Constantes y Tipos

### React-Vite
```javascript
// constants/finances.js
export const TIPOS_CONCEPTO = {
  CUOTA_MENSUAL: 'cuota_mensual',
  CUOTA_EXTRAORDINARIA: 'cuota_extraordinaria',
  MULTA_RUIDO: 'multa_ruido',
  MULTA_AREAS_COMUNES: 'multa_areas_comunes',
  MULTA_ESTACIONAMIENTO: 'multa_estacionamiento',
  MULTA_MASCOTA: 'multa_mascota',
  OTROS: 'otros',
};

export const ESTADOS_CONCEPTO = {
  ACTIVO: 'activo',
  INACTIVO: 'inactivo',
  SUSPENDIDO: 'suspendido',
};

export const ESTADOS_CARGO = {
  PENDIENTE: 'pendiente',
  PAGADO: 'pagado',
  VENCIDO: 'vencido',
  CANCELADO: 'cancelado',
};

export const TIPOS_CONCEPTO_LABELS = {
  [TIPOS_CONCEPTO.CUOTA_MENSUAL]: 'Cuota Mensual',
  [TIPOS_CONCEPTO.CUOTA_EXTRAORDINARIA]: 'Cuota Extraordinaria',
  [TIPOS_CONCEPTO.MULTA_RUIDO]: 'Multa por Ruido',
  [TIPOS_CONCEPTO.MULTA_AREAS_COMUNES]: 'Multa Áreas Comunes',
  [TIPOS_CONCEPTO.MULTA_ESTACIONAMIENTO]: 'Multa Estacionamiento',
  [TIPOS_CONCEPTO.MULTA_MASCOTA]: 'Multa por Mascota',
  [TIPOS_CONCEPTO.OTROS]: 'Otros',
};
```

### Flutter
```dart
// constants/finances_constants.dart
class FinancesConstants {
  static const String baseUrl = 'http://127.0.0.1:8000/api/finances';
  
  static const Map<String, String> tiposConcepto = {
    'cuota_mensual': 'Cuota Mensual',
    'cuota_extraordinaria': 'Cuota Extraordinaria',
    'multa_ruido': 'Multa por Ruido',
    'multa_areas_comunes': 'Multa Áreas Comunes',
    'multa_estacionamiento': 'Multa Estacionamiento',
    'multa_mascota': 'Multa por Mascota',
    'otros': 'Otros',
  };
  
  static const Map<String, String> estadosCargo = {
    'pendiente': 'Pendiente',
    'pagado': 'Pagado',
    'vencido': 'Vencido',
    'cancelado': 'Cancelado',
  };
}
```

---

**🔧 Herramientas Recomendadas:**
- **React**: Axios para HTTP, React Query para cache
- **Flutter**: http package, Provider/Riverpod para state management
- **Validación**: Implementar validación en frontend antes de enviar
- **Cache**: Cachear conceptos vigentes para mejor performance
- **Offline**: Considerar funcionalidad offline para consultas básicas