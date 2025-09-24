from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# Usa get_user_model() para obtener el modelo User personalizado
User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer personalizado para obtener tokens JWT con información adicional del usuario"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Agregar información adicional del usuario al token
        token['role'] = user.role
        token['username'] = user.username
        
        return token

    def validate(self, attrs):
        """Validar credenciales y retornar datos adicionales"""
        data = super().validate(attrs)
        
        # Agregar información del usuario a la respuesta
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'role': self.user.role,
            'phone': self.user.phone,
            'address': self.user.address,
        }
        
        return data

class UserSerializer(serializers.ModelSerializer):
    """Serializer para mostrar datos del usuario (sin password)"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'role', 'phone', 'address', 'profile_picture', 'date_joined')
        read_only_fields = ('id', 'date_joined')

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar perfil de usuario (sin username ni role)"""
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone', 'address', 'profile_picture')
        extra_kwargs = {
            'email': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def validate_email(self, value):
        """Validar que el email sea único, excluyendo el usuario actual"""
        user = self.instance
        if User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError('Este email ya está registrado por otro usuario')
        return value

class UserPasswordChangeSerializer(serializers.Serializer):
    """Serializer para cambio de contraseña"""
    current_password = serializers.CharField(required=True, help_text="Contraseña actual")
    new_password = serializers.CharField(required=True, min_length=8, help_text="Nueva contraseña (mínimo 8 caracteres)")
    new_password_confirm = serializers.CharField(required=True, help_text="Confirmar nueva contraseña")

    def validate_current_password(self, value):
        """Validar que la contraseña actual sea correcta"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('La contraseña actual es incorrecta')
        return value

    def validate_new_password(self, value):
        """Validar nueva contraseña con las reglas de Django"""
        validate_password(value)
        return value

    def validate(self, attrs):
        """Validar que las nuevas contraseñas coincidan"""
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        
        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': 'Las contraseñas no coinciden'
            })
        return attrs

class UserProfilePictureSerializer(serializers.ModelSerializer):
    """Serializer específico para actualizar solo la foto de perfil"""
    class Meta:
        model = User
        fields = ('profile_picture',)

class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear usuarios con validación de contraseña"""
    password = serializers.CharField(write_only=True, min_length=8, help_text="Mínimo 8 caracteres")
    password_confirm = serializers.CharField(write_only=True, help_text="Confirmar contraseña")
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password_confirm',
                 'first_name', 'last_name', 'role', 'phone', 'address')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        """Validar que las contraseñas coincidan"""
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        
        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden'
            })
        return attrs

    def validate_password(self, value):
        """Validar contraseña con las reglas de Django"""
        validate_password(value)
        return value

    def validate_email(self, value):
        """Validar que el email sea único"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Este email ya está registrado')
        return value

    def validate_username(self, value):
        """Validar que el username sea único"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Este nombre de usuario ya está registrado')
        return value

    def create(self, validated_data):
        # Remover password_confirm ya que no es parte del modelo
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user