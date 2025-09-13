import psycopg2

conn = psycopg2.connect(host='localhost', database='Smart_Condominium', user='postgres', password='123456')
cursor = conn.cursor()

print("=== INVESTIGANDO ESTRUCTURA DE TABLAS ===")

# Obtener todas las tablas
cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
tablas = cursor.fetchall()
print("Tablas disponibles:", [t[0] for t in tablas])

# Investigar la tabla usuario
cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'usuario' ORDER BY ordinal_position")
cols = cursor.fetchall()
print("\nColumnas de 'usuario':", cols)

# Investigar la tabla camara
cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'camara' ORDER BY ordinal_position")
cols_camara = cursor.fetchall()
print("\nColumnas de 'camara':", cols_camara)

# Investigar la tabla vehiculo_autorizado
cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'vehiculo_autorizado' ORDER BY ordinal_position")
cols_vehiculo = cursor.fetchall()
print("\nColumnas de 'vehiculo_autorizado':", cols_vehiculo)

# Investigar la tabla persona_autorizada
cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'persona_autorizada' ORDER BY ordinal_position")
cols_persona = cursor.fetchall()
print("\nColumnas de 'persona_autorizada':", cols_persona)

# Ver estructura de unidad_habitacional
cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'unidad_habitacional' ORDER BY ordinal_position")
cols_unidad = cursor.fetchall()
print(f"\nColumnas de 'unidad_habitacional': {cols_unidad}")

# Ver estructura de cuota
cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'cuota' ORDER BY ordinal_position")
cols_cuota = cursor.fetchall()
print(f"\nColumnas de 'cuota': {cols_cuota}")

# Ver estructura de reserva
cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'reserva' ORDER BY ordinal_position")
cols_reserva = cursor.fetchall()
print(f"\nColumnas de 'reserva': {cols_reserva}")

# Ver estructura de aviso
cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'aviso' ORDER BY ordinal_position")
cols_aviso = cursor.fetchall()
print(f"\nColumnas de 'aviso': {cols_aviso}")

# Ver estructura de pago
cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'pago' ORDER BY ordinal_position")
cols_pago = cursor.fetchall()
print(f"\nColumnas de 'pago': {cols_pago}")

# Ver las zonas creadas
cursor.execute("SELECT id_zona, id_areaComun, nombre, tipo FROM zona ORDER BY id_zona")
zonas = cursor.fetchall()
print(f"\nZonas creadas ({len(zonas)}):")
for zona in zonas[:10]:  # Mostrar las primeras 10
    print(f"  ID: {zona[0]}, Área: {zona[1]}, Nombre: {zona[2]}, Tipo: {zona[3]}")

# Obtener algunos registros de ejemplo de usuario
cursor.execute("SELECT * FROM usuario LIMIT 3")
usuarios = cursor.fetchall()
print("\nPrimeros 3 usuarios:")
for u in usuarios:
    print(u)

cursor.close()
conn.close()
