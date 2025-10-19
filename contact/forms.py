from django import forms
from contact.models import Contact
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import password_validation

class ContactForm(forms.ModelForm):
    picture = forms.ImageField(
        label='Foto',
        required=False,
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
                'class': 'form-control'
            }
        ),
        help_text='Selecione uma foto (opcional)'
    )

    class Meta:
        model = Contact
        fields = ('first_name', 'last_name', 'phone', 'email', 'description', 'category', 'picture',)
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'phone': 'Telefone',
            'email': 'E-mail',
            'description': 'Descrição',
            'category': 'Categoria',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o nome'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o sobrenome'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 99999-9999'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'nome@email.com'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Adicione uma descrição...'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'phone': 'Digite apenas números (DDD + número)',
            'email': 'E-mail válido (opcional)',
            'description': 'Informações adicionais sobre o contato',
            'category': 'Selecione uma categoria para organizar seus contatos'
        }

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')

        if not first_name:
            raise ValidationError("Nome é obrigatório.", code='invalid')

        if len(first_name.strip()) < 2:
            raise ValidationError("Nome deve ter pelo menos 2 caracteres.", code='invalid')

        # Permitir acentos e espaços, apenas não permitir números
        if any(char.isdigit() for char in first_name):
            raise ValidationError("Nome não pode conter números.", code='invalid')

        return first_name.strip().title()

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')

        if last_name:  # Campo opcional
            if len(last_name.strip()) < 2:
                raise ValidationError("Sobrenome deve ter pelo menos 2 caracteres.", code='invalid')

            if any(char.isdigit() for char in last_name):
                raise ValidationError("Sobrenome não pode conter números.", code='invalid')
            
            return last_name.strip().title()
        
        return last_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if not phone:
            raise ValidationError("Telefone é obrigatório.", code='invalid')

        # Remove caracteres especiais e espaços
        phone_digits = ''.join(filter(str.isdigit, phone))

        if len(phone_digits) < 10:
            raise ValidationError("Telefone deve ter pelo menos 10 dígitos.", code='invalid')

        if len(phone_digits) > 15:
            raise ValidationError("Telefone deve ter no máximo 15 dígitos.", code='invalid')

        return phone_digits

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email:  # Campo opcional
            if '@' not in email or '.' not in email.split('@')[-1]:
                raise ValidationError("Insira um endereço de e-mail válido.", code='invalid')
            return email.lower().strip()
        
        return email

    def clean_description(self):
        description = self.cleaned_data.get('description')

        if description:  # Campo opcional
            if len(description.strip()) < 5:
                raise ValidationError("Descrição deve ter pelo menos 5 caracteres.", code='invalid')
            return description.strip()
        
        return description

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2',)
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
            'username': 'Nome de usuário',
            'password1': 'Senha',
            'password2': 'Confirmação de senha',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu nome'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu sobrenome'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome de usuário único'}),
        }
        help_texts = {
            'username': 'Obrigatório. 150 caracteres ou menos. Apenas letras, números e @/./+/-/_ permitidos.',
            'password1': 'Sua senha deve ter pelo menos 8 caracteres.',
            'password2': 'Digite a mesma senha novamente para confirmação.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua senha'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirme sua senha'})

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')

        if not first_name:
            raise ValidationError("Nome é obrigatório.", code='invalid')

        if any(char.isdigit() for char in first_name):
            raise ValidationError("Nome não pode conter números.", code='invalid')

        return first_name.strip().title()

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')

        if not last_name:
            raise ValidationError("Sobrenome é obrigatório.", code='invalid')

        if any(char.isdigit() for char in last_name):
            raise ValidationError("Sobrenome não pode conter números.", code='invalid')

        return last_name.strip().title()

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if not username:
            raise ValidationError("Nome de usuário é obrigatório.", code='invalid')

        if len(username) < 4:
            raise ValidationError("Nome de usuário deve ter pelo menos 4 caracteres.", code='invalid')

        if User.objects.filter(username=username).exists():
            raise ValidationError("Este nome de usuário já está em uso.", code='invalid')

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not email:
            raise ValidationError("E-mail é obrigatório.", code='invalid')

        if '@' not in email or '.' not in email.split('@')[-1]:
            raise ValidationError("Digite um endereço de e-mail válido.", code='invalid')

        if User.objects.filter(email=email).exists():
            raise ValidationError("Este e-mail já está cadastrado.", code='invalid')

        return email.lower().strip()

class RegisterUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        min_length=2,
        max_length=30,
        required=True,
        label='Nome',
        help_text='Obrigatório.',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu nome'}),
        error_messages={
            'min_length': 'Por favor, adicione mais de 2 letras.'
        }
    )
    last_name = forms.CharField(
        min_length=2,
        max_length=30,
        required=True,
        help_text='Required.'
    )
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
        required=False,
    )
    password2 = forms.CharField(
        label="Password 2",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text='Use the same password as before.',
        required=False,
    )
 
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email',
            'username',
        )

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        user = super().save(commit=False)
        password = cleaned_data.get('password1')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
    
    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 or password2:
            if password1 != password2:
                self.add_error(
                    'password2',
                    ValidationError('Senhas não batem')
                )
        return super().clean()
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        current_email = self.instance.email
        if current_email != email:
            if User.objects.filter(email=email).exists():
                self.add_error(
                    'email',
                    ValidationError('Já existe este e-mail', code='invalid')
                )
        return email
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            try:
                password_validation.validate_password(password1)
            except ValidationError as errors:
                self.add_error(
                    'password1',
                    ValidationError(errors)
                )
        return password1
