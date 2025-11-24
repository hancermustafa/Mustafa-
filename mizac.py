import streamlit as st
import plotly.graph_objects as go
import streamlit.components.v1 as components
import time

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Mizaç Analiz | Dr. Sait SEVİNÇ", layout="wide", page_icon="🧬")

# --- 2. TASARIM VE GÖRSELLİK ---
st.markdown("""
    <style>
    /* Font */
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* LOGO */
    .dr-logo {
        font-size: 32px;
        font-weight: 900;
        color: #2C3E50;
        border-bottom: 4px solid #E74C3C;
        padding-bottom: 10px;
        margin-bottom: 30px;
        text-align: center;
        letter-spacing: 1px;
    }

    /* SORU KUTUSU */
    .question-box {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        border-left: 8px solid #3498DB;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .q-text { font-size: 19px; font-weight: 700; color: #2C3E50; margin-bottom: 12px; }
    
    /* UYARI MESAJI */
    .missing-alert {
        background-color: #FDEDEC;
        color: #E74C3C;
        padding: 10px;
        border-radius: 8px;
        font-weight: bold;
        border: 1px solid #E74C3C;
        margin-bottom: 10px;
    }

    /* YAZDIRMA AYARLARI */
    @media print {
        /* Menüleri gizle */
        [data-testid="stSidebar"], header, footer, .stButton, button, .stProgress, .stForm { display: none !important; }
        
        /* Ana içeriği serbest bırak */
        .block-container, [data-testid="stAppViewContainer"], .main { 
            padding-top: 0 !important; 
            max-width: 100% !important;
            overflow: visible !important; 
            height: auto !important;
        }
        
        body { 
            -webkit-print-color-adjust: exact !important; 
            print-color-adjust: exact !important; 
            background-color: white !important;
        }
        
        h1, h2, h3, p, div, span, li, b, strong { color: #000000 !important; }
        
        .plotly-graph-div { 
            break-inside: avoid; 
            page-break-inside: avoid; 
            width: 100% !important; 
            margin-bottom: 20px; 
            display: block !important; 
        }
        .rec-card, .score-box { break-inside: avoid; border: 1px solid #ccc !important; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SCROLL ÇÖZÜMÜ (ÇAPA SİSTEMİ) ---
# Sayfanın en tepesine görünmez bir işaret koyuyoruz
st.markdown("<div id='top-marker'></div>", unsafe_allow_html=True)

def force_scroll_up():
    # Bu fonksiyon, sayfa her değiştiğinde tarayıcıyı 'top-marker'a odaklar.
    # İçerik her seferinde değiştiği için (time.time) Streamlit bunu yeni kod sanıp çalıştırır.
    js = f"""
    <script>
        var target = window.parent.document.getElementById("top-marker");
        if (target) {{
            target.scrollIntoView({{behavior: "auto", block: "start"}});
        }}
        window.scrollTo(0, 0);
        var main = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
        if (main) {{ main.scrollTop = 0; }}
    </script>
    """
    components.html(js + f"", height=0)

# --- 4. VERİLER ---
SORULAR = {
    "SICAKLIK": {
        "puanlar": {"Hayır": 1, "Orta derece": 2, "Kesinlikle evet": 3},
        "sorular": [
            "Arkadaş çevrem geniş sosyal biriyim", "Hızlı düşünür çabuk harekete geçerim", "Konuşkan sıcakkanlı bir yapım var",
            "Soğuk havaları severim", "Soğuk yiyecek içeceklerden hoşlanırım", "Vücudum sıcaktır", "Takıntılı değilim",
            "Cesur ve atak biriyim", "Çok detaylı düşünmem", "Kabızlık sorunu çok fazla yaşamam", "Rutin / tekdüze sakin yaşamdan pek sevmem",
            "Pozitifim", "Kuralları çok sevmem", "Sonuç odaklıyım", "Lider bir ruhum var", "Genelde enerjik bir yapım var",
            "Yapılanı unuturum kin tutamam", "Sır saklamakta zorlanırım anlatma eğilimim vardır"
        ]
    },
    "SOĞUKLUK": {
        "puanlar": {"Hayır": 1, "Orta derece": 2, "Kesinlikle evet": 3},
        "sorular": [
            "Çok geniş bir çevrem yok", "Temkinli biriyim", "Hemen samimi olmam, seçiciyim", "Sıcak havaları severim",
            "Sıcak yiyecek ve içeceklerden hoşlanırım", "Vücudum soğuktur üşürüm", "Takıntılıyım", "Hassas ve alıngan biriyim",
            "Aceleyi sevmem işimi sağlam yavaş yavaş yaparım", "Kabızlık sorunu çok yaşarım", "Sakin yaşam severim", "Karamsarım",
            "Kurallara uyarım", "Süreç odaklıyım", "İyi bir takım oyuncusuyum", "Genelde enerjim düşüktür (çabuk yorulurum)",
            "Negatifi unutmam", "Sır saklarım"
        ]
    },
    "KURULUK": {
        "puanlar": {"Hayır": 0, "Orta derece": 2, "Kesinlikle evet": 3},
        "sorular": [
            "Saçlarım kalın telli", "Zayıf ince yapılıyım", "Cildim genelde kuru", "Cilt lekelerim vardır lekelenmeye müsaittir",
            "Çok uyuyamam derin değildir uyanırım hemen", "Sıkı ve gergin bir cildim var", "Göz yapım küçüktür", "Belim nispeten incedir",
            "Hafızam kuvvetlidir", "Duyularım gelişmiştir duyma/ koku alma", "Esnek biri değilim uyum sağlamam zordur",
            "Eklemlerim çıkıntılı", "Tenim daha sarı ve koyu renkte", "Tırnaklarım serttir", "Çabuk pes etmem ısrarcıyım",
            "Genelde burun akıntım çok az olur", "Kaşıntı egzemaya yatkınlığım fazladır", "Ağız kuruluğum fazladır"
        ]
    },
    "NEMLİLİK": {
        "puanlar": {"Hayır": 0, "Orta derece": 1, "Kesinlikle evet": 2},
        "sorular": [
            "Saçlarım ince telli", "Kiloluyum", "Cildim yumuşaktır", "Uykuyu severim derin uyurum", "Çok az cilt lekelerim var",
            "Cildim yumuşak ve esnektir", "Göz yapım iri ve nemlidir", "Belim nispeten kalındır",
            "Hafızam kuvvetli değil tekrarlamazsam çabuk unuturum", "Duyularım zayıftır koku alma/işitme", "Esnek biriyim uyum sağlarım",
            "Eklemlerim, hatlarım belirgin değildir", "Yuvarlak yüzlüyüm", "Tırnak yapım yumuşaktır", "Çabuk pes ederim bıkarım",
            "Burun akıntım olur", "Egzema ve kaşıntı çok nadir görülür", "Ağız kuruluğum yoktur sulu ve yoğun olabilir"
        ]
    }
}

HASTALIKLAR = {
    "SICAK NEMLİ (Demevi)": ["Yüksek tansiyon", "Kalp çarpıntıları", "Ciltte kızarıklık", "Akne problemleri", "Şeker (Diyabet)", "Baş ağrısı ve migren", "Karaciğer yağlanması"],
    "SICAK KURU (Safravi)": ["Mide yanması", "Safra problemleri", "Uykusuzluk ve stres", "Cilt kuruluğu", "Öfke kontrol sorunları", "Saç dökülmesi"],
    "SOĞUK KURU (Sovdavi)": ["Depresyon ve kaygı", "Eklem ağrıları", "Kabızlık", "Varis ve hemoroid", "Kronik yorgunluk", "Vesvese"],
    "SOĞUK NEMLİ (Balgami)": ["Obezite", "Ödem ve şişkinlik", "Unutkanlık", "Soğuk algınlığı", "Eklem romatizmaları", "Tembellik hissi"]
}

ONERILER_DETAY = {
    "SICAK NEMLİ (Demevi)": {
        "genel": "Demevi mizaçlı kişiler genellikle enerjik, sosyal ve sıcakkanlıdırlar. Kan basıncı ve dolaşım sistemi sorunlarına yatkındırlar.",
        "beslenme": "Kırmızı et, hamur işleri ve aşırı tatlı gıdalardan kaçınmalısınız. Serinletici gıdalar (salatalık, marul, kabak, limon) ve bol su tüketimi sizin için hayati önem taşır. Ekşi meyveler (nar, erik) tüketin.",
        "yasam": "Kan hacminiz yüksek olabilir; uzman kontrolünde hacamat yaptırmak size iyi gelebilir. Hareketli sporlar yapın.",
        "renk": "#E74C3C" 
    },
    "SICAK KURU (Safravi)": {
        "genel": "Safravi mizaçlılar lider ruhlu, hızlı düşünen ve atak kişilerdir. Isı ve kuruluk arttığında sinirlilik yaşayabilirler.",
        "beslenme": "Acı, baharatlı, tuzlu ve kızartma türü yiyeceklerden uzak durun. Ayran, yoğurt, cacık, sirke ve koruk suyu şifadır.",
        "yasam": "Aşırı sıcak ortamlardan ve güneşten kaçının. Düzenli uyuyun. Rekabetçi ortamlardan ziyade doğa yürüyüşleri yapın.",
        "renk": "#F1C40F" 
    },
    "SOĞUK KURU (Sovdavi)": {
        "genel": "Sovdavi mizaçlılar detaycı, analitik ve hassas bir yapıya sahiptir. Soğukluk metabolizmayı yavaşlatabilir.",
        "beslenme": "Kuru gıdalardan (mercimek, nohut) uzak durun. Sıcak, sulu tencere yemekleri (kuzu eti) tüketin. Tatlı meyveler yiyin.",
        "yasam": "Cildinizi nemlendirin. Yalnız kalmak melankoliyi artırabilir, sosyalleşin. Hafif egzersizler yapın.",
        "renk": "#8E44AD" 
    },
    "SOĞUK NEMLİ (Balgami)": {
        "genel": "Balgami mizaçlılar sakin, uyumlu ve sabırlı kişilerdir. Nem artışı tembellik ve ödem yapabilir.",
        "beslenme": "Süt ürünleri, beyaz un ve şekeri azaltın. Isıtıcı baharatlar (zencefil, karabiber) kullanın. Izgara etler tercih edin.",
        "yasam": "Hareketsizlik en büyük düşmanınızdır. Gündüz uykusundan kaçının. Sıcak hamam veya sauna size iyi gelir.",
        "renk": "#3498DB" 
    }
}

# --- 5. SESSION STATE ---
if 'step' not in st.session_state: st.session_state.step = 0 
if 'answers' not in st.session_state: st.session_state.answers = {}
if 'validation_error' not in st.session_state: st.session_state.validation_error = False

# --- SCROLL TRIGGER (STEP TAKİBİ) ---
if 'last_step_scroll' not in st.session_state: st.session_state.last_step_scroll = -1

BOLUMLER = list(SORULAR.keys())

# --- 6. HESAPLAMA ---
def hesapla():
    skorlar = {}
    yuzdeler = {}
    for bolum, veri in SORULAR.items():
        toplam = 0
        max_puan = len(veri["sorular"]) * max(veri["puanlar"].values())
        for i, soru in enumerate(veri["sorular"]):
            key = f"{bolum}_{i}"
            secim = st.session_state.answers.get(key)
            if secim: toplam += veri["puanlar"][secim]
        skorlar[bolum] = toplam
        yuzdeler[bolum] = (toplam / max_puan) * 100 if max_puan > 0 else 0
    return skorlar, yuzdeler

def mizac_bul(yuzdeler):
    isi = "SICAK" if yuzdeler["SICAKLIK"] >= yuzdeler["SOĞUKLUK"] else "SOĞUK"
    nem = "KURU" if yuzdeler["KURULUK"] >= yuzdeler["NEMLİLİK"] else "NEMLİ"
    anahtar = f"{isi} {nem}"
    for k in HASTALIKLAR.keys():
        if anahtar in k: return k
    return anahtar

# --- 7. ANA UYGULAMA AKIŞI ---

# Sayfa her değiştiğinde Scroll Fonksiyonunu çağır (Çapa'ya git)
if st.session_state.step != st.session_state.last_step_scroll:
    force_scroll_up()
    st.session_state.last_step_scroll = st.session_state.step

# LOGO (Her sayfada sabit)
st.markdown('<div class="dr-logo">Dr. Sait SEVİNÇ</div>', unsafe_allow_html=True)

# 1. GİRİŞ
if st.session_state.step == 0:
    st.markdown("### 🧬 Mizaç Analiz Sistemi")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1: yas = st.number_input("Yaş:", 1, 100, 30)
        with c2: cinsiyet = st.selectbox("Cinsiyet:", ["Kadın", "Erkek"])
    
    st.session_state.answers['yas'] = yas
    st.session_state.answers['cinsiyet'] = cinsiyet
    
    if st.button("Analize Başla 🚀", type="primary", use_container_width=True):
        st.session_state.step = 1
        st.rerun()

# 2. SORULAR (1-4)
elif 1 <= st.session_state.step <= 4:
    
    bolum_idx = st.session_state.step - 1
    bolum_adi = BOLUMLER[bolum_idx]
    veri = SORULAR[bolum_adi]
    
    st.progress((st.session_state.step - 1) / 4, text=f"Bölüm {st.session_state.step}/4: {bolum_adi} Analizi")
    st.subheader(f"📌 {bolum_adi}")

    with st.form(key=f"form_{bolum_adi}"):
        for idx, soru in enumerate(veri["sorular"]):
            key = f"{bolum_adi}_{idx}"
            
            st.markdown(f'<div class="question-box">', unsafe_allow_html=True)
            
            if st.session_state.validation_error and st.session_state.answers.get(key) is None:
                st.markdown(f'<div class="missing-alert">⚠️ Lütfen cevaplayınız</div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="q-text">{idx+1}. {soru}</div>', unsafe_allow_html=True)
            
            opts = list(veri["puanlar"].keys())
            opts.sort(key=lambda x: veri["puanlar"][x])
            
            current_val = st.session_state.answers.get(key)
            idx_val = opts.index(current_val) if current_val in opts else None
            
            st.radio("Cevap:", opts, index=idx_val, key=f"widget_{key}", horizontal=True, label_visibility="collapsed")
            
            st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.validation_error:
            st.error("⚠️ Lütfen boş bıraktığınız soruları yanıtlayın.")

        btn_txt = "Sonraki Bölüm ➡️" if st.session_state.step < 4 else "Bitir ve Kontrol Et ✅"
        if st.form_submit_button(btn_txt, type="primary"):
            missing = False
            for i in range(len(veri["sorular"])):
                w_key = f"widget_{bolum_adi}_{i}"
                val = st.session_state.get(w_key)
                if val: st.session_state.answers[f"{bolum_adi}_{i}"] = val
                else: 
                    st.session_state.answers[f"{bolum_adi}_{i}"] = None
                    missing = True
            
            if missing:
                st.session_state.validation_error = True
                st.rerun()
            else:
                st.session_state.validation_error = False
                st.session_state.step += 1
                st.rerun()

    if st.session_state.step > 1:
        if st.button("⬅️ Geri", use_container_width=False):
            st.session_state.step -= 1
            st.rerun()

# 3. KONTROL
elif st.session_state.step == 5:
    st.title("📝 Kontrol")
    st.success("Tüm sorular yanıtlandı.")
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Düzenle", use_container_width=True):
        st.session_state.step = 4
        st.rerun()
    if c2.button("Sonuçları Göster 🏁", type="primary", use_container_width=True):
        st.session_state.step = 6
        st.rerun()

# 4. SONUÇ
elif st.session_state.step == 6:
    
    skorlar, yuzdeler = hesapla()
    sonuc = mizac_bul(yuzdeler)
    detaylar = ONERILER_DETAY.get(sonuc, {})
    renk = detaylar.get("renk", "#333")

    st.markdown(f"**Danışan:** {st.session_state.answers.get('yas')} / {st.session_state.answers.get('cinsiyet')}")
    st.markdown(f"<h1 style='text-align:center; color:{renk}; border-bottom:2px solid {renk}'>Baskın Mizaç: {sonuc}</h1>", unsafe_allow_html=True)

    c_main, c_side = st.columns([1.5, 1])
    
    with c_main:
        st.subheader("Grafiksel Analiz")
        cats = list(yuzdeler.keys())
        vals = list(yuzdeler.values())
        
        # Grafik 1: Bar
        fig1 = go.Figure(go.Bar(
            x=cats, y=vals, text=[f"%{v:.0f}" for v in vals], textposition='auto',
            marker_color=['#E74C3C', '#3498DB', '#F1C40F', '#2ECC71'],
            marker=dict(line=dict(width=2, color='DarkSlateGrey'), opacity=0.9)
        ))
        fig1.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig1, use_container_width=True)
        
        # Grafik 2: Radar
        vals_c = vals + [vals[0]]
        cats_c = cats + [cats[0]]
        hex_code = renk.lstrip('#')
        rgb = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
        
        fig2 = go.Figure(go.Scatterpolar(
            r=vals_c, theta=cats_c, fill='toself',
            fillcolor=f'rgba({rgb[0]},{rgb[1]},{rgb[2]},0.4)',
            line=dict(color=renk, width=3)
        ))
        fig2.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=350, margin=dict(t=30, b=30))
        st.plotly_chart(fig2, use_container_width=True)

    with c_side:
        st.subheader("Puanlar")
        for b in BOLUMLER:
            st.metric(label=b, value=f"{skorlar[b]} Puan", delta=f"%{yuzdeler[b]:.0f}")
            st.progress(min(yuzdeler[b]/100, 1.0))

    st.markdown("---")
    st.header("📋 Tavsiye ve Öneriler")
    
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("#### 🧬 Genel")
            st.write(detaylar.get('genel', ''))
        with st.container(border=True):
            st.markdown("#### 🥗 Beslenme")
            st.write(detaylar.get('beslenme', ''))
    with c2:
        with st.container(border=True):
            st.markdown("#### 🏃 Yaşam Tarzı")
            st.write(detaylar.get('yasam', ''))
        with st.container(border=True):
            st.markdown("#### ⚠️ Riskler")
            for r in HASTALIKLAR.get(sonuc, []):
                st.write(f"- {r}")
                
    st.markdown("---")
    
    # Manuel Yazdırma Uyarısı (Sizin beğendiğiniz)
    st.info("💡 İPUCU: Raporu yazdırmak veya PDF olarak kaydetmek için tarayıcınızın menüsünden **Yazdır (Ctrl+P)** seçeneğini kullanınız. En temiz sonuç bu şekilde alınmaktadır.")
    
    if st.button("🔄 Yeni Analiz", use_container_width=True):
        st.session_state.clear()
        st.rerun()