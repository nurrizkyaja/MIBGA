# MultiPath Island-Based Genetic Algorithm for the K-Most Diverse Near-Shortest Paths

**MIBGA** adalah implementasi Python untuk menyelesaikan masalah *K-Most Diverse Near-Shortest Paths* (KMDNSP) pada jaringan jalan (road networks). Proyek ini menggunakan **Island-Model Genetic Algorithm** untuk menemukan sekumpulan rute alternatif yang tidak hanya pendek (optimal), tetapi juga memiliki keragaman spasial (dissimilarity) yang tinggi satu sama lain.

Sistem ini dirancang untuk bekerja dengan data jaringan jalan dalam format Excel, CSV, atau Edgelist dan menyediakan visualisasi interaktif menggunakan **Plotly**.

## 🌟 Fitur Utama

  * **Island Model GA:** Menggunakan populasi terdistribusi (islands) dengan mekanisme migrasi untuk mencegah konvergensi dini dan menjaga keragaman genetik.
  * **LFPC Operators:** Mengimplementasikan *Loop-Free Path-Composer* (LFPC) untuk Crossover dan Mutasi, memastikan setiap solusi jalur yang dihasilkan valid dan bebas dari *loop*.
  * **Path Mending:** Mekanisme otomatis untuk memperbaiki jalur yang tidak valid atau memiliki putaran (cycle).
  * **Diversity Metric:** Menggunakan metrik dissimilarity berbasis panjang irisan (intersection) dan gabungan (union) edge.
  * **Visualisasi Interaktif:** Menampilkan peta jaringan, jalur kandidat, dan jalur solusi akhir menggunakan Plotly.
  * **Support Multi-Format:** Mendukung input data berupa `.xlsx`, `.csv`, dan `.edgelist`.

## 📂 Struktur Direktori

```text
MIBGA/
│
├── data/                 # Folder untuk menyimpan dataset (Excel/CSV)
│   ├── arizona.xlsx
│   └── ...
├── analysis.py           # Logika perhitungan dissimilarity & seleksi K jalur terbaik
├── graph_handler.py      # Modul loading graf dan operasi NetworkX
├── island.py             # Logika manajemen populasi (Island Model)
├── main.py               # Entry point aplikasi (CLI & Visualisasi)
├── mibga.py              # Algoritma utama MIBGA (Loop evolusi)
├── operators.py          # Operator genetika (LFPC Crossover & Mutation)
├── path_solution.py      # Struktur data individu jalur (Path)
├── requirements.txt      # Daftar dependensi Python
└── README.md             # Dokumentasi proyek
```

## ⚙️ Instalasi

Pastikan Anda telah menginstal **Python 3.8+**.

1.  **Clone repository ini:**

    ```bash
    git clone https://github.com/username/MIBGA.git
    cd MIBGA
    ```

2.  **Buat Virtual Environment (Disarankan):**

    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install Dependensi:**

    ```bash
    pip install -r requirements.txt
    ```

## 📊 Format Data Input

Program ini membaca file graf yang berisi daftar *edge*. Format yang didukung:

### 1\. Excel (`.xlsx`) / CSV (`.csv`)

File harus memiliki header. Program akan mendeteksi kolom secara otomatis jika namanya sesuai (misal: `startnode_x`), atau menggunakan urutan indeks kolom 0-4.

| Column 0 (Sx) | Column 1 (Sy) | Column 2 (Ex) | Column 3 (Ey) | Column 4 (Weight) |
| :--- | :--- | :--- | :--- | :--- |
| Koordinat X Asal | Koordinat Y Asal | Koordinat X Tujuan | Koordinat Y Tujuan | Jarak/Bobot |

### 2\. Edgelist (`.txt` / lainnya)

Format standar NetworkX: `u v weight`.

## 🚀 Cara Penggunaan

Program dijalankan melalui terminal menggunakan `main.py`. Terdapat dua mode operasi:

### 1\. Mode Inspeksi (Cek Node ID)

Gunakan mode ini jika Anda belum mengetahui ID dari Node Start dan Node Target. Jalankan tanpa argumen `-S` dan `-T`.

```bash
python main.py data/arizona.xlsx
```

**Output:** Program akan menampilkan statistik graf dan daftar sampel Node ID beserta koordinatnya.

### 2\. Mode Eksekusi (Menjalankan Algoritma)

Setelah mendapatkan Node ID, jalankan algoritma dengan perintah berikut:

```bash
python main.py <path_file> -S <start_node> -T <target_node> [opsi]
```

**Argumen:**

  * `graph_file` (Wajib): Path ke file dataset.
  * `-S`, `--start` (Wajib): ID Node Awal.
  * `-T`, `--target` (Wajib): ID Node Tujuan.
  * `-K`, `--k_paths` (Opsional): Jumlah jalur alternatif yang dicari (Default: 3).
  * `-e`, `--epsilon` (Opsional): Batas toleransi kepanjangan jalur relatif terhadap jalur terpendek (Default: 0.2 atau 20%).

**Contoh Perintah:**

```bash
# Mencari 5 jalur alternatif dari Node 0 ke Node 45 dengan toleransi panjang 30%
python main.py data/arizona.xlsx -S 0 -T 45 -K 5 -e 0.3
```

## 🧠 Penjelasan Algoritma

1.  **Inisialisasi:** Populasi awal dibangkitkan secara acak (Random Walk) dari Node S ke T.
2.  **Pembentukan Pulau (Islands):** Populasi dibagi menjadi beberapa "pulau". Setiap pulau memiliki sub-populasi *Superior* (fitness tinggi) dan *Central* (fitness rata-rata).
3.  **Evolusi (Generasi):**
      * **Migrasi:** Secara periodik, individu superior berpindah antar pulau.
      * **Crossover & Mutasi:** Operator LFPC digunakan untuk menghasilkan keturunan baru tanpa *loop*.
      * **Seleksi:** Individu terbaik dipertahankan berdasarkan rata-rata fitness pulau.
4.  **Seleksi Akhir (KMDNSP):**
      * Semua jalur unik yang ditemukan dikumpulkan.
      * Filter jalur yang panjangnya $\le (1 + \epsilon) \times \text{ShortestPath}$.
      * Cari kombinasi $K$ jalur yang memiliki nilai keragaman (diversity) kolektif tertinggi.

## 📈 Visualisasi

Setelah proses selesai, browser akan otomatis membuka visualisasi **Plotly**:

  * **Garis Abu-abu:** Jaringan jalan (background).
  * **Garis Berwarna:** Jalur solusi akhir (K jalur terbaik).
  * **Bintang Hijau/Hitam:** Titik Awal (Start) dan Tujuan (Target).
  * Anda dapat melakukan *zoom*, *pan*, dan *hover* untuk melihat detail node.
