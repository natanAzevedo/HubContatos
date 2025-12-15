# Como Configurar Resend para o Render

O Render bloqueia portas SMTP (587/465) por padrão. A solução é usar **Resend**, um serviço moderno de email transacional com API simples e excelente entregabilidade.

## Passo 1: Criar Conta no Resend

1. Acesse: https://resend.com/signup
2. Crie uma conta gratuita (100 emails/dia grátis, 3.000/mês)
3. Verifique seu email

## Passo 2: Adicionar Domínio (Opcional mas Recomendado)

Se você tem um domínio próprio:
1. Vá em **Domains** → **Add Domain**
2. Digite seu domínio (ex: `hubcontatos.com`)
3. Adicione os registros DNS que o Resend mostrar
4. Aguarde verificação (alguns minutos)

**Sem domínio?** Use o domínio de teste: `onboarding@resend.dev` (limitado mas funciona!)

## Passo 3: Criar API Key

1. Faça login no Resend
2. Vá em **API Keys** no menu lateral
3. Clique em **Create API Key**
4. Nome: `HubContatos Render`
5. Permissão: **Sending access**
6. Clique em **Add**
7. **COPIE A CHAVE** (começa com `re_`) — só aparece uma vez!

Exemplo: `re_9iYsNtbq_MkKMNjTY6zJTrEuA2x9aKUAE`

## Passo 4: Configurar no Render

1. No painel do Render, vá no seu Web Service
2. Vá em **Environment**
3. Adicione as variáveis:

```
RESEND_API_KEY=re_SuaChaveAqui
RESEND_FROM_EMAIL=onboarding@resend.dev
DEBUG=False
```

**Se você adicionou seu próprio domínio:**
```
RESEND_FROM_EMAIL=contato@seudominio.com
```

4. Clique em **Save Changes**
5. O Render vai fazer redeploy automaticamente

## Passo 5: Testar

Após o deploy, faça um cadastro no site do Render:
- Acesse: https://agenda-otd0.onrender.com/user/create/
- Preencha o formulário
- O email deve chegar em **segundos**!

## Troubleshooting

**Email não chega?**
- Verifique se a API Key está correta no Render (começa com `re_`)
- Verifique se `RESEND_FROM_EMAIL` é válido
- Confira a caixa de spam
- Veja os logs no Render: `Dashboard → Logs`
- Veja logs no Resend: `Logs` → últimos emails enviados

**Limite excedido?**
- Plano gratuito: 100 emails/dia, 3.000/mês
- Se precisar mais, faça upgrade (planos a partir de $20/mês)

**Domínio não verificado?**
- Use `onboarding@resend.dev` temporariamente
- Verifique os registros DNS no seu provedor
- Aguarde até 24h para propagação (geralmente minutos)

## Vantagens do Resend

✅ API super simples (1 request para enviar)  
✅ Entregabilidade excelente (99%+)  
✅ Logs detalhados em tempo real  
✅ Webhooks para tracking de aberturas/clicks  
✅ Suporte a React Email (templates modernos)  
✅ Dashboard limpo e intuitivo

## Fallback SMTP

Se o Resend falhar, o sistema automaticamente tenta enviar via SMTP Gmail (configurado no `.env`). Isso garante que emails sempre sejam enviados!
