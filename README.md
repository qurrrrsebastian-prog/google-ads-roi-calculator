# Google Ads ROI Calculator

![Python](https://img.shields.io/badge/Python-3.13%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-red)
![Pandas](https://img.shields.io/badge/Pandas-2.3%2B-green)
![NumPy](https://img.shields.io/badge/NumPy-2.1%2B-orange)

## 📌 Deskripsi
Streamlit app untuk kalkulasi ROI Google Ads. Input budget, CPC, conversion rate, dan AOV — output: clicks, conversions, revenue, ROAS, break-even analysis, dan rekomendasi scaling. Dibuat untuk marketer & UMKM Indonesia yang ingin tahu apakah campaign Google Ads mereka layak di-scale, di-hold, atau di-stop.

## 🎯 Fitur
- KPI cards real-time (Clicks, Conversions, Revenue, ROAS)
- 3 Scenario analysis (Pessimistic, Realistic, Optimistic)
- Break-even chart by conversion rate
- Scaling roadmap (Stop / Hold / Scale)
- 12-month projection dengan auto-scaling

## 🛠️ Tech Stack
- Python, Streamlit, Pandas, NumPy

## 🚀 Cara Menjalankan
```powershell
pip install -r requirements.txt
streamlit run app.py
```

App akan terbuka otomatis di browser pada `http://localhost:8501`.

## 💡 3 Key Insights
1. **Break-even conversion rate = CPC / (AOV × 1%)**: Dengan CPC Rp 2.500 dan AOV Rp 500.000, campaign break-even di conversion rate **0,5%** — setiap 0,5% tambahan CR di atasnya menghasilkan ROAS +1.0x.
2. **Gap pessimistic vs optimistic bisa 7x**: Pada budget Rp 5 juta/bulan, skenario pessimistic (CPC Rp 3.500, CR 1,5%) menghasilkan revenue ~Rp 10,5 juta (ROAS 2,1x), sedangkan optimistic (CPC Rp 1.800, CR 5,5%) mencapai ~Rp 76 juta (ROAS 15,2x) — riset keyword & landing page menentukan segalanya.
3. **Compounding 10% scaling itu signifikan**: Jika ROAS stabil di atas 1,5x dan budget dinaikkan 10% per bulan, budget bulan ke-12 menjadi ~2,85x budget awal — dari Rp 5 juta menjadi ~Rp 14,3 juta dengan revenue yang tumbuh proporsional.

## 👤 Author
**Avatar Putra Sigit**
- LinkedIn: [linkedin.com/in/avatarputrasigit](https://linkedin.com/in/avatarputrasigit)
- GitHub: [github.com/qurrrrsebastian-prog](https://github.com/qurrrrsebastian-prog)
