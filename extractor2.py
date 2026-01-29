import re

def extract_wallets(input_file_path):
    mnemonics_file = "mnemonics.txt"
    addresses_file = "addresses.txt"

    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Mnemonic'leri bulma ve temizleme
        # Regex: mnemonic : ile başlayıp } işaretine kadar olanı alır
        mnemonic_pattern = re.compile(r'mnemonic\s*:\s*([^}]+)')
        raw_mnemonics = mnemonic_pattern.findall(content)
        
        clean_mnemonics = []
        for m in raw_mnemonics:
            # Satır sonlarını ve fazla boşlukları temizleyip tek satıra indirir
            clean_m = ' '.join(m.split())
            if clean_m:
                clean_mnemonics.append(clean_m)

        # 2. ETH Adreslerini bulma
        # Regex: address : ile başlayıp virgüle kadar olanı veya 0x ile başlayan 42 karakteri alır
        address_pattern = re.compile(r'address\s*:\s*(0x[a-fA-F0-9]+)')
        clean_addresses = address_pattern.findall(content)

        # 3. Mnemonic'leri kaydetme
        with open(mnemonics_file, 'w', encoding='utf-8') as f:
            for m in clean_mnemonics:
                f.write(m + '\n')

        # 4. Adresleri kaydetme
        with open(addresses_file, 'w', encoding='utf-8') as f:
            for addr in clean_addresses:
                f.write(addr + '\n')

        print(f"İşlem Tamamlandı!")
        print(f"-----------------")
        print(f"Bulunan Mnemonic Sayısı : {len(clean_mnemonics)} -> '{mnemonics_file}' dosyasına kaydedildi.")
        print(f"Bulunan Adres Sayısı    : {len(clean_addresses)} -> '{addresses_file}' dosyasına kaydedildi.")

    except FileNotFoundError:
        print(f"Hata: '{input_file_path}' dosyası bulunamadı.")
    except Exception as e:
        print(f"Bir hata oluştu: {e}")

if __name__ == "__main__":
    # Log dosyanızın adı
    LOG_DOSYASI = 'logs.txt'
    
    extract_wallets(LOG_DOSYASI)
