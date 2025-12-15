from django.shortcuts import redirect, render, get_object_or_404
from contact.forms import RegisterForm, EmailVerificationForm
from django.contrib import messages
from contact.forms import RegisterUpdateForm
from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from contact.models import EmailVerification
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

def register(request):
    form = RegisterForm()
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            # Salva o usuário como inativo
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            
            # Gera código de verificação
            code = EmailVerification.generate_code()
            expires_at = timezone.now() + timedelta(hours=24)
            
            # Salva o código no banco
            verification = EmailVerification.objects.create(
                user=user,
                code=code,
                expires_at=expires_at
            )
            
            # Envia email com o código
            try:
                send_mail(
                    subject='HubContatos - Verifique seu email',
                    message=f'''Olá {user.first_name}!

Bem-vindo ao HubContatos! 

Seu código de verificação é: {code}

Este código expira em 24 horas.

Se você não solicitou este cadastro, ignore este email.

Atenciosamente,
Equipe HubContatos''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                messages.success(request, f'Cadastro realizado! Enviamos um código de verificação para {user.email}')
                return redirect('contact:verify_email', user_id=user.id)
            except Exception as e:
                user.delete()
                messages.error(request, f'Erro ao enviar email. Tente novamente.')
                print(f"Erro ao enviar email: {e}")

    return render(
        request,
        'contact/register.html',{
            'form':form
        }
    )

@login_required(login_url='contact:login')
def user_update(request):
    form = RegisterUpdateForm(instance=request.user)

    if request.method != 'POST':
        return render(
        request,
        'contact/register.html',
        {
            'form':form,
        }
    )

    form = RegisterUpdateForm(data=request.POST, instance=request.user)

    if not form.is_valid():
        return render(
        request,
        'contact/user_update.html',
        {
            'form':form,
        }
    )

    form.save()  
    return redirect('contact:user_update')

  



def login_view(request):
    form = AuthenticationForm(request)

    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)

        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            messages.success(request, 'Logado com sucesso!')
            return redirect('contact:index')
        messages.error(request, 'Login inválido')

    return render(
        request,
        'contact/login.html',{
            'form':form
        }
    )

@login_required(login_url='contact:login')
def logout_view(request):
    auth.logout(request)
    return redirect('contact:login')


def verify_email(request, user_id):
    """View para verificação de email"""
    user = get_object_or_404(auth.get_user_model(), id=user_id)
    
    # Se o usuário já está ativo, redireciona para o login
    if user.is_active:
        messages.info(request, 'Este email já foi verificado. Faça login.')
        return redirect('contact:login')
    
    # Busca verificação pendente
    try:
        verification = EmailVerification.objects.filter(
            user=user,
            is_verified=False
        ).latest('created_at')
    except EmailVerification.DoesNotExist:
        messages.error(request, 'Código de verificação não encontrado.')
        return redirect('contact:register')
    
    form = EmailVerificationForm()
    
    if request.method == 'POST':
        form = EmailVerificationForm(request.POST)
        
        if form.is_valid():
            code = form.cleaned_data['code']
            success, message = verification.verify(code)
            
            if success:
                messages.success(request, message)
                return redirect('contact:login')
            else:
                messages.error(request, message)
    
    return render(
        request,
        'contact/verify_email.html',
        {
            'form': form,
            'user_email': user.email,
            'user_id': user_id,
            'user_public_id': getattr(user, 'profile').public_id if hasattr(user, 'profile') else None,
        }
    )


def resend_verification_code(request, user_id):
    """Reenvia código de verificação"""
    user = get_object_or_404(auth.get_user_model(), id=user_id)
    
    if user.is_active:
        messages.info(request, 'Este email já foi verificado.')
        return redirect('contact:login')
    
    # Invalida códigos anteriores
    EmailVerification.objects.filter(user=user, is_verified=False).update(is_verified=True)
    
    # Gera novo código
    code = EmailVerification.generate_code()
    expires_at = timezone.now() + timedelta(hours=24)
    
    verification = EmailVerification.objects.create(
        user=user,
        code=code,
        expires_at=expires_at
    )
    
    # Envia email
    try:
        send_mail(
            subject='HubContatos - Novo código de verificação',
            message=f'''Olá {user.first_name}!

Você solicitou um novo código de verificação.

Seu novo código é: {code}

Este código expira em 24 horas.

Atenciosamente,
Equipe HubContatos''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        messages.success(request, f'Novo código enviado para {user.email}')
    except Exception as e:
        messages.error(request, 'Erro ao enviar email. Tente novamente.')
        print(f"Erro ao enviar email: {e}")
    
    return redirect('contact:verify_email', user_id=user_id)