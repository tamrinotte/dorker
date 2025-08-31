# Dorker

![Dorker](https://raw.githubusercontent.com/tamrinotte/dorker/main/app_images/dorker_logo.png)

Dorker is an advanced reconnaissance tool that automates the use of Google Dorks to discover publicly exposed sensitive information related to a target. It supports both domain-based and personal/company/event name-based queries, provides progress feedback, takes screenshots of search results.

<br>

## Installation

1. Download the installer.

   * Kali

         curl -L https://github.com/tamrinotte/dorker/releases/download/kali_v0.1.3/dorker.deb -o dorker.deb

2. Start the installer.

       sudo dpkg -i dorker.deb

<br>

## Options

**-h, --help:** Displays the help message.

**target:** Name or domain to be searched (e.g., `example.com` or `John Doe`).

**-hl, --headless:** Run browser in headless mode for stealth operation.

**-gd GECKODRIVER, --geckodriver GECKODRIVER:** Optional path to a GeckoDriver binary. If not provided, Selenium will auto-manage it.

**-min MIN_DELAY, --min_delay MIN_DELAY:** Optional minimum delay (in seconds) between searches to simulate human-like behavior (default: 0).

**-max MAX_DELAY, --max_delay MAX_DELAY:** Optional maximum delay (in seconds) between searches to simulate human-like behavior (default: 1).

<br>

## Examples

1. Scan a person or company name using DuckDuckGo:

       dorker example.com

2. Scan a domain using DuckDuckGo:

       dorker "John Doe"

3. Specify a custom GeckoDriver path:

       dorker example.com -gd /home/bob/geckodriver

4. Scan a person or company name using Startpage:

       dorker "John Doe" -e startpage

<br>

---

# Dorker

![Dorker](https://raw.githubusercontent.com/tamrinotte/dorker/main/app_images/dorker_logo.png)

Dorker, bir hedefe ait herkese açık hassas bilgileri otomatik olarak Google Dork sorgularıyla tespit eden gelismis bir keşif aracıdır. Alan adı ve kişi/şirket/etkinlik adı tabanlı aramaları destekler, ilerleme durumu gösterir, arama sonuçlarının ekran görüntülerini alır.

<br>

## Kurulum

1. Yükleyiciyi indirin.

   * Kali

         curl -L https://github.com/tamrinotte/dorker/releases/download/kali_v0.1.3/dorker.deb -o dorker.deb

2. Yükleyiciyi başlatın.

       sudo dpkg -i dorker.deb

<br>

## Seçenekler

**-h, --help:** Yardım mesajını görüntüler.

**target:** Aranacak kişi adı veya alan adı ("example.com" ya da "John Doe" gibi).

**-hl, --headless:** Tarayıcıyı başlıksız modda çalıştır.

**-gd GECKODRIVER, --geckodriver GECKODRIVER:** GeckoDriver binary dosyasının isteğe konumu. Sağlanmazsa, Selenium bunu otomatik olarak halledecektir.

**-min MIN_DELAY, --min_delay MIN_DELAY:** Aramalar arasında insan benzeri davranışı taklit etmek için isteğe bağlı minimum gecikme (saniye cinsinden) (varsayılan: 0).

**-max MAX_DELAY, --max_delay MAX_DELAY:** Aramalar arasında insan benzeri davranışı taklit etmek için isteğe bağlı maksimum gecikme (saniye cinsinden) (varsayılan: 1).

<br>

## Örnekler

1. DuckDuckGo'yu kullanarak bir kişi veya şirket adını tarayın:

       dorker example.com

2. DuckDuckGo kullanarak bir alan adını tarayın:

       dorker "John Doe"

3. Özel bir GeckoDriver yolu belirtin:

       dorker example.com -gd /home/bob/geckodriver

4. Startpage'ı kullanarak bir kişi veya şirket adını tarayın:

       dorker "John Doe" -e startpage
