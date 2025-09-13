"""
Servicio para generar comprobantes de pago en PDF
T4: Generar comprobante de pago - Módulo 2 Gestión Financiera Básica
"""

from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import uuid


class ComprobanteService:
    """Servicio para generar comprobantes de pago en PDF"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configurar estilos personalizados para el comprobante"""
        
        # Estilo para el título
        self.titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        # Estilo para subtítulos
        self.subtitulo_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.darkblue,
            alignment=TA_LEFT,
            spaceAfter=10,
            spaceBefore=10
        )
        
        # Estilo para texto normal
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_LEFT
        )
        
        # Estilo para texto centrado
        self.centro_style = ParagraphStyle(
            'CustomCenter',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_CENTER
        )
        
        # Estilo para monto destacado
        self.monto_style = ParagraphStyle(
            'CustomMonto',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=colors.darkgreen,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
    
    def generar_comprobante(self, cargo_financiero):
        """
        Generar comprobante de pago en PDF
        
        Args:
            cargo_financiero: Instancia de CargoFinanciero pagado
            
        Returns:
            BytesIO: Archivo PDF en memoria
        """
        if cargo_financiero.estado != 'pagado':
            raise ValueError("Solo se pueden generar comprobantes de cargos pagados")
        
        buffer = BytesIO()
        
        # Crear documento PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Construir contenido del comprobante
        story = []
        story.extend(self._crear_encabezado(cargo_financiero))
        story.extend(self._crear_datos_residente(cargo_financiero))
        story.extend(self._crear_detalle_pago(cargo_financiero))
        story.extend(self._crear_totales(cargo_financiero))
        story.extend(self._crear_pie_comprobante(cargo_financiero))
        
        # Generar PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def _crear_encabezado(self, cargo):
        """Crear encabezado del comprobante"""
        elementos = []
        
        # Título principal
        elementos.append(Paragraph("COMPROBANTE DE PAGO", self.titulo_style))
        elementos.append(Spacer(1, 20))
        
        # Información del condominio
        elementos.append(Paragraph("CONDOMINIO RESIDENCIAL", self.subtitulo_style))
        
        # Crear tabla con información del condominio y comprobante
        data = [
            ['Razón Social:', 'Condominio Torre Vista', 'No. Comprobante:', self._generar_numero_comprobante(cargo)],
            ['Dirección:', 'Av. Principal #123, Ciudad', 'Fecha Emisión:', datetime.now().strftime('%d/%m/%Y %H:%M')],
            ['Teléfono:', '(123) 456-7890', 'Estado:', 'PAGADO'],
            ['Email:', 'admin@condominio.com', 'Método Pago:', self._obtener_metodo_pago(cargo)]
        ]
        
        tabla_header = Table(data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
        tabla_header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elementos.append(tabla_header)
        elementos.append(Spacer(1, 20))
        
        return elementos
    
    def _crear_datos_residente(self, cargo):
        """Crear sección de datos del residente"""
        elementos = []
        
        elementos.append(Paragraph("DATOS DEL RESIDENTE", self.subtitulo_style))
        
        residente = cargo.residente
        nombre_completo = f"{residente.first_name} {residente.last_name}".strip() or residente.username
        
        data = [
            ['Usuario:', residente.username, 'Nombre:', nombre_completo],
            ['Email:', residente.email or 'No registrado', 'Teléfono:', getattr(residente, 'phone', 'No registrado')],
            ['Rol:', residente.get_role_display() if hasattr(residente, 'role') else 'Residente', 'ID Usuario:', str(residente.id)]
        ]
        
        tabla_residente = Table(data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
        tabla_residente.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elementos.append(tabla_residente)
        elementos.append(Spacer(1, 20))
        
        return elementos
    
    def _crear_detalle_pago(self, cargo):
        """Crear sección de detalle del pago"""
        elementos = []
        
        elementos.append(Paragraph("DETALLE DEL PAGO", self.subtitulo_style))
        
        concepto = cargo.concepto
        fecha_pago = cargo.fecha_pago.strftime('%d/%m/%Y %H:%M:%S') if cargo.fecha_pago else 'No registrada'
        
        data = [
            ['Concepto:', concepto.nombre],
            ['Descripción:', concepto.descripcion or 'Sin descripción'],
            ['Tipo:', concepto.get_tipo_display()],
            ['Fecha Aplicación:', cargo.fecha_aplicacion.strftime('%d/%m/%Y')],
            ['Fecha Vencimiento:', cargo.fecha_vencimiento.strftime('%d/%m/%Y')],
            ['Fecha Pago:', fecha_pago],
            ['Referencia Pago:', cargo.referencia_pago or 'Sin referencia'],
        ]
        
        tabla_detalle = Table(data, colWidths=[2*inch, 5*inch])
        tabla_detalle.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elementos.append(tabla_detalle)
        elementos.append(Spacer(1, 20))
        
        return elementos
    
    def _crear_totales(self, cargo):
        """Crear sección de totales"""
        elementos = []
        
        elementos.append(Paragraph("RESUMEN DE PAGO", self.subtitulo_style))
        
        # Calcular totales
        monto_base = float(cargo.monto)
        recargo = 0  # Por ahora sin recargo, pero puede extenderse
        total_pagado = monto_base + recargo
        
        data = [
            ['Monto Base:', f'${monto_base:,.2f}'],
            ['Recargo por Mora:', f'${recargo:,.2f}'],
            ['TOTAL PAGADO:', f'${total_pagado:,.2f}']
        ]
        
        tabla_totales = Table(data, colWidths=[3*inch, 2*inch])
        tabla_totales.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -2), colors.lightgrey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, -2), colors.black),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -2), 12),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elementos.append(tabla_totales)
        elementos.append(Spacer(1, 30))
        
        # Monto en palabras (opcional)
        monto_palabras = self._numero_a_palabras(total_pagado)
        elementos.append(Paragraph(f"<b>Son:</b> {monto_palabras}", self.normal_style))
        elementos.append(Spacer(1, 20))
        
        return elementos
    
    def _crear_pie_comprobante(self, cargo):
        """Crear pie del comprobante"""
        elementos = []
        
        # Información adicional
        elementos.append(Paragraph("INFORMACIÓN ADICIONAL", self.subtitulo_style))
        
        observaciones = cargo.observaciones if cargo.observaciones else "Sin observaciones adicionales"
        elementos.append(Paragraph(f"<b>Observaciones:</b> {observaciones}", self.normal_style))
        elementos.append(Spacer(1, 10))
        
        # Código de verificación
        codigo_verificacion = self._generar_codigo_verificacion(cargo)
        elementos.append(Paragraph(f"<b>Código de Verificación:</b> {codigo_verificacion}", self.normal_style))
        elementos.append(Spacer(1, 20))
        
        # Mensaje de validez
        elementos.append(Paragraph(
            "Este comprobante es válido como constancia de pago. "
            "Para verificar su autenticidad, consulte con el código de verificación en administración.",
            self.centro_style
        ))
        elementos.append(Spacer(1, 10))
        
        # Fecha y hora de generación
        fecha_generacion = datetime.now().strftime('%d de %B de %Y a las %H:%M:%S')
        elementos.append(Paragraph(
            f"Comprobante generado el {fecha_generacion}",
            self.centro_style
        ))
        
        return elementos
    
    def _generar_numero_comprobante(self, cargo):
        """Generar número único de comprobante"""
        fecha = cargo.fecha_pago or cargo.fecha_aplicacion
        return f"COMP-{fecha.strftime('%Y%m%d')}-{cargo.id:06d}"
    
    def _obtener_metodo_pago(self, cargo):
        """Obtener método de pago del cargo"""
        # Buscar en observaciones por método de pago
        observaciones = cargo.observaciones or ""
        if "efectivo" in observaciones.lower():
            return "Efectivo"
        elif "transferencia" in observaciones.lower():
            return "Transferencia"
        elif "cheque" in observaciones.lower():
            return "Cheque"
        elif "tarjeta" in observaciones.lower():
            return "Tarjeta"
        else:
            return "En línea"
    
    def _generar_codigo_verificacion(self, cargo):
        """Generar código de verificación único"""
        # Usar combinación de ID cargo, fecha y hash
        fecha_str = cargo.fecha_pago.strftime('%Y%m%d') if cargo.fecha_pago else cargo.fecha_aplicacion.strftime('%Y%m%d')
        codigo_base = f"{cargo.id}{fecha_str}{cargo.monto}"
        return f"VER-{hash(codigo_base) % 100000:05d}"
    
    def _numero_a_palabras(self, numero):
        """Convertir número a palabras (implementación básica)"""
        # Implementación simplificada - podría mejorarse con una librería específica
        if numero == 0:
            return "CERO PESOS"
        
        entero = int(numero)
        decimal = int((numero - entero) * 100)
        
        # Para simplicidad, solo convertimos números básicos
        if entero < 1000:
            if decimal > 0:
                return f"{entero:,} PESOS CON {decimal:02d}/100"
            else:
                return f"{entero:,} PESOS"
        else:
            if decimal > 0:
                return f"{entero:,} PESOS CON {decimal:02d}/100"
            else:
                return f"{entero:,} PESOS"


# Instancia global del servicio
comprobante_service = ComprobanteService()