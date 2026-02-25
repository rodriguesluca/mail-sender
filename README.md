<div align="center">
  <img src="https://raw.githubusercontent.com/feathericons/feather/master/icons/send.svg" width="60" alt="Logo">
  <h1>🚀 MailSender · SMTP Tester & API</h1>
  <p><strong>Smart & Secure Asynchronous Email Dispatch Architecture</strong></p>
</div>

---

Um microsserviço completo, robusto e escalável para disparo assíncrono de e-mails, construído sobre **FastAPI**, **Celery**, **Redis** e **Docker**. Além da API REST poderosa preparada para ser consumida por microsserviços e automações (como Power Automate), inclui um elegante **Painel Visul (Web UI)** que atua como um avançado **SMTP Tester**, suportando configurações seguras e dinâmicas de conexão, totalmente desacoplado.

### ✨ Highlights & Features

- ⚡ **Alta Performance (Assíncrona):** Recebe requisições via FastAPI e delega o processamento pesado de SMTP para _Workers_ em background usando o **Celery**.
- 🛠️ **Painel Web (SMTP Tester):** Interface lindíssima e interativa (Glassmorphism), permitindo testar disparos inserindo Host, Porta, Segurança (TLS) e anexo dinamicamente sem alterar código.
- 🔐 **Segurança via Fernet:** Senhas reais de SMTP não trafegam em texto puro pelas APIs públicas. O frontend contém um utilitário nativo onde você converte sua Raw Password em um **Encrypted Token** usando uma `MASTER_KEY`. Apenas o Worker isolado descriptografa o Token no último milissegundo antes de autenticar.
- 📊 **Monitoramento em Tempo Real:** Stack nativamente integrada ao **Flower**, garantindo um painel gráfico para fiscalizar as filas do Redis, métricas de envio, retentativas e falhas.
- 🐳 **Plug and Play:** Infraestrutura conteinerizada (`docker-compose`) que levanta Servidor Web, Workers, Cache e Monitoramento em um só pacote.
- 🔗 **Suporte a Anexos:** Conversão automática de anexos usando codificação **Base64** padronizada por APIs escaláveis.

---

## 🏗️ Arquitetura e Stack

<div style="display: flex; gap: 10px; margin-bottom: 20px;">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white" alt="Celery">
  <img src="https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white" alt="Redis">
  <img src="https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="Python">
</div>

1. **API (Web Container):** FastAPI recebe o Payload (`/send-email/`) gerando validação de segurança via _Pydantic_, empurrando a tarefa à fila do Redis e retornando `202 Accepted` de forma quase imediata pro cliente/automação.
2. **Worker (Broker/Consumer):** Celery vigia o Redis, puxa a tarefa, desencripta a credencial fornecida via variável global restrita e faz o IO Blocking do envio SMTP e anexos.
3. **Flower (Monitor):** Interface na porta `5555` lendo os states (`SUCCESS`, `RETRY`, `FAILURE`) do broker para dar rastreabilidade.

---

## 🛠️ Como Iniciar (Quickstart)

### 1. Clonar e Configurar Variáveis

Clone o projeto e prepare as variáveis. A aplicação usa um segredo (Master Key) para criar os Tokens das suas credenciais com o pacote `cryptography`.

```bash
git clone https://github.com/SeuUsuario/MailSender.git
cd MailSender
```

Lá dentro, edite ou crie o `.env`:

```env
# URL do Redis para a comunicação do Celery
CELERY_BROKER_URL=redis://redis:6379/0

# (Obrigatório) Chave Mestre de 32 bits codificada Base64 exigida pelo Fernet
# Você pode gerar uma teclando em Python:
# from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())
ENCRYPTION_KEY="sua_chave_secreta_aqui"
```

### 2. Rodar pelo Docker (Recomendado)

Um único comando orquestra e sobe todas as 4 peças da aplicação (Redis, Worker, API, Flower). Em Wsl2 ou Docker Desktop, basta executar:

```bash
docker-compose up --build -d
```

### 3. Serviços Acessíveis

| Serviço                | URL Local                    | Descrição                                           |
| ---------------------- | ---------------------------- | --------------------------------------------------- |
| **Painel / Tester UI** | `http://localhost:8000/`     | Dashboard Web e Ferramenta Criptográfica p/ Senhas. |
| **API Docs (Swagger)** | `http://localhost:8000/docs` | Testar Endpoints via requisição direta documentada. |
| **Flower Monitor**     | `http://localhost:5555/`     | Observar tempo de execução, retry e fila do Celery. |

---

## 📡 Endpoints (API)

Caso pretenda injetar o MailSender como integrador (ex: Power Automate), dispare um `POST` para `/send-email/` utilizando o seguinte JSON Body:

#### `POST /send-email/`

```json
{
  "to_email": ["client1@domain.com", "partner2@domain.com"],
  "cc_email": ["manager@domain.com"],
  "subject": "System Warning - MailSender",
  "body": "This is a scalable automated email.",
  "smtp_user": "your_robot@smtpdomain.com",
  "smtp_password": "gAAAAABp1A...", // O Token criptografado
  "smtp_host": "smtp.office365.com",
  "smtp_port": 587,
  "smtp_tls": true,
  "attachment_base64": "SGVsbG8gV29ybGQ=", // Opcional (Bytes Base 64)
  "attachment_filename": "hello.txt" // Obrigatório de houver anexo
}
```

> ⚠️ Assegure que as chaves de Encriptação (`ENCRYPTION_KEY`) presentes no Servidor destino baterão exatamente com a usada na hora de Gerar o Token que você enviou.

---

## 👨‍💻 Fluxo do Desenvolvedor

### Lidando com Certificados e SMTPs Empresariais

Caso no Docker ele sofra _Timeouts DNS_ internos para enxergar o Office365 ou Google (comum no sub-layer do Docker no Windows/WSL2), nós injetamos DNS públicos limpos `[8.8.8.8]` no arquivo de manifesto do Compose que soluciona o erro silencioso.

### Criptografando Rapidamente

Se você possui um novo SMTP e precisa engarrafar a senha em um Token sem precisar entrar no painel visual:

1. Abra um Curl: `curl -X POST http://localhost:8000/encrypt/ -H "Content-Type: application/json" -d "{\"raw_password\":\"suasenha123\"}"`
2. Resposta: `{"encrypted_token": "gAAAAAB..."}`

---
