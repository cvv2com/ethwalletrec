from web3 import Web3
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_balances(input_file, output_file):
    # RPC URL - Öncelikle .env dosyasından çekilir, yoksa public LlamaRPC kullanılır
    # Daha hızlı sonuç için .env dosyasına kendi Infura veya Alchemy URL'nizi ekleyin:
    # ETH_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
    rpc_url = os.getenv("ETH_RPC_URL", "https://eth.llamarpc.com") 
    
    w3 = Web3(Web3.HTTPProvider(rpc_url))

    if not w3.is_connected():
        print("Blockchain ağına bağlanılamadı. RPC URL'sini kontrol edin.")
        return

    print(f"Bağlantı Başarılı! Aktif Blok Numarası: {w3.eth.block_number}")
    
    try:
        with open(input_file, 'r') as f:
            addresses = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Hata: {input_file} dosyası bulunamadı.")
        return

    rich_wallets = []
    
    print(f"Toplam {len(addresses)} adres kontrol edilecek...")
    print("-" * 50)

    for i, address in enumerate(addresses, 1):
        try:
            # Adresin formatını (checksum) doğrula
            checksum_address = Web3.to_checksum_address(address)
            
            # Bakiyeyi Wei cinsinden al (1 ETH = 10^18 Wei)
            balance_wei = w3.eth.get_balance(checksum_address)
            
            # Wei'yi ETH'ye çevir
            balance_eth = w3.from_wei(balance_wei, 'ether')

            status = f"[{i}/{len(addresses)}] {address} : {balance_eth:.6f} ETH"
            
            if balance_eth > 0:
                print(f"💰 BULUNDU! -> {status}")
                rich_wallets.append(f"{address} | {balance_eth} ETH")
            else:
                print(status)
            
            # Sunucuyu yormamak için kısa bir bekleme (rate limit)
            time.sleep(0.2)

        except Exception as e:
            print(f"Hata ({address}): {e}")

    # Bakiyesi olanları dosyaya kaydet
    if rich_wallets:
        with open(output_file, 'w') as f:
            for wallet in rich_wallets:
                f.write(wallet + '\n')
        print("-" * 50)
        print(f"Tebrikler! Bakiyesi olan {len(rich_wallets)} cüzdan '{output_file}' dosyasına kaydedildi.")
    else:
        print("-" * 50)
        print("Maalesef, kontrol edilen cüzdanlarda bakiye bulunamadı.")

if __name__ == "__main__":
    GIRIS_DOSYASI = "addresses.txt"
    CIKTI_DOSYASI = "rich_wallets.txt"
    
    check_balances(GIRIS_DOSYASI, CIKTI_DOSYASI)
