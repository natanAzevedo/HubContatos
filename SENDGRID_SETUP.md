# Como Configurar SendGrid para o Render

O Render bloqueia portas SMTP (587/465) por padrão. A solução é usar SendGrid, um serviço gratuito de email transacional.

## Passo 1: Criar Conta no SendGrid

1. Acesse: https://signup.sendgrid.com/
2. Crie uma conta gratuita (100 emails/dia grátis)
3. Verifique seu email

## Passo 2: Criar API Key

1. Faça login no SendGrid
2. Vá em **Settings** → **API Keys**
3. Clique em **Create API Key**
4. Nome: `HubContatos Render`
5. Permissões: **Full Access** (ou apenas "Mail Send")
6. Clique em **Create & View**
7. **COPIE A CHAVE** (só aparece uma vez!)

## Passo 3: Verificar Sender Identity

1. Vá em **Settings** → **Sender Authentication**
2. Escolha **Single Sender Verification**
3. Preencha com:
   - From Name: `HubContatos`
   - From Email: `agendacontatosite@gmail.com`
   - Reply To: `agendacontatosite@gmail.com`
4. Verifique o email que o SendGrid enviar para `agendacontatosite@gmail.com`

## Passo 4: Configurar no Render

1. No painel do Render, vá no seu Web Service
2. Vá em **Environment**
3. Adicione as variáveis:

```
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=agendacontatosite@gmail.com
DEBUG=False
```

4. Clique em **Save Changes**
5. O Render vai fazer redeploy automaticamente

## Passo 5: Testar

Após o deploy, faça um cadastro no site do Render:
- Acesse: https://agenda-otd0.onrender.com/user/create/
- Preencha o formulário
- O email deve chegar em segundos!

## Troubleshooting

**Email não chega?**
- Verifique se a API Key está correta no Render
- Verifique se verificou o Sender no SendGrid
- Confira a caixa de spam
- Veja os logs no Render: `Dashboard → Logs`

**Limite excedido?**
- Plano gratuito: 100 emails/dia
- Se precisar mais, faça upgrade no SendGrid

## Alternativas ao SendGrid

Se preferir outros serviços:
- **Mailgun**: https://www.mailgun.com/ (100 emails/dia grátis)
- **AWS SES**: https://aws.amazon.com/ses/ (62.000 emails/mês grátis)
- **Resend**: https://resend.com/ (100 emails/dia grátis)
