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
import threading
import resend

def send_email_resend(subject, message, to_email):
    """Envia email usando Resend API ou SMTP"""
    # Tenta usar Resend se tiver API key configurada
    resend_key = getattr(settings, 'RESEND_API_KEY', '')
    
    if resend_key and not settings.DEBUG:
        try:
            resend.api_key = resend_key
            from_email = getattr(settings, 'RESEND_FROM_EMAIL', 'onboarding@resend.dev')
            resend.Emails.send({
                "from": from_email,
                "to": to_email,
                "subject": subject,
                "html": f"<div style='font-family: Arial, sans-serif; white-space: pre-wrap;'>{message}</div>"
            })
            print(f"[DEBUG] Email enviado via Resend para {to_email}")
            return True
        except Exception as e:
            print(f"[ERRO] Falha no Resend, tentando SMTP: {e}")
    
    # Fallback: SMTP
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
        print(f"[DEBUG] Email enviado via SMTP para {to_email}")
        return True
    except Exception as e:
        print(f"[ERRO] Falha ao enviar email: {e}")
        return False

def register(request):
    form = RegisterForm()
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            # Salva dados temporariamente na sessão (NÃO cria usuário ainda)
            user_data = {
                'username': form.cleaned_data['username'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password1'],
            }
            request.session['pending_user'] = user_data
            print(f"[DEBUG] Dados salvos na sessão para {user_data['email']} - NÃO CRIOU USUÁRIO")
            
            # Gera código de verificação
            code = EmailVerification.generate_code()
            expires_at = timezone.now() + timedelta(hours=24)
            
            # Salva o código no banco (sem usuário)
            verification = EmailVerification.objects.create(
                email=user_data['email'],
                code=code,
                expires_at=expires_at
            )
            
            # Função para enviar email
            def send_verification_email():
                email_message = f'''Olá {user_data['first_name']}!

Bem-vindo ao HubContatos! 

Seu código de verificação é: {code}

Este código expira em 24 horas.

Se você não solicitou este cadastro, ignore este email.

Atenciosamente,
Equipe HubContatos'''
                send_email_resend(
                    subject='HubContatos - Verifique seu email',
                    message=email_message,
                    to_email=user_data['email']
                )
            
            # Em produção (Render), usa thread para não bloquear worker
            if not settings.DEBUG:
                email_thread = threading.Thread(target=send_verification_email)
                email_thread.daemon = True
                email_thread.start()
            else:
                # Em desenvolvimento, envia síncrono para facilitar debug
                send_verification_email()
            
            # Redireciona imediatamente sem esperar o email
            messages.success(request, f'Enviamos um código de verificação para {user_data["email"]}')
            return redirect('contact:verify_email')

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


def verify_email(request):
    """View para verificação de email"""
    # Recupera dados temporários da sessão
    user_data = request.session.get('pending_user')
    
    if not user_data:
        messages.error(request, 'Sessão expirada. Por favor, faça o cadastro novamente.')
        return redirect('contact:register')
    
    # Busca verificação pendente
    try:
        verification = EmailVerification.objects.filter(
            email=user_data['email'],
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
                # AGORA SIM cria o usuário no banco
                User = auth.get_user_model()
                print(f"[DEBUG] CRIANDO USUÁRIO NO BANCO: {user_data['username']} / {user_data['email']}")
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    is_active=True
                )
                print(f"[DEBUG] USUÁRIO CRIADO COM SUCESSO: ID={user.id}")
                
                # Limpa dados temporários da sessão
                del request.session['pending_user']
                
                messages.success(request, 'Email verificado! Cadastro concluído com sucesso.')
                return redirect('contact:login')
            else:
                messages.error(request, message)
    
    return render(
        request,
        'contact/verify_email.html',
        {
            'form': form,
            'user_email': user_data['email'],
        }
    )


def resend_verification_code(request):
    """Reenvia código de verificação"""
    user_data = request.session.get('pending_user')
    
    if not user_data:
        messages.error(request, 'Sessão expirada. Por favor, faça o cadastro novamente.')
        return redirect('contact:register')
    
    # Invalida códigos anteriores
    EmailVerification.objects.filter(email=user_data['email'], is_verified=False).update(is_verified=True)
    
    # Gera novo código
    code = EmailVerification.generate_code()
    expires_at = timezone.now() + timedelta(hours=24)
    
    verification = EmailVerification.objects.create(
        email=user_data['email'],
        code=code,
        expires_at=expires_at
    )
    
    # Função para enviar email
    def send_resend_email():
        email_message = f'''Olá {user_data['first_name']}!

Você solicitou um novo código de verificação.

Seu novo código é: {code}

Este código expira em 24 horas.

Atenciosamente,
Equipe HubContatos'''
        send_email_resend(
            subject='HubContatos - Novo código de verificação',
            message=email_message,
            to_email=user_data['email']
        )
    
    # Em produção (Render), usa thread para não bloquear worker
    if not settings.DEBUG:
        email_thread = threading.Thread(target=send_resend_email)
        email_thread.daemon = True
        email_thread.start()
    else:
        # Em desenvolvimento, envia síncrono
        send_resend_email()
    
    messages.success(request, f'Novo código enviado para {user_data["email"]}')
    return redirect('contact:verify_email')