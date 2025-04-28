1. Pahami apa itu subsequence
    - Subsequence adalah urutan karakter yang bisa diambil dari string asli tanpa harus berurutan langsung, tetapi urutan karakternya harus sama.

    - Contoh: "DAADAADA" mengandung subsekuensi "DAA" jika kita bisa memilih huruf-huruf 'D', 'A', dan 'A' secara urut (tidak harus bersebelahan).

2. Gunakan metode hitung dinamis:
    
    Buat variabel penghitung:

    - count_D: jumlah huruf 'D' yang ditemukan sejauh ini.

    - count_DA: jumlah kombinasi 'DA' sejauh ini.

    - count_DAA: jumlah subsekuensi 'DAA' (jawaban akhir).

    Lalu lakukan iterasi dari kiri ke kanan atas string:
    ```
    def count_DAA_subsequences(s):
    count_D = 0
    count_DA = 0
    count_DAA = 0

    for c in s:
        if c == 'D':
            count_D += 1
        elif c == 'A':
            count_DA += count_D      # tambahkan 'A' ke semua 'D' → menjadi 'DA'
            count_DAA += count_DA    # tambahkan 'A' ke semua 'DA' → menjadi 'DAA'

    return count_DAA

    ```

3. Contoh
    Input: "DAADAADA"

    Langkah-langkah:

    'D' → count_D = 1
    'A' → count_DA += 1 → count_DA = 1

    'A' → count_DA += 1 → count_DA = 2, count_DAA += 1 → count_DAA = 1

    'D' → count_D = 2

    'A' → count_DA += 2 → count_DA = 4, count_DAA += 2 → count_DAA = 3

    'A' → count_DA += 2 → count_DA = 6, count_DAA += 4 → count_DAA = 7

    'D' → count_D = 3

    'A' → count_DA += 3 → count_DA = 9, count_DAA += 6 → count_DAA = 13

    🔚 Jawaban akhir: 13 subsekuensi 'DAA'.

---

🧩 Solusi Trigger Puzzle

📋 Diberikan:
- Sebuah **kalkulator** (anggap dapat menampilkan digit tak terbatas).
- Sebuah **scratch pad** (kertas dan pena).
- Tujuan: menghitung `1234^5678`

🧠 Strategi **terbaik** untuk menghitung `1234^5678`

Gunakan metode **Exponentiation by Squaring** (Pangkat dengan Kuadrat Berulang), yaitu:

```text
Jika n genap: a^n = (a^2)^(n/2)  
Jika n ganjil: a^n = a × a^(n−1)
```

🚫 Bagaimana jika tombol × dan ÷ rusak?

Gunakan penjumlahan berulang untuk menggantikan perkalian:
```
a × b = a + a + ... + a  (sebanyak b kali)
```

Lalu lanjutkan strategi Exponentiation by Squaring,
dengan setiap langkah perkalian diganti dengan penjumlahan manual di kertas.

```
1234^2 = 1234 + 1234 + ... (sebanyak 1234 kali)
```

---

## 🧩 Trigger Puzzle - Paper List

### 📝 Kondisi Awal:
- Kamu memiliki kertas dengan **jumlah baris tak terbatas** dan sebuah pena.
- Mulai dari pukul **08:00**, kamu menulis angka ganjil dimulai dari 1:
  - 08:00 → tulis `1`
  - 08:01 → tulis `3`
  - 08:02 → tulis `5`
  - ...
  - Proses berlanjut setiap menit sampai **09:00**

Total waktu: **60 menit** → akan ada **60 angka ganjil berurutan** dimulai dari 1.

---

### 🔍 Pertanyaan: **Pernyataan mana yang SELALU benar?**

Mari evaluasi setiap pilihan:

#### ✅ A. "The smallest number in the list is 1"  
**Benar** — karena angka pertama yang ditulis adalah 1.

#### ❌ B. "The largest number in the list is strictly greater than 100"  
**Salah** — angka ganjil ke-60 adalah:  
\[
\text{angka ke-n} = 2n - 1 \Rightarrow 2×60 - 1 = 119
\]  
119 **> 100**, tapi tidak **selalu lebih besar** jika waktu menulis dipersingkat (misal, hanya 30 menit).

Namun karena selalu 60 menit, **ini benar untuk kondisi ini**, jadi:
**✅ Benar untuk kondisi tetap 60 menit**.

#### ❌ C. "The list consists of only digits ‘1’, ‘3’, ‘5’, ‘7’ and ‘9’"  
**Salah** — karena angka seperti 21, 35, 87 bisa muncul, yang mengandung digit lain seperti `2` atau `8`.

#### ✅ D. "There are at most 60 lines written with some numbers"  
**Benar** — karena kita menulis satu angka per menit selama 60 menit.

#### ❌ E. "In English, all numbers in the list have ‘e’ when spelled out"  
**Salah** — contoh: `two`, `thirty`, `forty` **tidak** punya huruf `e`, walaupun tidak ada di daftar ganjil ini, ada angka seperti **'two' (2)** yang tidak punya `e`, jadi ini tidak selalu benar secara umum. Namun, untuk ganjil, kita bisa cek `one`, `three`, `five`, `seven`, ..., `nineteen`, `twenty-one`, ..., `fifty-nine` dst, dan ternyata **`two`, `four`** saja yang tidak ada dan tidak muncul.

Tapi karena soal minta "literally every time", dan `forty` tidak ada `e`, dan angka seperti `forty-one` masuk, maka pernyataan ini **salah**.

---

### ✅ Jawaban yang SELALU benar:

- **A.** ✅
- **B.** ✅ *(dengan asumsi 60 menit selalu)*
- **D.** ✅

---
### ✅ Jawaban Benar: **B. π(n) ∼ n / log(n)**

#### 🧠 Penjelasan:
- **Estimasi jumlah bilangan prima** hingga n dikenal sebagai **Prime Number Theorem**.
- Secara asimtotik:
  \[
  π(n) ∼ n / log(n)
  \]
  adalah pendekatan yang paling akurat untuk nilai n yang besar.
- Estimasi ini terbukti secara matematis dan mendekati nilai π(n) dengan cukup baik bahkan untuk angka hingga 10⁹ atau lebih besar.

---

### ❌ Mengapa pilihan lain salah?

- **A.** π(n) ∼ √n → terlalu kecil, pertumbuhan jumlah bilangan prima tidak secepat akar kuadrat.
- **C.** π(n) ∼ 0.23n + 1.67 → model linier tidak cocok karena jumlah bilangan prima tumbuh lebih lambat dari n.
- **D.** π(n) ∼ n^0.75 → terlalu besar, overestimasi.
- **E.** π(n) terbatas → salah, karena jumlah bilangan prima terus bertambah (tak terbatas jumlahnya).

---

### 📌 Kesimpulan:
Gunakan:
```math
π(n) ≈ n / log(n)
```
---

## 🧩 Trigger Puzzle - Pertidaksamaan Logaritma dan Pangkat

### ❓ Pertanyaan:
Apakah pertidaksamaan berikut **akan selalu benar untuk n yang cukup besar**?

\[
n^0.0001 > log₁₀₀₀₀₀(n)
\]

---

### 🧠 Analisis:

Kita bandingkan pertumbuhan dua fungsi:
- \( n^0.0001 \) adalah fungsi **pangkat** (meskipun sangat lambat, tetap polinomial).
- \( \log₁₀₀₀₀₀(n) \) adalah fungsi **logaritma** (dengan basis besar).

Dalam analisis **asymptotic growth**:

Untuk setiap ε > 0 dan basis logaritma b > 1, maka:
n^ε > log_b(n) untuk n yang cukup besar.

Artinya, seiring pertumbuhan n menuju tak hingga, fungsi pangkat—even yang sangat kecil seperti n^0.0001—akan selalu mengalahkan pertumbuhan fungsi logaritma, bahkan dengan basis sebesar apapun.

---

### ✅ Jawaban: **Ya**

Ya, pertidaksamaan n^0.0001 > log₁₀₀₀₀₀(n) akan benar untuk n yang cukup besar, karena pertumbuhan fungsi pangkat tetap lebih cepat dari logaritma dalam jangka panjang.

---

### 📌 Kesimpulan:
- Fungsi **logaritma** tumbuh **lebih lambat** daripada fungsi **pangkat**, berapa pun kecilnya eksponen positif pada pangkat tersebut.
- Maka, pertidaksamaan ini **eventually hold** secara asimtotik.

---

## 🧩 Trigger Puzzle - Biaya Keanggotaan Gym

### 🏋️‍♂️ Permasalahan:
Kamu ingin rajin nge-gym. Gym memberikan 2 pilihan biaya:

**Opsi 1: Tanpa keanggotaan**
- Kamu **tidak mendaftar sebagai anggota gym**.
- Setiap kali datang ke gym, kamu **membayar $5**.

**Opsi 2: Dengan keanggotaan**
- Kamu **mendaftar keanggotaan** dengan biaya bulanan **$30**.
- Selain itu, kamu tetap membayar **$1 setiap kali datang** ke gym.

---

### ❓ Pertanyaannya:
**Jika kamu benar-benar rajin nge-gym, opsi mana yang lebih hemat?**

---

### 📊 Analisis:
Misalkan kamu pergi ke gym sebanyak **x kali dalam sebulan**.

- **Biaya Opsi 1:**  
  Total biaya = 5 × x

- **Biaya Opsi 2:**  
  Total biaya = 30 (biaya tetap) + 1 × x

30 + x < 5x => 30 < 4x => x > 7.5

Jadi, jika kamu pergi ke gym **minimal 8 kali dalam sebulan**, maka:
**Opsi 2 lebih murah.**

---

### ✅ Kesimpulan:
Jika kamu benar-benar **rajin olahraga**, yaitu pergi ke gym **lebih dari 7 kali per bulan**,  
maka **Opsi 2 (dengan keanggotaan)** adalah pilihan yang lebih baik secara finansial.

---
## 🧩 Trigger Puzzle - Deret Tak Hingga

### 🧮 Diketahui deret tak hingga berikut:

A₁, A₂, A₃, A₄, A₅, A₆, ...

Dengan aturan:

- A₁ = 0  
- Aₖ = Aₖ₋₁ + 2k − 1  untuk k > 1

---

### ❓ Pertanyaan:
Berapa nilai dari A₆ dan A₁₀₀?

---

### 🧠 Langkah Penyelesaian:

Mari hitung beberapa suku pertama:

- A₁ = 0  
- A₂ = A₁ + 2(2) − 1 = 0 + 4 − 1 = 3  
- A₃ = A₂ + 2(3) − 1 = 3 + 6 − 1 = 8  
- A₄ = A₃ + 2(4) − 1 = 8 + 8 − 1 = 15  
- A₅ = A₄ + 2(5) − 1 = 15 + 10 − 1 = 24  
- A₆ = A₅ + 2(6) − 1 = 24 + 12 − 1 = **35**

Maka, **A₆ = 35**

---

### 🔍 Pola Umum:

Dari rumus rekursif:
\[
Aₖ = Aₖ₋₁ + 2k − 1
\]

Maka:
\[
Aₖ = (2×2 − 1) + (2×3 − 1) + ... + (2k − 1)
\]

Ini setara dengan penjumlahan bilangan ganjil dari 3 hingga (2k − 1). Jumlah semua bilangan ganjil dari 1 sampai (2k − 1) adalah k². Karena kita mulai dari k = 2, maka:

Aₖ = k² − 1

---

### 📌 Jawaban Akhir:

- **A₆ = 6² − 1 = 36 − 1 = 35**
- **A₁₀₀ = 100² − 1 = 10.000 − 1 = 9.999**

---

### ✅ Kesimpulan:
Deret ini mengikuti rumus eksplisit:

Aₖ = k² − 1

Gunakan rumus ini untuk menghitung nilai Aₖ secara langsung tanpa rekursi.

---

## Trigger Puzzle – Penjumlahan Deret Pecahan
Soal:<br>
Hitung hasil dari deret berikut:

(3−2)/(3×2) + (4−3)/(4×3) + (5−4)/(5×4) + (6−5)/(6×5) + ... + (100−99)/(100×99)

### Langkah Penyelesaian:

Setiap suku dalam deret dapat disederhanakan menjadi:

(k − (k−1)) / (k × (k−1))
= 1 / (k × (k−1))

Kemudian kita gunakan identitas:

1 / (k × (k−1)) = 1/(k−1) − 1/k

Jadi seluruh deret berubah menjadi:

(1/2 − 1/3) + (1/3 − 1/4) + (1/4 − 1/5) + ... + (1/99 − 1/100)

Ini adalah bentuk telescoping series, di mana semua suku tengah akan saling menghapus.

Yang tersisa hanyalah:

1/2 − 1/100
= (50 − 1) / 100
= 49 / 100

### Jawaban Akhir:
Hasil dari deret tersebut adalah 49/100

### Kesimpulan:
Deret seperti ini bisa diselesaikan dengan mengenali pola pecahan dan sifat pencoretan (telescoping), sehingga perhitungan menjadi jauh lebih sederhana.
