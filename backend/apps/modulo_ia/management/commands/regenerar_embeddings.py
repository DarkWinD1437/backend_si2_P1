from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from backend.apps.modulo_ia.models import RostroRegistrado
from backend.apps.modulo_ia.facial_recognition import FacialRecognitionService
import base64
from io import BytesIO
from PIL import Image
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Regenera embeddings faciales para rostros registrados usando el nuevo sistema de reconocimiento facial'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Regenerar solo para un usuario específico (username)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Regenerar para todos los usuarios (por defecto)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar qué se haría sin hacer cambios',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔄 Iniciando regeneración de embeddings faciales...')
        )

        # Filtrar rostros a procesar
        queryset = RostroRegistrado.objects.filter(activo=True)

        if options['user']:
            try:
                user = User.objects.get(username=options['user'])
                queryset = queryset.filter(usuario=user)
                self.stdout.write(f'📋 Procesando rostros del usuario: {user.username}')
            except User.DoesNotExist:
                raise CommandError(f'Usuario "{options["user"]}" no encontrado')
        else:
            self.stdout.write('📋 Procesando todos los rostros registrados')

        total_rostros = queryset.count()
        if total_rostros == 0:
            self.stdout.write(
                self.style.WARNING('⚠️  No se encontraron rostros para procesar')
            )
            return

        self.stdout.write(f'📊 Total de rostros a procesar: {total_rostros}')

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('🔍 MODO DRY-RUN: No se harán cambios reales')
            )

        procesados = 0
        exitosos = 0
        fallidos = 0

        for rostro in queryset:
            procesados += 1

            self.stdout.write(
                f'🔄 Procesando rostro {procesados}/{total_rostros}: '
                f'{rostro.nombre_identificador} (Usuario: {rostro.usuario.username})'
            )

            try:
                # Verificar si el rostro tiene imagen
                if not rostro.imagen_rostro:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️  Rostro {rostro.nombre_identificador} no tiene imagen asociada'
                        )
                    )
                    fallidos += 1
                    continue

                # Convertir imagen a base64
                image_path = rostro.imagen_rostro.path
                if not os.path.exists(image_path):
                    self.stdout.write(
                        self.style.ERROR(
                            f'❌ Imagen no encontrada: {image_path}'
                        )
                    )
                    fallidos += 1
                    continue

                # Leer imagen y convertir a base64
                with open(image_path, 'rb') as f:
                    image_data = f.read()

                # Convertir a base64
                imagen_base64 = base64.b64encode(image_data).decode()

                # Extraer nuevo embedding
                embedding_data = FacialRecognitionService.extract_face_embedding(
                    FacialRecognitionService.decode_base64_image(imagen_base64)
                )

                if not options['dry_run']:
                    # Actualizar el embedding en la base de datos
                    rostro.embedding_ia = {
                        'vector': embedding_data['embedding'],
                        'timestamp': rostro.embedding_ia.get('timestamp', None) if rostro.embedding_ia else None,
                        'modelo': embedding_data['model'],
                        'note': f'Regenerated with face_recognition at {embedding_data["face_location"]}',
                        'confidence': embedding_data['confidence']
                    }
                    rostro.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Embedding regenerado exitosamente para {rostro.nombre_identificador}'
                    )
                )
                exitosos += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Error procesando rostro {rostro.nombre_identificador}: {str(e)}'
                    )
                )
                fallidos += 1

        # Resumen final
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('📊 RESUMEN DE REGENERACIÓN'))
        self.stdout.write('='*50)
        self.stdout.write(f'🔄 Total procesados: {procesados}')
        self.stdout.write(self.style.SUCCESS(f'✅ Exitosos: {exitosos}'))
        if fallidos > 0:
            self.stdout.write(self.style.ERROR(f'❌ Fallidos: {fallidos}'))

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('\n🔍 Este fue un dry-run. Ejecuta sin --dry-run para aplicar cambios.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\n🎉 Regeneración completada exitosamente!')
            )

        # Recomendaciones
        if exitosos > 0:
            self.stdout.write('\n💡 Recomendaciones:')
            self.stdout.write('   • Prueba el login facial con los rostros regenerados')
            self.stdout.write('   • Si aún hay problemas, verifica la calidad de las imágenes')
            self.stdout.write('   • Considera registrar nuevos rostros con mejor iluminación')