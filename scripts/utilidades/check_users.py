from django.contrib.auth import get_user_model

User = get_user_model()

print("=== USUARIOS EXISTENTES ===")
users = User.objects.all()
if users:
    for user in users:
        role = getattr(user, 'role', 'N/A')
        print(f"- {user.username} (email: {user.email}, superuser: {user.is_superuser}, role: {role})")
else:
    print("No hay usuarios en la base de datos")

print(f"\nTotal usuarios: {users.count()}")
