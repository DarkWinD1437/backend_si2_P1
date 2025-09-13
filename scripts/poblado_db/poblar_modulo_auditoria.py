#!/usr/bin/env python
"""
Script para poblar el módulo de auditoría con datos de ejemplo
"""
import os
import sys
import django
from datetime import datetime, timedelta, date
from django.utils import timezone

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.apps.audit.models import RegistroAuditoria, SesionUsuario, EstadisticasAuditoria, TipoActividad, NivelImportancia
from backend.apps.audit.utils import AuditoriaLogger
from backend.apps.users.models import User
from django.contrib.contenttypes.models import ContentType

def poblar_registros_auditoria():
    """Crear registros de auditoría de ejemplo"""
    print("🔍 Creando registros de auditoría de ejemplo...")
    
    # Obtener usuarios existentes
    try:
        admin_user = User.objects.get(username='admin')
        carlos = User.objects.filter(username='carlos').first()
        ana = User.objects.filter(username='ana').first()
        miguel = User.objects.filter(username='miguel').first()
        
        usuarios = [u for u in [admin_user, carlos, ana, miguel] if u is not None]
        
    except User.DoesNotExist:
        print("❌ No se encontró el usuario admin. Ejecuta el poblado de usuarios primero.")
        return False
    
    # Limpiar registros existentes para evitar duplicados
    RegistroAuditoria.objects.all().delete()
    SesionUsuario.objects.all().delete()
    EstadisticasAuditoria.objects.all().delete()
    
    registros_creados = 0
    
    # 1. Registros de Login exitosos
    for i in range(15):
        fecha_base = timezone.now() - timedelta(days=i, hours=8+i%12)
        usuario = usuarios[i % len(usuarios)]
        
        AuditoriaLogger.registrar_actividad(
            usuario=usuario,
            tipo_actividad=TipoActividad.LOGIN,
            descripcion=f'Inicio de sesión exitoso para {usuario.username}',
            nivel_importancia=NivelImportancia.MEDIO,
            ip_address=f'192.168.1.{100+i%20}',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            es_exitoso=True,
            datos_adicionales={
                'metodo': 'POST',
                'endpoint': '/api/auth/login/',
                'rol': getattr(usuario, 'role', 'resident')
            }
        )
        registros_creados += 1
    
    # 2. Algunos intentos de login fallidos
    for i in range(5):
        fecha_base = timezone.now() - timedelta(days=i*2, hours=10)
        
        RegistroAuditoria.objects.create(
            usuario=None,
            tipo_actividad=TipoActividad.LOGIN,
            descripcion=f'Intento de login fallido para usuario: test_user_{i}',
            nivel_importancia=NivelImportancia.ALTO,
            timestamp=fecha_base,
            ip_address=f'192.168.1.{200+i}',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            es_exitoso=False,
            mensaje_error='Credenciales inválidas',
            datos_adicionales={
                'username_intentado': f'test_user_{i}',
                'intentos_consecutivos': i + 1
            }
        )
        registros_creados += 1
    
    # 3. Registros de Logout
    for i in range(12):
        fecha_base = timezone.now() - timedelta(days=i, hours=18+i%4)
        usuario = usuarios[i % len(usuarios)]
        
        AuditoriaLogger.registrar_logout(
            usuario=usuario,
            ip_address=f'192.168.1.{100+i%20}',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        )
        registros_creados += 1
    
    # 4. Registros de creación de usuarios
    for i, usuario in enumerate(usuarios[1:]):  # Excluir admin
        fecha_base = timezone.now() - timedelta(days=30-i*5)
        
        AuditoriaLogger.registrar_creacion(
            usuario=admin_user,
            objeto=usuario,
            descripcion_personalizada=f'Usuario registrado: {usuario.username}',
            datos_adicionales={
                'email': usuario.email,
                'rol': getattr(usuario, 'role', 'resident'),
                'via': 'admin_panel'
            }
        )
        registros_creados += 1
    
    # 5. Registros de actividades del módulo financiero (si existe)
    try:
        from backend.apps.finances.models import ConceptoFinanciero, CargoFinanciero
        
        conceptos = ConceptoFinanciero.objects.all()[:3]
        cargos = CargoFinanciero.objects.all()[:5]
        
        # Creación de conceptos
        for i, concepto in enumerate(conceptos):
            fecha_base = timezone.now() - timedelta(days=20-i*2, hours=14)
            
            AuditoriaLogger.registrar_creacion(
                usuario=admin_user,
                objeto=concepto,
                descripcion_personalizada=f'Concepto financiero creado: {concepto.nombre}',
                datos_adicionales={
                    'tipo': concepto.tipo,
                    'monto': str(concepto.monto),
                    'es_recurrente': concepto.es_recurrente
                }
            )
            registros_creados += 1
        
        # Procesamiento de pagos
        for i, cargo in enumerate(cargos):
            if i % 2 == 0:  # Simular algunos pagos
                fecha_base = timezone.now() - timedelta(days=10-i, hours=16)
                
                AuditoriaLogger.registrar_pago(
                    usuario=cargo.residente if cargo.residente else admin_user,
                    cargo=cargo,
                    referencia_pago=f'PAY-{2025}{9:02d}{13:02d}-{1000+i}',
                    monto=cargo.monto
                )
                registros_creados += 1
        
    except ImportError:
        print("   ℹ️  Módulo de finanzas no disponible, saltando registros financieros")
    
    # 6. Algunos errores del sistema
    errores_ejemplo = [
        {
            'descripcion': 'Error de conexión a base de datos',
            'error': 'Database connection timeout',
            'usuario': admin_user
        },
        {
            'descripcion': 'Error de validación en formulario',
            'error': 'Invalid data format in payment form',
            'usuario': carlos if carlos else admin_user
        },
        {
            'descripcion': 'Error de permisos',
            'error': 'Access denied to financial module',
            'usuario': ana if ana else admin_user
        }
    ]
    
    for i, error_data in enumerate(errores_ejemplo):
        fecha_base = timezone.now() - timedelta(days=15-i*3, hours=12)
        
        RegistroAuditoria.objects.create(
            usuario=error_data['usuario'],
            tipo_actividad=TipoActividad.ERROR_SISTEMA,
            descripcion=error_data['descripcion'],
            nivel_importancia=NivelImportancia.CRITICO,
            timestamp=fecha_base,
            ip_address=f'192.168.1.{150+i}',
            es_exitoso=False,
            mensaje_error=error_data['error'],
            datos_adicionales={
                'contexto': 'sistema_operativo',
                'severidad': 'alta'
            }
        )
        registros_creados += 1
    
    # 7. Accesos denegados
    for i in range(3):
        fecha_base = timezone.now() - timedelta(days=7-i*2, hours=11)
        usuario = usuarios[(i+1) % len(usuarios)]
        
        AuditoriaLogger.registrar_acceso_denegado(
            usuario=usuario,
            recurso=f'/admin/audit/registroauditoria/',
            motivo='Usuario sin permisos de administrador'
        )
        registros_creados += 1
    
    print(f"✅ Creados {registros_creados} registros de auditoría")
    return True


def poblar_sesiones_usuario():
    """Crear sesiones de usuario de ejemplo"""
    print("🔑 Creando sesiones de usuario de ejemplo...")
    
    usuarios = User.objects.all()[:4]
    sesiones_creadas = 0
    
    for i, usuario in enumerate(usuarios):
        # Sesiones activas
        if i < 2:  # Solo algunos usuarios tienen sesiones activas
            SesionUsuario.objects.create(
                usuario=usuario,
                token_session=f'token_activo_{usuario.username}_{i}',
                ip_address=f'192.168.1.{100+i}',
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                fecha_inicio=timezone.now() - timedelta(hours=2+i),
                fecha_ultimo_acceso=timezone.now() - timedelta(minutes=10+i*5),
                esta_activa=True
            )
            sesiones_creadas += 1
        
        # Sesiones cerradas
        for j in range(3):
            inicio = timezone.now() - timedelta(days=j+1, hours=8+j)
            cierre = inicio + timedelta(hours=2+j, minutes=30)
            
            SesionUsuario.objects.create(
                usuario=usuario,
                token_session=f'token_cerrado_{usuario.username}_{j}',
                ip_address=f'192.168.1.{110+i*10+j}',
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                fecha_inicio=inicio,
                fecha_ultimo_acceso=cierre,
                esta_activa=False,
                fecha_cierre=cierre
            )
            sesiones_creadas += 1
    
    print(f"✅ Creadas {sesiones_creadas} sesiones de usuario")
    return True


def poblar_estadisticas():
    """Crear estadísticas de auditoría de ejemplo"""
    print("📊 Creando estadísticas de auditoría...")
    
    estadisticas_creadas = 0
    
    for i in range(30):  # Últimos 30 días
        fecha = date.today() - timedelta(days=i)
        
        # Calcular estadísticas para esta fecha
        registros_dia = RegistroAuditoria.objects.filter(
            timestamp__date=fecha
        )
        
        total_actividades = registros_dia.count()
        total_logins = registros_dia.filter(tipo_actividad=TipoActividad.LOGIN, es_exitoso=True).count()
        actividades_criticas = registros_dia.filter(nivel_importancia=NivelImportancia.CRITICO).count()
        errores_sistema = registros_dia.filter(tipo_actividad=TipoActividad.ERROR_SISTEMA).count()
        
        # Usuarios únicos que tuvieron actividad
        usuarios_activos = registros_dia.filter(usuario__isnull=False).values('usuario').distinct().count()
        
        # Datos estadísticos detallados
        datos_detallados = {
            'actividades_por_tipo': {},
            'actividades_por_hora': {},
            'usuarios_mas_activos': {},
            'ips_mas_frecuentes': {}
        }
        
        # Contar por tipo de actividad
        for tipo in TipoActividad.choices:
            count = registros_dia.filter(tipo_actividad=tipo[0]).count()
            if count > 0:
                datos_detallados['actividades_por_tipo'][tipo[1]] = count
        
        if total_actividades > 0 or i < 7:  # Siempre crear para la última semana
            EstadisticasAuditoria.objects.create(
                fecha=fecha,
                total_actividades=total_actividades,
                total_logins=total_logins,
                total_usuarios_activos=usuarios_activos,
                actividades_criticas=actividades_criticas,
                errores_sistema=errores_sistema,
                datos_estadisticas=datos_detallados
            )
            estadisticas_creadas += 1
    
    print(f"✅ Creadas {estadisticas_creadas} estadísticas de auditoría")
    return True


def main():
    """Función principal del script de poblado"""
    print("🏗️  POBLANDO MÓDULO DE AUDITORÍA")
    print("=" * 50)
    
    try:
        # Poblar registros de auditoría
        if poblar_registros_auditoria():
            print("✅ Registros de auditoría poblados correctamente")
        
        # Poblar sesiones de usuario
        if poblar_sesiones_usuario():
            print("✅ Sesiones de usuario pobladas correctamente")
        
        # Poblar estadísticas
        if poblar_estadisticas():
            print("✅ Estadísticas pobladas correctamente")
        
        # Resumen final
        total_registros = RegistroAuditoria.objects.count()
        total_sesiones = SesionUsuario.objects.count()
        total_estadisticas = EstadisticasAuditoria.objects.count()
        
        print("\n📊 RESUMEN DEL POBLADO:")
        print(f"   📝 Registros de auditoría: {total_registros}")
        print(f"   🔑 Sesiones de usuario: {total_sesiones}")
        print(f"   📈 Estadísticas: {total_estadisticas}")
        
        print("\n🎯 PRÓXIMOS PASOS:")
        print("   1. Visita /admin/audit/ para ver los registros")
        print("   2. Los registros se crearán automáticamente con login/logout")
        print("   3. Cada acción importante queda registrada")
        
        print("\n🎉 ¡MÓDULO DE AUDITORÍA LISTO!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante el poblado: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)