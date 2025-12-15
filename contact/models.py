from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from contact.supabase_storage import SupabaseStorage
import random
import string

def get_supabase_storage():
    return SupabaseStorage()

class Category(models.Model):
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    name = models.CharField(max_length=60, verbose_name='Nome')

    def __str__(self):
        return f"{self.name}"

class Contact(models.Model):
    class Meta:
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'
        
    first_name = models.CharField(max_length=60, verbose_name='Nome')
    last_name = models.CharField(max_length=60, blank=True, verbose_name='Sobrenome')
    phone = models.CharField(max_length=50, verbose_name='Telefone')
    email = models.EmailField(max_length=254, blank=True, verbose_name='E-mail')
    create_date = models.DateTimeField(default=timezone.now, verbose_name='Data de criação')
    description = models.TextField(blank=True, verbose_name='Descrição')
    show = models.BooleanField(default=True, verbose_name='Exibir')
    picture = models.ImageField(blank=True, upload_to='contacts/', storage=get_supabase_storage, verbose_name='Foto')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Categoria')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Proprietário')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class EmailVerification(models.Model):
    class Meta:
        verbose_name = 'Verificação de Email'
        verbose_name_plural = 'Verificações de Email'
    
    email = models.EmailField(max_length=254, verbose_name='Email')
    code = models.CharField(max_length=6, verbose_name='Código')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    expires_at = models.DateTimeField(verbose_name='Expira em')
    is_verified = models.BooleanField(default=False, verbose_name='Verificado')
    
    def __str__(self):
        return f"Código {self.code} para {self.email}"
    
    @staticmethod
    def generate_code():
        """Gera um código de 6 dígitos"""
        return ''.join(random.choices(string.digits, k=6))
    
    def is_expired(self):
        """Verifica se o código expirou"""
        return timezone.now() > self.expires_at
    
    def verify(self, code):
        """Verifica se o código é válido"""
        if self.is_expired():
            return False, "Código expirado. Solicite um novo código."
        
        if self.code != code:
            return False, "Código inválido."
        
        if self.is_verified:
            return False, "Este código já foi utilizado."
        
        self.is_verified = True
        self.save()
        
        return True, "Email verificado com sucesso!"


class Profile(models.Model):
    """Perfil simples para armazenar um ID público aleatório do usuário."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    public_id = models.CharField(max_length=12, unique=True, verbose_name='ID Público')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.public_id})"

    @staticmethod
    def generate_public_id(length=8):
        """Gera um identificador público alfanumérico único"""
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(random.choices(alphabet, k=length))


# Sinal para criar Profile automaticamente com public_id único
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Gera um public_id único
        for _ in range(10):
            candidate = Profile.generate_public_id()
            if not Profile.objects.filter(public_id=candidate).exists():
                Profile.objects.create(user=instance, public_id=candidate)
                break
        else:
            # fallback (extremamente improvável)
            Profile.objects.create(user=instance, public_id=f"U{instance.id}{int(timezone.now().timestamp())}")