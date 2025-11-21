# Pro RAG Sistemi (v2.2 - OpenRouter Destekli)

Bu sürüm, **Pinecone**, **OpenAI Embedding** ve **OpenRouter** (Grok, Gemini, Claude vb.) desteği sunar.

## 🚀 Güncellenen Kurulum Talimatları

### 1. API Anahtarları (ZORUNLU)
Bu sistemin çalışması için gerekli anahtarlar:

1.  **OPENAI_API_KEY:** (Embedding işlemleri için hala gerekli - Backend ve Worker)
2.  **PINECONE_API_KEY:** (Vektör veritabanı için - Backend ve Worker)
3.  **OPENROUTER_API_KEY:** (Sohbet sırasında Gemini, Grok, Claude vb. kullanmak için - Backend)

### 2. Backend (Render) Kurulumu
Render'da Environment Variables kısmına şunları ekleyin:
*   `OPENAI_API_KEY`: sk-proj-...
*   `PINECONE_API_KEY`: pc-...
*   `OPENROUTER_API_KEY`: sk-or-... (OpenRouter anahtarınız)
*   `GOOGLE_DRIVE_CLIENT_ID` ve `SECRET`: (Dosyalar için)

### 3. Local Worker Kurulumu
Bilgisayarınızda terminali açın ve worker'ı başlatın (Worker sadece embedding yaptığı için OpenRouter anahtarına ihtiyaç duymaz, ama OpenAI anahtarına duyar):

**Windows (PowerShell):**
```powershell
$env:BACKEND_URL="https://sizin-render-app.onrender.com"
$env:PINECONE_API_KEY="pc-..."
$env:OPENAI_API_KEY="sk-proj-..."
python worker_local.py
```

---

## 🧠 Desteklenen Modeller

Web arayüzünden artık şunları seçebilirsiniz:

*   **OpenAI:** GPT-4o, GPT-3.5
*   **OpenRouter:**
    *   Google Gemini Pro 1.5
    *   Anthropic Claude 3 Opus / Sonnet
    *   Meta Llama 3 70B
    *   X.AI Grok (Erişim varsa)
*   **Ollama:** Yerel modeller (Llama 3, Mistral)

## ❓ Embedding için neden hala OpenAI?
Sorgu kalitesi için "Embedding Modeli" ile "Sohbet Modeli" ayrılmıştır.
*   Verileri anlamlandırmak (Vektör) için en stabil olan **OpenAI text-embedding-3-small** kullanıyoruz.
*   Cevabı yazdırmak (Chat) için istediğiniz modeli (**Grok, Gemini, Claude**) seçebilirsiniz.
