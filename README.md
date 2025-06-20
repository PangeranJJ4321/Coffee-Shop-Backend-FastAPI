# ☕ Coffee Shop Backend

> **Aplikasi backend modern untuk Coffee Shop** - Dibangun dengan FastAPI, SQLAlchemy, dan PostgreSQL

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)

---

## 📋 Daftar Isi

- [✨ Fitur Utama](#-fitur-utama)
- [🛠️ Teknologi yang Digunakan](#️-teknologi-yang-digunakan)
- [📋 Persyaratan Sistem](#-persyaratan-sistem)
- [🚀 Quick Start](#-quick-start)
- [⚙️ Setup Lingkungan](#️-setup-lingkungan)
- [🗄️ Konfigurasi Database](#️-konfigurasi-database)
- [📚 Dokumentasi API](#-dokumentasi-api)
- [👨‍💼 Admin Panel](#-admin-panel)
- [🧪 Testing](#-testing)
- [📁 Struktur Proyek](#-struktur-proyek)
- [🤝 Kontribusi](#-kontribusi)
- [📄 Lisensi](#-lisensi)

---

## ✨ Fitur Utama

### 👥 **Manajemen Pengguna**
- 🔐 Pendaftaran & Login dengan JWT Authentication
- 👤 Manajemen profil pengguna
- 🛡️ Role-based access control (User, Admin)

### ☕ **Manajemen Menu Kopi**
- 📝 CRUD operasi untuk item menu
- 🖼️ Upload gambar dengan Supabase Storage
- 🏷️ Kategori dan tags untuk organisasi menu
- 📋 Deskripsi detail untuk setiap item

### 🎛️ **Sistem Varian Kopi**
- 📏 Tipe varian (Ukuran, Tingkat Gula, dll.)
- ⚙️ Varian individual (Small, Medium, No Sugar, dll.)
- 🔗 Koneksi fleksible antara kopi dan varian

### 🛒 **Manajemen Pesanan**
- 📦 Pembuatan dan tracking pesanan
- 📜 Riwayat lengkap pesanan
- ❌ Pembatalan pesanan
- 📊 Status tracking real-time

### 💳 **Sistem Pembayaran**
- 🏦 Integrasi Midtrans Gateway
- 📱 QRIS dan metode pembayaran lainnya
- 🤝 Fitur "Bayar untuk Orang Lain"
- 🧾 Riwayat transaksi lengkap

### 📧 **Notifikasi & Komunikasi**
- ✉️ Email otomatis untuk status pesanan
- 📨 Template email dengan Jinja2
- 🔔 Notifikasi real-time

### 📊 **Dashboard Admin**
- 👥 Manajemen user CRUD
- 📈 Analitik penjualan
- 📊 Statistik produk terlaris
- 📋 Overview performa bisnis

---

## 🛠️ Teknologi yang Digunakan

| Kategori | Teknologi | Versi | Deskripsi |
|----------|-----------|--------|-----------|
| **Framework** | FastAPI | Latest | Modern Python web framework |
| **Database** | PostgreSQL | 13+ | Robust relational database |
| **ORM** | SQLAlchemy | 2.0+ | Python SQL toolkit |
| **Migration** | Alembic | Latest | Database migration tool |
| **Validation** | Pydantic | V2 | Data validation library |
| **Authentication** | JWT | Latest | JSON Web Token |
| **Storage** | Supabase | Latest | File storage solution |
| **Payment** | Midtrans | Latest | Payment gateway |
| **Email** | SMTPLib + Jinja2 | Latest | Email templating |
| **Testing** | Pytest | Latest | Testing framework |
| **Server** | Uvicorn | Latest | ASGI web server |

---

## 📋 Persyaratan Sistem

- 🐍 **Python 3.9+**
- 🗄️ **PostgreSQL 13+**
- 🌐 **Akses Supabase** (database & storage)
- 💳 **Akun Midtrans Sandbox** (untuk development)
- 📧 **Akun Mailtrap** (opsional, untuk testing email)

---

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/PangeranJJ4321/Coffee-Shop-Backend-FastAPI
cd Coffee-Shop-Backend-FastAPI

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# atau venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env dengan konfigurasi Anda

# Setup database
createdb coffee_shop_db
alembic upgrade head

# Run application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

🎉 **Selamat!** Aplikasi Anda sekarang berjalan di `http://localhost:8000`

---

## ⚙️ Setup Lingkungan

### 1️⃣ **Clone Repository**
```bash
git clone <URL_REPOSITORY_ANDA>
cd coffee-shop-backend
```

### 2️⃣ **Setup Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# atau
venv\Scripts\activate   # Windows
```

### 3️⃣ **Install Dependencies**
```bash
pip install -r requirements.txt
```

> **💡 Tip:** Jika `requirements.txt` belum ada, install manual lalu generate:
> ```bash
> pip install fastapi uvicorn "python-dotenv[dotenv]" sqlalchemy psycopg2-binary pydantic alembic passlib[bcrypt] python-jose[cryptography] httpx requests python-multipart supabase jinja2
> pip freeze > requirements.txt
> ```

### 4️⃣ **Konfigurasi Environment Variables**

Buat file `.env` di root proyek dengan konfigurasi berikut:

```env
# 🗄️ Database Configuration
DATABASE_URL="postgresql://postgres:password@localhost:5432/coffee_shop_db"

# 🔐 JWT Configuration
SECRET_KEY="your_super_secret_jwt_key_here_at_least_32_chars_long"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 🌐 Supabase Configuration
SUPABASE_URL="https://your-project-id.supabase.co"
SUPABASE_KEY="your_supabase_anon_key"
SUPABASE_SERVICE_KEY="your_supabase_service_role_key"

# 💳 Midtrans Configuration (Sandbox)
MIDTRANS_SANDBOX=True
MIDTRANS_CLIENT_KEY="SB-Mid-client-XXXXXX"
MIDTRANS_SERVER_KEY="SB-Mid-server-YYYYYY:"

# 📧 Email Configuration (Mailtrap for development)
EMAILS_FROM_EMAIL="noreply@coffeeshop.com"
EMAILS_FROM_NAME="Coffee Shop Admin"
MAILTRAP_HOST="smtp.mailtrap.io"
MAILTRAP_PORT=2525
MAILTRAP_USERNAME="your_mailtrap_username"
MAILTRAP_PASSWORD="your_mailtrap_password"

# 🌐 Base URL
BASE_URL="http://localhost:8000/api/v1"
```

> **⚠️ Penting:** Untuk `SECRET_KEY`, gunakan string acak yang kuat:
> ```bash
> openssl rand -hex 32  # Linux/macOS
> ```

---

## 🗄️ Konfigurasi Database

### **Setup PostgreSQL**
```bash
# Buat database baru
psql -U postgres
CREATE DATABASE coffee_shop_db;
\q
```

### **Jalankan Migrasi**
```bash
# Generate migrasi awal (jika belum ada)
alembic revision --autogenerate -m "Initial migration"

# Jalankan semua migrasi
alembic upgrade head
```

### **Seeding Data (Opsional)**
Data seed akan otomatis dijalankan saat migrasi jika sudah dikonfigurasi.

---

## 📚 Dokumentasi API

FastAPI menyediakan dokumentasi API otomatis yang interaktif:

| Dokumentasi | URL | Deskripsi |
|------------|-----|-----------|
| **Swagger UI** | `http://localhost:8000/docs` | Dokumentasi interaktif lengkap |
| **ReDoc** | `http://localhost:8000/redoc` | Dokumentasi bergaya ReDoc |

### **API Endpoints Overview**

```
📁 Authentication
├── POST /api/v1/auth/register
├── POST /api/v1/auth/login
└── GET  /api/v1/auth/me

📁 Menu Management
├── GET    /api/v1/menu/
├── POST   /api/v1/menu/
├── GET    /api/v1/menu/{id}
├── PUT    /api/v1/menu/{id}
└── DELETE /api/v1/menu/{id}

📁 Orders
├── GET  /api/v1/orders/
├── POST /api/v1/orders/
└── GET  /api/v1/orders/{id}

📁 Payments
├── POST /api/v1/payments/create
└── POST /api/v1/payments/notification
```

---

## 👨‍💼 Admin Panel

> **🔒 Akses Terbatas:** Semua endpoint admin memerlukan role `ADMIN`

### **User Management**
- `GET /api/v1/admin/user-management/users` - List semua user
- `PUT /api/v1/admin/user-management/users/{id}` - Update user
- `DELETE /api/v1/admin/user-management/users/{id}` - Hapus user

### **Menu Management**
- `GET /api/v1/admin/menu-management/menu` - Kelola menu
- `GET /api/v1/admin/menu-management/variant-types` - Kelola tipe varian
- `GET /api/v1/admin/menu-management/variants` - Kelola varian
- `GET /api/v1/admin/menu-management/coffee-variants` - Kelola koneksi kopi-varian

### **Order Management**
- `GET /api/v1/admin/order-management/orders` - Kelola pesanan
- `PUT /api/v1/admin/order-management/orders/{id}/status` - Update status

### **Analytics Dashboard**
- `GET /api/v1/admin/analytics/dashboard/summary` - Ringkasan dashboard
- `GET /api/v1/admin/analytics/sales` - Analitik penjualan
- `GET /api/v1/admin/analytics/products` - Produk terlaris

---

## 🧪 Testing

Jalankan test suite menggunakan pytest:

```bash
# Jalankan semua test
pytest

# Jalankan dengan coverage
pytest --cov=app

# Jalankan test spesifik
pytest tests/test_auth.py
```

---

## 📁 Struktur Proyek

```
coffee-shop-backend/
│
├── 📁 app/                          # Source code utama
│   ├── 📁 api/                      # API endpoints & routers
│   │   ├── 📁 endpoints/            # Endpoint entitas utama
│   │   ├── 📁 admin/                # Admin-only endpoints
│   │   └── __init__.py
│   ├── 📁 controllers/              # Business logic orchestration
│   ├── 📁 core/                     # Core configurations
│   │   ├── config.py                # App settings
│   │   ├── database.py              # Database connection
│   │   └── security.py              # Auth & security
│   ├── 📁 models/                   # SQLAlchemy models
│   ├── 📁 repositories/             # Database access layer
│   ├── 📁 schemas/                  # Pydantic schemas
│   ├── 📁 services/                 # Business logic services
│   ├── 📁 utils/                    # Utility functions
│   └── main.py                      # FastAPI app entry point
│
├── 📁 alembic/                      # Database migrations
├── 📁 tests/                        # Test suite
├── 📄 .env.example                  # Environment template
├── 📄 .env                          # Environment variables (git-ignored)
├── 📄 requirements.txt              # Python dependencies
├── 📄 README.md                     # Project documentation
└── 📄 .gitignore                    # Git ignore rules
```

---

## 🤝 Kontribusi

Kami sangat menghargai kontribusi Anda! Berikut cara berkontribusi:

1. **🍴 Fork** repository ini
2. **🌿 Buat branch** untuk fitur Anda (`git checkout -b feature/AmazingFeature`)
3. **✅ Commit** perubahan Anda (`git commit -m 'Add some AmazingFeature'`)
4. **📤 Push** ke branch (`git push origin feature/AmazingFeature`)
5. **🔄 Buat Pull Request**

### **📋 Guidelines Kontribusi**
- Ikuti standar koding Python (PEP 8)
- Tambahkan test untuk fitur baru
- Update dokumentasi jika diperlukan
- Pastikan semua test pass sebelum PR

---

## 📄 Lisensi

Proyek ini dilisensikan dengan **MIT License** - lihat file [LICENSE](LICENSE) untuk detail lengkap.

---

## 📞 Dukungan

Jika Anda mengalami masalah atau memiliki pertanyaan:

- 🐛 **Bug Reports:** [Issues](https://github.com/yourusername/coffee-shop-backend/issues)
- 💡 **Feature Requests:** [Discussions](https://github.com/yourusername/coffee-shop-backend/discussions)
- 📧 **Email:** pangeranjuhrifar@gmail.com

---

<div align="center">

**Dibuat dengan ❤️ untuk Coffee Shop Backend**

[![⭐ Star this repo](https://img.shields.io/github/stars/PangeranJJ4321/Coffee-Shop-Backend-FastAPI?style=social)](https://github.com/PangeranJJ4321/Coffee-Shop-Backend-FastAPI)

</div>
