from flask import Flask, render_template_string, request, Response, jsonify
import time
from datetime import datetime, date
import os

app = Flask(__name__)

# Ayarlar
DOMAIN = os.environ.get('DOMAIN', 'paneli.art')  # Deployda DOMAIN=paneli.art olarak ayarla
MAX_REQUESTS = int(os.environ.get('MAX_REQUESTS', 50))  # istek limiti
PER_SECONDS = int(os.environ.get('PER_SECONDS', 3600))  # limit süresi (saniye)

# Rate limiter (basit)
class RateLimiter:
    def __init__(self, max_requests=100, per_seconds=3600):
        self.max_requests = max_requests
        self.per_seconds = per_seconds
        self.requests = {}  # { ip: [timestamp,...] }

    def is_allowed(self, ip, record=True):
        """
        record=True ise bu istek kaydedilir.
        record=False ise sadece kontrol yapılır (kaydetmez).
        """
        now = time.time()
        if ip not in self.requests:
            self.requests[ip] = []

        # Eski kayıtları temizle
        self.requests[ip] = [t for t in self.requests[ip] if now - t < self.per_seconds]

        # Limit kontrolü
        if len(self.requests[ip]) >= self.max_requests:
            return False

        # Eğer kaydetmek isteniyorsa, listeye ekle
        if record:
            self.requests[ip].append(now)
        return True

# Başlat
rate_limiter = RateLimiter(max_requests=MAX_REQUESTS, per_seconds=PER_SECONDS)

# Günlük istek sayacı
request_counter = {
    'count': 0,
    'last_reset': date.today()
}

def get_client_ip():
    """
    Öncelikle User-Agent kontrolü ile search engine tespiti yapar.
    Eğer search engine ise 'search-engine' döner (bypass için).
    Aksi halde X-Forwarded-For veya remote_addr döner.
    """
    ua = (request.headers.get('User-Agent') or '').lower()
    # Google / Bing / Yahoo bot vs
    if 'googlebot' in ua or 'bingbot' in ua or 'slurp' in ua:
        return 'search-engine'
    xff = request.headers.get('X-Forwarded-For')
    if xff:
        return xff.split(',')[0].strip()
    return request.remote_addr or 'unknown'

# ---------- ORIJINAL UZUN HTML (SENIN EKLEDIGIN) ----------
# Google doğrulama meta tag'ı eklendi hemen <head> içine.
HTML_CONTENT = '''<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bedava Sorgu Panel Botu 2025-2026 | Resmi Tanıtım Sitesi</title>

    <!-- Google Site Verification -->
    <meta name="google-site-verification" content="abBtwfM4CNlHI7IeT4UM_37y1brKBWo8qJI_yjGau3U" />

    <meta name="description" content="Bedava Panel Bot ile 2025-2026 güncel TC kimlik, adres, araç, mernis sorgulama. Telegram botumuz @bedeva_panelbot ve kanalımız @f3system ile ücretsiz sorgu yapın.">
    <meta name="keywords" content="mernis 2025, bedava sorgu panel, tc sorgulama, ad soyad sorgulama, adres sorgulama, 2026 sorgu panel, sorgu panel, telegram bot, bedava panel, f3system">
    
    <!-- Open Graph / Sosyal Medya -->
    <meta property="og:title" content="Bedava Sorgu Panel Botu 2025-2026">
    <meta property="og:description" content="Telegram üzerinden ücretsiz TC, adres, mernis ve daha birçok sorgu yapın.">
    <meta property="og:type" content="website">
    
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="https://img.icons8.com/color/96/000000/telegram-app.png">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Roboto:wght@300;400;500&display=swap" rel="stylesheet">
    
    <!-- Font Awesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Roboto', sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
        }
        h1, h2, h3, h4 {
            font-family: 'Poppins', sans-serif;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        a {
            text-decoration: none;
            color: inherit;
        }
        .container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        .btn {
            display: inline-block;
            padding: 12px 28px;
            border-radius: 50px;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            border: none;
            font-family: 'Poppins', sans-serif;
        }
        .btn-primary {
            background: linear-gradient(90deg, #0088cc, #00a2ff);
            color: white;
            box-shadow: 0 4px 15px rgba(0, 136, 204, 0.3);
        }
        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0, 136, 204, 0.4);
        }
        .btn-secondary {
            background-color: transparent;
            color: #0088cc;
            border: 2px solid #0088cc;
        }
        .btn-secondary:hover {
            background-color: #0088cc;
            color: white;
        }
        section {
            padding: 80px 0;
        }
        /* HEADER */
        header {
            background-color: white;
            box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 0;
        }
        .logo {
            display: flex;
            align-items: center;
            font-family: 'Poppins', sans-serif;
            font-size: 1.8rem;
            font-weight: 700;
            color: #0088cc;
        }
        .logo i {
            margin-right: 10px;
            font-size: 2rem;
        }
        nav ul {
            display: flex;
            list-style: none;
        }
        nav ul li {
            margin-left: 30px;
        }
        nav ul li a {
            font-weight: 500;
            color: #555;
            transition: color 0.3s;
        }
        nav ul li a:hover {
            color: #0088cc;
        }
        .mobile-menu-btn {
            display: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #0088cc;
        }
        /* HERO */
        .hero {
            text-align: center;
            background: linear-gradient(rgba(255,255,255,0.9), rgba(255,255,255,0.8)), url('https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80') center/cover no-repeat;
            padding: 120px 0;
        }
        .hero h1 {
            font-size: 3.5rem;
            color: #222;
            margin-bottom: 20px;
            line-height: 1.2;
        }
        .hero h1 span {
            color: #0088cc;
        }
        .hero p {
            font-size: 1.2rem;
            color: #666;
            max-width: 700px;
            margin: 0 auto 40px;
        }
        .cta-buttons {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }
        /* FEATURES */
        .features {
            background-color: white;
        }
        .section-title {
            text-align: center;
            margin-bottom: 60px;
        }
        .section-title h2 {
            font-size: 2.5rem;
            color: #222;
            position: relative;
            display: inline-block;
            padding-bottom: 15px;
        }
        .section-title h2::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 4px;
            background: linear-gradient(90deg, #0088cc, #00a2ff);
            border-radius: 2px;
        }
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 30px;
        }
        .feature-card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border-top: 5px solid #0088cc;
        }
        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        }
        .feature-card i {
            font-size: 3rem;
            color: #0088cc;
            margin-bottom: 20px;
        }
        .feature-card h3 {
            font-size: 1.5rem;
            color: #333;
        }
        .feature-card p {
            color: #777;
            margin-top: 10px;
        }
        /* HOW IT WORKS */
        .how-it-works {
            background-color: #f8f9fa;
        }
        .steps-container {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            margin-top: 50px;
            position: relative;
        }
        .step {
            text-align: center;
            flex: 1;
            min-width: 250px;
            padding: 0 15px;
            position: relative;
            margin-bottom: 30px;
        }
        .step-number {
            display: inline-block;
            width: 60px;
            height: 60px;
            line-height: 60px;
            background: linear-gradient(135deg, #0088cc, #00a2ff);
            color: white;
            border-radius: 50%;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 20px;
        }
        .step h3 {
            color: #333;
        }
        /* CTA */
        .cta {
            text-align: center;
            background: linear-gradient(135deg, #0088cc 0%, #006699 100%);
            color: white;
            padding: 100px 0;
        }
        .cta h2 {
            font-size: 2.8rem;
            margin-bottom: 20px;
        }
        .cta p {
            font-size: 1.2rem;
            max-width: 700px;
            margin: 0 auto 40px;
            opacity: 0.9;
        }
        .cta .btn {
            background-color: white;
            color: #0088cc;
        }
        .cta .btn:hover {
            background-color: #f1f1f1;
        }
        /* FOOTER */
        footer {
            background-color: #222;
            color: #bbb;
            padding: 60px 0 30px;
        }
        .footer-content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 40px;
            margin-bottom: 40px;
        }
        .footer-logo {
            font-family: 'Poppins', sans-serif;
            font-size: 1.8rem;
            font-weight: 700;
            color: white;
            margin-bottom: 20px;
            display: block;
        }
        .footer-links h4, .footer-contact h4 {
            color: white;
            margin-bottom: 20px;
            font-size: 1.2rem;
        }
        .footer-links ul {
            list-style: none;
        }
        .footer-links ul li {
            margin-bottom: 10px;
        }
        .footer-links ul li a {
            color: #bbb;
            transition: color 0.3s;
        }
        .footer-links ul li a:hover {
            color: #0088cc;
        }
        .social-icons {
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }
        .social-icons a {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            background-color: #333;
            border-radius: 50%;
            color: white;
            font-size: 1.2rem;
            transition: background-color 0.3s;
        }
        .social-icons a:hover {
            background-color: #0088cc;
        }
        .copyright {
            text-align: center;
            padding-top: 30px;
            border-top: 1px solid #444;
            font-size: 0.9rem;
            color: #888;
        }
        /* RESPONSIVE */
        @media (max-width: 992px) {
            .hero h1 {
                font-size: 2.8rem;
            }
        }
        @media (max-width: 768px) {
            .header-container {
                padding: 15px 0;
            }
            nav {
                display: none;
                position: absolute;
                top: 100%;
                left: 0;
                width: 100%;
                background-color: white;
                box-shadow: 0 10px 15px rgba(0,0,0,0.05);
                padding: 20px;
                flex-direction: column;
            }
            nav.active {
                display: flex;
            }
            nav ul {
                flex-direction: column;
            }
            nav ul li {
                margin: 10px 0;
                margin-left: 0;
            }
            .mobile-menu-btn {
                display: block;
            }
            .hero h1 {
                font-size: 2.2rem;
            }
            .hero p {
                font-size: 1rem;
            }
            .cta-buttons {
                flex-direction: column;
                align-items: center;
            }
            .btn {
                width: 100%;
                max-width: 300px;
            }
            .section-title h2 {
                font-size: 2rem;
            }
        }
        /* RATE LIMIT UYARI */
        .rate-limit-warning {
            background-color: #ffebee;
            border-left: 4px solid #f44336;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
            display: none;
        }
        .rate-limit-warning.show {
            display: block;
        }
    </style>
</head>
<body>
    <!-- HEADER -->
    <header>
        <div class="container header-container">
            <a href="#" class="logo">
                <i class="fab fa-telegram"></i> F3System Panel
            </a>
            <div class="mobile-menu-btn" id="mobileMenuBtn">
                <i class="fas fa-bars"></i>
            </div>
            <nav id="mainNav">
                <ul>
                    <li><a href="#home">Ana Sayfa</a></li>
                    <li><a href="#features">Özellikler</a></li>
                    <li><a href="#how-it-works">Nasıl Çalışır?</a></li>
                    <li><a href="#cta">Hemen Başla</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <!-- HERO SECTION -->
    <section class="hero" id="home">
        <div class="container">
            <h1>2025-2026 <span>En Güncel Sorgu Paneli</span></h1>
            <p>Telegram botumuz <strong>@bedeva_panelbot</strong> ile TC kimlik, adres, araç, mernis ve daha birçok sorguyu anlık, güvenli ve <strong>ücretsiz</strong> yapın. Resmi kanalımız: <strong>@f3system</strong></p>
            <div class="cta-buttons">
                <a href="https://t.me/bedeva_panelbot" target="_blank" class="btn btn-primary">
                    <i class="fab fa-telegram-plane"></i> Sorgu Botuna Katıl
                </a>
                <a href="https://t.me/f3system" target="_blank" class="btn btn-secondary">
                    <i class="fab fa-telegram"></i> Telegram Kanalımız
                </a>
            </div>
        </div>
    </section>

    <!-- FEATURES SECTION -->
    <section class="features" id="features">
        <div class="container">
            <div class="section-title">
                <h2>Neler Sorgulayabilirsiniz?</h2>
                <p>2025 ve 2026 güncel veritabanları ile hizmetinizdeyiz.</p>
            </div>
            <div class="features-grid">
                <div class="feature-card">
                    <i class="fas fa-id-card"></i>
                    <h3>TC Kimlik Sorgulama</h3>
                    <p>TC kimlik numarası ile ad, soyad, doğum yılı ve daha birçok bilgiye anında ulaşın.</p>
                </div>
                <div class="feature-card">
                    <i class="fas fa-home"></i>
                    <h3>Adres Sorgulama</h3>
                    <p>TC kimlik numarasından adres bilgilerini öğrenin. Güncel ve doğru adres bilgisi.</p>
                </div>
                <div class="feature-card">
                    <i class="fas fa-user-friends"></i>
                    <h3>Ad Soyad Sorgulama</h3>
                    <p>Ad ve soyad bilgisi ile kişinin temel bilgilerine erişim sağlayın.</p>
                </div>
                <div class="feature-card">
                    <i class="fas fa-database"></i>
                    <h3>Mernis 2025 Sorgu</h3>
                    <p>Mernis sistemine entegre 2025 güncel veriler ile kapsamlı sorgulama yapın.</p>
                </div>
                <div class="feature-card">
                    <i class="fas fa-car"></i>
                    <h3>Araç Sorgulama</h3>
                    <p>Plaka veya şase numarası ile araç bilgilerini, muayene durumunu öğrenin.</p>
                </div>
                <div class="feature-card">
                    <i class="fas fa-shield-alt"></i>
                    <h3>Güvenli & Hızlı</h3>
                    <p>Tamamen güvenli API bağlantıları. Sorgularınız anında cevaplanır.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- HOW IT WORKS SECTION -->
    <section class="how-it-works" id="how-it-works">
        <div class="container">
            <div class="section-title">
                <h2>Nasıl Kullanılır?</h2>
                <p>3 adımda sorgu yapmaya başlayın.</p>
            </div>
            <div class="steps-container">
                <div class="step">
                    <div class="step-number">1</div>
                    <h3>Telegram'a Girin</h3>
                    <p>Telegram uygulamanızı açın ve <strong>@bedeva_panelbot</strong> adlı botu arayın veya yandaki butona tıklayın.</p>
                </div>
                <div class="step">
                    <div class="step-number">2</div>
                    <h3>Botu Başlatın</h3>
                    <p>Botta <strong>/start</strong> komutunu gönderin. Menüden yapmak istediğiniz sorgu türünü seçin.</p>
                </div>
                <div class="step">
                    <div class="step-number">3</div>
                    <h3>Sorgunuzu Yapın</h3>
                    <p>İstenen bilgiyi (TC, plaka, ad soyad vb.) gönderin ve anında sonucu alın.</p>
                </div>
            </div>
            <div style="text-align: center; margin-top: 50px;">
                <a href="https://t.me/bedeva_panelbot" target="_blank" class="btn btn-primary" style="font-size: 1.1rem; padding: 15px 35px;">
                    <i class="fab fa-telegram-plane"></i> HEMEN BOTU AÇ VE /start YAZ
                </a>
            </div>
        </div>
    </section>

    <!-- CTA SECTION -->
    <section class="cta" id="cta">
        <div class="container">
            <h2>Ücretsiz Sorgu Yapmaya Başlayın!</h2>
            <p>Binlerce kullanıcı güvenle kullanıyor. Siz de <strong>@bedeva_panelbot</strong>'a katılın ve 2025-2026'nın en güçlü sorgu panelini deneyimleyin. Güncellemeler ve duyurular için <strong>@f3system</strong> kanalımıza abone olmayı unutmayın.</p>
            <div class="cta-buttons">
                <a href="https://t.me/bedeva_panelbot" target="_blank" class="btn">
                    <i class="fab fa-telegram-plane"></i> BOTU KULLANMAYA BAŞLA
                </a>
                <a href="https://t.me/f3system" target="_blank" class="btn btn-secondary" style="background-color: transparent; border: 2px solid white; color: white;">
                    <i class="fab fa-telegram"></i> KANALA KATIL
                </a>
            </div>
            <p style="margin-top: 30px; font-size: 0.9rem; opacity: 0.8;">
                <i class="fas fa-exclamation-circle"></i> Bot tamamen ücretsizdir. Kişisel verilerin güvenliği için SSL koruması kullanılmaktadır.
            </p>
        </div>
    </section>

    <!-- FOOTER -->
    <footer>
        <div class="container">
            <div class="footer-content">
                <div>
                    <a href="#" class="footer-logo"><i class="fab fa-telegram"></i> F3System Panel</a>
                    <p>2025-2026'nın en güncel ve güvenilir Telegram sorgu botu. Hızlı, ücretsiz ve kapsamlı sorgu deneyimi.</p>
                    <p>Resmi İletişim: <strong>@f3system</strong></p>
                    <div class="social-icons">
                        <a href="https://t.me/f3system" target="_blank" title="Telegram Kanalımız">
                            <i class="fab fa-telegram"></i>
                        </a>
                        <a href="https://t.me/bedeva_panelbot" target="_blank" title="Sorgu Botumuz">
                            <i class="fab fa-telegram-plane"></i>
                        </a>
                    </div>
                </div>
                <div class="footer-links">
                    <h4>Hızlı Linkler</h4>
                    <ul>
                        <li><a href="#home">Ana Sayfa</a></li>
                        <li><a href="#features">Özellikler</a></li>
                        <li><a href="#how-it-works">Nasıl Çalışır?</a></li>
                        <li><a href="#cta">Botu Başlat</a></li>
                    </ul>
                </div>
                <div class="footer-contact">
                    <h4>Sorgu Türleri</h4>
                    <ul>
                        <li>TC Kimlik Sorgulama</li>
                        <li>Adres Sorgulama</li>
                        <li>Ad Soyad Sorgulama</li>
                        <li>Mernis 2025 Sorgu</li>
                        <li>Araç Sorgulama</li>
                        <li>Telegram Sorgu Botu</li>
                    </ul>
                </div>
            </div>
            <div class="copyright">
                <p>&copy; 2025 - 2026 F3System Bedava Sorgu Paneli. Tüm hakları saklıdır. Bu site bir tanıtım sitesidir.</p>
                <p style="margin-top: 10px; font-size: 0.8rem;">Anahtar Kelimeler: mernis 2025, bedava sorgu panel, tc sorgulama, ad soyad sorgulama, adres sorgulama, 2026 sorgu panel, sorgu panel, telegram bot, bedava panel, f3system</p>
                <p style="margin-top: 5px; font-size: 0.7rem; color: #666;">Server Time: {{server_time}} | Requests Today: {{request_count}}</p>
            </div>
        </div>
    </footer>

    <!-- JavaScript for Mobile Menu -->
    <script>
        document.getElementById('mobileMenuBtn').addEventListener('click', function() {
            const nav = document.getElementById('mainNav');
            nav.classList.toggle('active');
            this.innerHTML = nav.classList.contains('active') ? 
                '<i class="fas fa-times"></i>' : 
                '<i class="fas fa-bars"></i>';
        });

        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                if(targetId === '#') return;
                const targetElement = document.querySelector(targetId);
                if(targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 80,
                        behavior: 'smooth'
                    });
                    // Close mobile menu if open
                    const nav = document.getElementById('mainNav');
                    const menuBtn = document.getElementById('mobileMenuBtn');
                    if(nav.classList.contains('active')) {
                        nav.classList.remove('active');
                        menuBtn.innerHTML = '<i class="fas fa-bars"></i>';
                    }
                }
            });
        });
        
        // Rate limit kontrolü
        fetch('/api/check-rate-limit')
            .then(response => response.json())
            .then(data => {
                if (data.rate_limited) {
                    const warning = document.createElement('div');
                    warning.className = 'rate-limit-warning show';
                    warning.innerHTML = `
                        <i class="fas fa-exclamation-triangle"></i>
                        <strong>Rate Limit Uyarısı:</strong> Çok fazla istek gönderdiniz. 
                        Lütfen bir süre bekleyin. Limitler: ${data.limit_info}
                    `;
                    document.body.insertBefore(warning, document.body.firstChild);
                }
            });
    </script>
</body>
</html>'''

# ---------- END ORIG HTML ----------

@app.route('/')
def index():
    client_ip = get_client_ip()
    is_search_engine = (client_ip == 'search-engine')

    # Rate limit yalnızca gerçek kullanıcılar için uygulanır
    if not is_search_engine:
        allowed = rate_limiter.is_allowed(client_ip, record=True)
        if not allowed:
            return render_template_string('''
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8"><title>Rate Limit Aşıldı</title>
                    <style>
                        body{font-family:Arial,Helvetica,sans-serif;background:#f8f9fa;color:#222;padding:40px;text-align:center}
                        .card{display:inline-block;background:#fff;padding:30px;border-radius:8px;box-shadow:0 12px 30px rgba(0,0,0,0.06);border-left:6px solid #f44336}
                        a{display:inline-block;margin-top:12px;padding:10px 18px;background:#0088cc;color:#fff;border-radius:6px;text-decoration:none}
                    </style>
                </head>
                <body>
                    <div class="card">
                        <h1>⏰ Rate Limit Aşıldı</h1>
                        <p>Çok fazla istek gönderdiniz. Lütfen 1 saat sonra tekrar deneyin.</p>
                        <p><strong>IP:</strong> {{ ip }}</p>
                        <a href="/">Ana Sayfaya Dön</a>
                    </div>
                </body>
                </html>
            ''', ip=client_ip), 429

    # Günlük sayaç sıfırlama
    today = date.today()
    if request_counter['last_reset'] != today:
        request_counter['count'] = 0
        request_counter['last_reset'] = today

    # Arama motoru isteklerini günlük sayaca dahil etme
    if not is_search_engine:
        request_counter['count'] += 1

    server_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template_string(HTML_CONTENT, server_time=server_time, request_count=request_counter['count'])

@app.route('/api/check-rate-limit')
def check_rate_limit():
    """
    Rate limit kontrolü: sadece kontrol eder, kaydetmez (record=False),
    böylece test endpoint'i istek sayısını artırmaz.
    """
    client_ip = get_client_ip()
    is_search_engine = (client_ip == 'search-engine')

    if is_search_engine:
        return jsonify({
            'rate_limited': False,
            'ip': client_ip,
            'limit_info': f'{MAX_REQUESTS} istek/{PER_SECONDS//3600} saat',
            'timestamp': datetime.now().isoformat()
        })

    allowed = rate_limiter.is_allowed(client_ip, record=False)
    return jsonify({
        'rate_limited': not allowed,
        'ip': client_ip,
        'limit_info': f'{MAX_REQUESTS} istek/{PER_SECONDS//3600} saat',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/robots.txt')
def robots():
    txt = f"""User-agent: *
Allow: /

Disallow: /admin/

Sitemap: https://{DOMAIN}/sitemap.xml
"""
    return Response(txt, mimetype='text/plain')

@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    xml_sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://paneli.art/</loc>
    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://paneli.art/#features</loc>
    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://paneli.art/#how-it-works</loc>
    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://paneli.art/#cta</loc>
    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>'''
    return xml_sitemap, 200, {'Content-Type': 'application/xml'}

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
