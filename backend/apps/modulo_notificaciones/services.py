import requests
import json
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from google.auth import default
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from .models import Notificacion, Dispositivo, PreferenciasNotificacion

User = get_user_model()


class NotificacionService:
    """Servicio para manejar el envío de notificaciones push"""

    def __init__(self):
        self.fcm_project_id = getattr(settings, 'FCM_PROJECT_ID', None)
        self.fcm_credentials_path = getattr(settings, 'FCM_CREDENTIALS_PATH', None)
        self.vapid_private_key = getattr(settings, 'VAPID_PRIVATE_KEY', None)
        self.vapid_email = getattr(settings, 'VAPID_CLAIMS_SUB', None)
        self._access_token = None
        self._token_expiry = None

    def enviar_notificacion_masiva(self, titulo, mensaje, tipo, usuarios_ids=None,
                                 destinatarios=None, datos_extra=None, prioridad=1):
        """
        Enviar notificación a múltiples usuarios
        """
        if usuarios_ids:
            usuarios = User.objects.filter(id__in=usuarios_ids, is_active=True)
        elif destinatarios:
            # Filtrar por roles
            usuarios = User.objects.filter(is_active=True)
            if 'residentes' in destinatarios:
                usuarios = usuarios.filter(role='resident')
            if 'administradores' in destinatarios:
                usuarios = usuarios.filter(role='admin')
            if 'seguridad' in destinatarios:
                usuarios = usuarios.filter(role='security')
        else:
            usuarios = User.objects.filter(is_active=True)

        resultados = {
            'total_usuarios': len(usuarios),
            'notificaciones_creadas': 0,
            'push_enviados': 0,
            'errores': []
        }

        for usuario in usuarios:
            try:
                # Verificar preferencias del usuario
                if not self._usuario_acepta_notificacion(usuario, tipo):
                    continue

                # Crear notificación
                notificacion = Notificacion.objects.create(
                    titulo=titulo,
                    mensaje=mensaje,
                    tipo=tipo,
                    usuario=usuario,
                    datos_extra=datos_extra or {},
                    prioridad=prioridad
                )

                # Enviar push a todos los dispositivos activos del usuario
                dispositivos_enviados = self._enviar_push_a_dispositivos(
                    notificacion, usuario
                )

                resultados['notificaciones_creadas'] += 1
                resultados['push_enviados'] += dispositivos_enviados

            except Exception as e:
                resultados['errores'].append({
                    'usuario_id': usuario.id,
                    'error': str(e)
                })

        return resultados

    def enviar_notificacion(self, notificacion):
        """
        Enviar una notificación específica
        """
        try:
            # Verificar preferencias
            if not self._usuario_acepta_notificacion(notificacion.usuario, notificacion.tipo):
                notificacion.estado = 'fallida'
                notificacion.error_mensaje = 'Usuario no acepta este tipo de notificación'
                notificacion.save()
                return False

            # Enviar push
            dispositivos_enviados = self._enviar_push_a_dispositivos(
                notificacion, notificacion.usuario
            )

            if dispositivos_enviados > 0:
                notificacion.marcar_como_enviada()
                return True
            else:
                notificacion.estado = 'fallida'
                notificacion.error_mensaje = 'No se pudo enviar a ningún dispositivo'
                notificacion.save()
                return False

        except Exception as e:
            notificacion.estado = 'fallida'
            notificacion.error_mensaje = str(e)
            notificacion.save()
            return False

    def _usuario_acepta_notificacion(self, usuario, tipo_notificacion):
        """
        Verificar si el usuario acepta este tipo de notificación
        """
        try:
            preferencia = PreferenciasNotificacion.objects.get(
                usuario=usuario,
                tipo_notificacion=tipo_notificacion
            )
            return preferencia.push_enabled
        except PreferenciasNotificacion.DoesNotExist:
            # Si no hay preferencia específica, asumir que acepta
            return True

    def _enviar_push_a_dispositivos(self, notificacion, usuario):
        """
        Enviar notificación push a todos los dispositivos activos del usuario
        """
        dispositivos = Dispositivo.objects.filter(
            usuario=usuario,
            activo=True
        )

        enviados = 0
        for dispositivo in dispositivos:
            try:
                if dispositivo.tipo_dispositivo in ['android', 'ios']:
                    # Usar FCM para móviles
                    if self._enviar_fcm(notificacion, dispositivo):
                        enviados += 1
                elif dispositivo.tipo_dispositivo == 'web':
                    # Usar web push para navegadores
                    if self._enviar_web_push(notificacion, dispositivo):
                        enviados += 1
                else:
                    # Para otros tipos, usar FCM por defecto
                    if self._enviar_fcm(notificacion, dispositivo):
                        enviados += 1
            except Exception as e:
                print(f"Error enviando a dispositivo {dispositivo.id}: {e}")

        return enviados

    def _get_access_token(self):
        """
        Obtener access token OAuth 2.0 para FCM
        """
        from datetime import datetime, timedelta

        # Si ya tenemos un token válido, lo reutilizamos
        if self._access_token and self._token_expiry and datetime.now() < self._token_expiry:
            return self._access_token

        try:
            if self.fcm_credentials_path:
                # Usar service account file
                credentials = service_account.Credentials.from_service_account_file(
                    self.fcm_credentials_path,
                    scopes=['https://www.googleapis.com/auth/firebase.messaging']
                )
            else:
                # Intentar usar Application Default Credentials
                credentials, project = default(scopes=['https://www.googleapis.com/auth/firebase.messaging'])
                if not self.fcm_project_id:
                    self.fcm_project_id = project

            # Refresh token si es necesario
            if not credentials.valid:
                request = Request()
                credentials.refresh(request)

            self._access_token = credentials.token
            # El token expira en 1 hora, pero guardamos con un margen de 5 minutos
            self._token_expiry = datetime.now() + timedelta(seconds=credentials.expiry.timestamp() - datetime.now().timestamp() - 300)

            return self._access_token

        except Exception as e:
            print(f"Error obteniendo access token: {e}")
            return None

    def _enviar_fcm(self, notificacion, dispositivo):
        """
        Enviar notificación usando Firebase Cloud Messaging API HTTP v1
        """
        if not self.fcm_project_id:
            print("FCM_PROJECT_ID no configurado")
            return False

        access_token = self._get_access_token()
        if not access_token:
            print("No se pudo obtener access token para FCM")
            return False

        url = f'https://fcm.googleapis.com/v1/projects/{self.fcm_project_id}/messages:send'

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        # Nuevo formato para FCM HTTP v1 API
        data = {
            'message': {
                'token': dispositivo.token_push,
                'notification': {
                    'title': notificacion.titulo,
                    'body': notificacion.mensaje,
                },
                'data': {
                    'tipo': notificacion.tipo,
                    'notificacion_id': str(notificacion.id),
                    'prioridad': str(notificacion.prioridad),
                    'click_action': '/notificaciones',
                    **{k: str(v) for k, v in notificacion.datos_extra.items()}  # Convertir valores a string
                },
                'android': {
                    'priority': 'high' if notificacion.prioridad >= 4 else 'normal',
                    'notification': {
                        'icon': 'ic_notification',
                        'color': '#1976D2',
                        'sound': 'default'
                    }
                },
                'apns': {
                    'headers': {
                        'apns-priority': '10' if notificacion.prioridad >= 4 else '5'
                    },
                    'payload': {
                        'aps': {
                            'alert': {
                                'title': notificacion.titulo,
                                'body': notificacion.mensaje,
                            },
                            'badge': 1,
                            'sound': 'default'
                        }
                    }
                }
            }
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)

            if response.status_code == 200:
                result = response.json()
                if 'name' in result:  # FCM v1 API retorna 'name' en caso de éxito
                    notificacion.push_enviado = True
                    notificacion.save()
                    return True
                else:
                    print(f"Respuesta FCM inesperada: {result}")
            else:
                error_data = response.json() if response.content else {}
                print(f"Error FCM: {response.status_code} - {error_data}")

        except requests.exceptions.RequestException as e:
            print(f"Error de conexión FCM: {e}")

        return False

    def _enviar_web_push(self, notificacion, dispositivo):
        """
        Enviar notificación web push
        """
        if not all([self.vapid_private_key, self.vapid_email]):
            print("VAPID keys no configuradas")
            return False

        # Para web push, necesitaríamos una librería como pywebpush
        # Por ahora, simularemos el envío
        print(f"Web push simulado para dispositivo {dispositivo.id}")
        notificacion.push_enviado = True
        notificacion.save()
        return True

    def crear_preferencias_default(self, usuario):
        """
        Crear preferencias de notificación por defecto para un usuario
        """
        tipos_default = [
            ('acceso_permitido', True, False, False),
            ('acceso_denegado', True, False, False),
            ('nuevo_mensaje', True, False, False),
            ('pago_realizado', True, True, False),
            ('pago_pendiente', True, True, True),
            ('mantenimiento', True, True, False),
            ('emergencia', True, True, True),
            ('recordatorio', True, False, False),
        ]

        for tipo, push, email, sms in tipos_default:
            PreferenciasNotificacion.objects.get_or_create(
                usuario=usuario,
                tipo_notificacion=tipo,
                defaults={
                    'push_enabled': push,
                    'email_enabled': email,
                    'sms_enabled': sms
                }
            )