from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from contact.supabase_storage import SupabaseStorage

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
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Proprietário')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"