# 🌐 Configuração do Domínio arcsat.com.br

## 📋 Domínios Configurados

- **Frontend**: https://arcsat.com.br (ou https://www.arcsat.com.br)
- **Backend API**: https://api.arcsat.com.br
- **Documentação API**: https://api.arcsat.com.br/docs

---

## 🔧 Configuração DNS

Configure os seguintes registros DNS no seu provedor (Registro.br, Hostgator, etc.):

### Registros A (IPv4):

```
@ (ou arcsat.com.br)        A      [IP do servidor ou Railway]
www                         A      [IP do servidor ou Railway]
api                         A      [IP do servidor backend]
```

### Ou CNAME (para Railway):

```
@                          CNAME   arcsat-frontend.up.railway.app.
www                        CNAME   arcsat-frontend.up.railway.app.
api                        CNAME   arcsat-backend.up.railway.app.
```

**Nota**: Alguns provedores não permitem CNAME no registro raiz (@). Nesse caso, use registro A ou ALIAS.

---

## 🚀 Configuração no Railway

### Para Backend (api.arcsat.com.br):

1. No Railway, acesse o serviço **backend**
2. Vá em **Settings** → **Domains**
3. Click em **+ Custom Domain**
4. Digite: `api.arcsat.com.br`
5. Railway mostrará o CNAME para configurar no DNS

### Para Frontend (arcsat.com.br):

1. No Railway, acesse o serviço **frontend**
2. Vá em **Settings** → **Domains**
3. Click em **+ Custom Domain**
4. Digite: `arcsat.com.br`
5. Configure também: `www.arcsat.com.br`
6. Railway mostrará os CNAMEs para configurar no DNS

---

## 🔒 SSL/HTTPS (Automático)

Railway provisiona certificados SSL **automaticamente** via Let's Encrypt:
- ✅ Gratuito
- ✅ Renovação automática
- ✅ HTTPS forçado

Aguarde 5-10 minutos após configurar o DNS para o SSL ser provisionado.

---

## ✅ Checklist de Configuração

- [ ] Registros DNS criados (A ou CNAME)
- [ ] Domínio adicionado no Railway (backend)
- [ ] Domínio adicionado no Railway (frontend)
- [ ] Aguardar propagação DNS (até 48h, geralmente 1-2h)
- [ ] Verificar SSL ativo (https funcionando)
- [ ] Testar aplicação no domínio
- [ ] Atualizar links/documentação

---

## 🧪 Testar Propagação DNS

```bash
# Verificar DNS do domínio principal
nslookup arcsat.com.br

# Verificar DNS da API
nslookup api.arcsat.com.br

# Verificar www
nslookup www.arcsat.com.br

# Ou usar online:
# https://dnschecker.org
```

---

## 🔄 Redirecionamentos

### www → sem www (ou vice-versa)

Configure no Railway em **Settings** → **Domains**:
- Marque opção para redirecionar `www.arcsat.com.br` → `arcsat.com.br`

### HTTP → HTTPS

Railway força HTTPS automaticamente. Não precisa configurar.

---

## 🆘 Troubleshooting

### DNS não propaga

- Aguarde até 48h (geralmente 1-2h)
- Limpe cache DNS: `ipconfig /flushdns` (Windows)
- Verifique em: https://dnschecker.org

### SSL não ativa

- Verifique se DNS aponta corretamente para Railway
- Aguarde 10-15 minutos após DNS propagar
- Entre em contato com suporte Railway se persistir

### CORS Error

Já configurado no `backend/main.py` para aceitar:
- ✅ arcsat.com.br
- ✅ www.arcsat.com.br
- ✅ HTTP e HTTPS

### API não conecta

Verifique `frontend/src/services/api.ts`:
- URL deve ser: `https://api.arcsat.com.br/api`

---

## 📧 Suporte

- **Railway**: https://railway.app/help
- **Registro.br**: https://registro.br

---

**Domínio configurado com sucesso! 🎉**
