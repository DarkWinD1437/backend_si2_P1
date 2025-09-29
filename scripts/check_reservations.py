from backend.apps.reservations.models import Reserva, AreaComun

try:
    area = AreaComun.objects.get(id=4)
    print(f'Area: {area.nombre}')
    reservas = Reserva.objects.filter(
        area_comun=area,
        estado__in=['confirmada', 'pagada', 'usada']
    ).order_by('fecha', 'hora_inicio')
    print(f'Reservas activas: {reservas.count()}')
    for r in reservas:
        print(f'- {r.fecha} {r.hora_inicio}-{r.hora_fin} ({r.estado})')
except AreaComun.DoesNotExist:
    print("Area 4 no existe")
except Exception as e:
    print(f"Error: {e}")