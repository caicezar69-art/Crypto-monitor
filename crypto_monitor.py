import os
import requests
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# === Moedas principais + tendências de novembro 2026 ===
COINS = {
    # Blue chips
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",

    # Tendências fortes (nov/2026)
    "hyperliquid": "HYPE",          # DeFi / Perps
    "zcash": "ZEC",                 # Privacidade
    "near": "NEAR",                 # AI + infraestrutura
    "venice-token": "VVV",          # AI privada
    "bittensor": "TAO",             # Decentralized AI
    "pudgy-penguins": "PENGU",      # Memes / NFT
    "pepe": "PEPE",                 # Meme
    "just": "JST",                  # TRON DeFi
    "initia": "INIT",               # Forte momentum recente
}

# Lançamentos recentes (novembro 2026)
NEW_LAUNCHES = {
    "kor-protocol": "KOR",
    # Adicione outros IDs do CoinGecko conforme forem listados
}

def get_prices(coin_ids: list):
    ids = ",".join(coin_ids)
    url = (
        f"https://api.coingecko.com/api/v3/simple/price"
        f"?ids={ids}&vs_currencies=usd,brl&include_24hr_change=true"
    )
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json()

def send_telegram(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Tokens do Telegram não configurados")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    print("Mensagem enviada com sucesso!")

def format_section(title: str, data: dict, coins: dict) -> str:
    section = f"*{title}*\n"
    for coin_id, symbol in coins.items():
        info = data.get(coin_id)
        if not info:
            continue
        price_usd = info.get("usd", 0)
        price_brl = info.get("brl", 0)
        change = info.get("usd_24h_change", 0)
        emoji = "🟢" if change >= 0 else "🔴"

        section += (
            f"`{symbol}`  \( {price_usd:,.4f}  |  R \) {price_brl:,.2f}\n"
            f"   24h: {emoji} `{change:+.2f}%`\n"
        )
    return section + "\n"

def generate_alerts(data: dict) -> list:
    """Gera alertas de movimentos tendenciosos"""
    alerts = []

    # Configuração de sensibilidade (pode ajustar)
    thresholds = {
        "bitcoin": 3.5,        # BTC mais sensível
        "ethereum": 4.5,
        "solana": 5.0,
        "hyperliquid": 7.0,    # HYPE costuma ser volátil
        "zcash": 6.0,
        "near": 6.0,
        "venice-token": 8.0,
        "bittensor": 7.0,
        "pudgy-penguins": 8.0,
        "pepe": 9.0,
        "just": 6.0,
        "initia": 10.0,        # tokens novos costumam oscilar mais
        "kor-protocol": 12.0,
    }

    for coin_id, threshold in thresholds.items():
        info = data.get(coin_id)
        if not info:
            continue

        change = info.get("usd_24h_change")
        if change is None:
            continue

        symbol = COINS.get(coin_id) or NEW_LAUNCHES.get(coin_id) or coin_id.upper()

        if change <= -threshold:
            alerts.append(f"🔻 *{symbol}* caiu `{change:.1f}%` (forte movimento de baixa)")
        elif change >= threshold:
            alerts.append(f"🚀 *{symbol}* subiu `{change:+.1f}%` (movimento de alta forte)")

    return alerts

def main():
    try:
        all_ids = list(COINS.keys()) + list(NEW_LAUNCHES.keys())
        data = get_prices(all_ids)

        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        message = f"📊 *Monitor Cripto Tendências* — {now}\n\n"

        # Seção de tendências
        message += format_section("🔥 Tendências Nov/2026", data, COINS)

        # Seção de lançamentos
        message += format_section("🚀 Lançamentos Recentes", data, NEW_LAUNCHES)

        # Alertas de movimentos tendenciosos
        alerts = generate_alerts(data)

        if alerts:
            message += "*⚡ Movimentos Tendenciosos Detectados:*\n"
            message += "\n".join(alerts) + "\n\n"
        else:
            message += "_Nenhum movimento extremo detectado nas últimas 24h._\n\n"

        message += "_Fonte: CoinGecko | Atualizado automaticamente via GitHub Actions_"

        send_telegram(message)
        print("Monitoramento concluído com sucesso")

    except Exception as e:
        error_msg = f"❌ Erro no monitor de cripto:\n`{str(e)}`"
        print(error_msg)
        try:
            send_telegram(error_msg)
        except:
            pass

if __name__ == "__main__":
    main()
