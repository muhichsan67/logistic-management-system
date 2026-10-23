# ALUR Logistik - Frontend

Vue 3 (`<script setup>`) + Vite + Tailwind + Vue Router + Pinia + axios + vite-plugin-pwa.
PrimeVue hanya untuk tabel & dialog Admin. Satu project untuk Customer, Kurir (mobile PWA) dan Admin (desktop).

## Menjalankan
```bash
npm install
cp .env.example .env        # VITE_API_BASE_URL=/api/v1
npm run dev                 # http://localhost:5173  (proxy /api & /static -> http://localhost:8000)
npm run build && npm run preview
```
Backend harus jalan di `localhost:8000` (lihat README backend). Akun seed: `admin@alur.com`, `budi.courier@alur.com`, `eko.customer@gmail.com`.

## Produksi
- Layani `dist/` dari domain yang sama dengan API, dan teruskan `/api` **dan `/static`** (foto bukti) ke backend.
- Atau set `VITE_API_BASE_URL=https://api.contoh.com/api/v1` dan tambahkan origin frontend ke `CORS_ORIGINS` backend.

## Struktur
```
src/
├── main.js, App.vue, style.css
├── router/index.js     route + guard login/role (meta.roles)
├── stores/auth.js      satu-satunya store: token, refresh token, role, nama
├── api/http.js         axios, Bearer, auto-refresh token (rotation), error handler
├── api/index.js        semua fungsi API
├── layouts/            MobileLayout (Customer & Kurir), AdminLayout
├── components/         StatusBadge, TrackingTimeline, Loading/Empty/ErrorState, FormField, ...
├── views/              auth, public, customer, courier, admin
└── utils/              format, validate, useAsync, toast, online, image, push, session
```

## Catatan
- Notifikasi: izin diminta setelah aksi pertama (buat pengiriman). Pengiriman Web Push butuh endpoint subscribe di backend (belum ada).
- Service worker hanya cache file statis; data API tidak di-cache.
