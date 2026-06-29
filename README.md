# Brazilian E-commerce Data Platform

Olist (Brezilya e-ticaret) veri seti üzerine kurulu, uçtan uca bir veri platformu.
Amaç: ham CSV verisini → PostgreSQL'e yükleyip → dbt ile temizleyip → API ile sunmak.

Veri seti: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

## Mimari (Medallion: Bronze → Silver → Gold)

```
brazilian-ecommerce-data-platform/
├── docker-compose.yml   # Tüm servisleri (PostgreSQL vb.) tek komutla ayağa kaldırır
├── data/                # İndirilen CSV dosyaları burada durur
├── ingestion/           # CSV'yi PostgreSQL'e yükleyen Python scriptleri (Bronze)
├── dbt/                 # dbt projesi — Silver + Gold modelleri, testler
├── api/                 # FastAPI — Gold metriklerini sunan REST endpoint (ileride)
├── .env                 # Veritabanı bağlantı bilgileri
├── .gitignore
└── README.md
```

İleride eklenecek: `airflow/` (orkestrasyon) · `kafka/` (streaming) · `spark/` (büyük veri işleme)

## Başlangıç

```bash
# 1. PostgreSQL'i ayağa kaldır
docker compose up -d

# 2. Çalışıyor mu kontrol et
docker compose ps
```

## Yol Haritası

- [x] Proje iskeleti ve docker-compose (PostgreSQL)
- [x] `data/` — Kaggle'dan CSV'leri indir
- [x] `ingestion/` — CSV → PostgreSQL (Bronze katman)
- [x] `dbt/` — Silver staging modelleri (`stg_*`) + source tanımları
- [x] `dbt/` — Gold modeli (`fct_orders` — sipariş bazlı metrikler)
- [ ] `dbt/` — Ek Gold modelleri + testler
- [ ] `api/` — FastAPI ile Gold metrik endpoint'leri
