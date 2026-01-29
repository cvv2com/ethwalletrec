import re
import os

def extract_wallets_from_directory(directory_path='.'):
    mnemonics_file = "mnemonics.txt"
    addresses_file = "addresses.txt"
    script_name = os.path.basename(__file__)
    
    # Files to skip
    skip_files = {mnemonics_file, addresses_file, script_name}
    
    # Use sets to store unique values
    all_mnemonics = set()
    all_addresses = set()
    
    # Regex patterns
    # Capture mnemonic text until closing brace } or end of line
    mnemonic_pattern = re.compile(r'mnemonic\s*:\s*([^}\n]+)')
    address_pattern = re.compile(r'address\s*:\s*(0x[a-fA-F0-9]+)')
    
    files_scanned = 0
    
    try:
        # Walk through directory tree
        for root, dirs, files in os.walk(directory_path):
            for filename in files:
                # Skip output files and the script itself
                if filename in skip_files:
                    continue
                
                file_path = os.path.join(root, filename)
                
                try:
                    # Read file with error handling for binary/non-UTF-8 files
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    files_scanned += 1
                    
                    # 1. Extract and clean mnemonics
                    raw_mnemonics = mnemonic_pattern.findall(content)
                    for m in raw_mnemonics:
                        # Clean up line breaks and extra spaces
                        clean_m = ' '.join(m.split())
                        if clean_m:
                            all_mnemonics.add(clean_m)
                    
                    # 2. Extract ETH addresses
                    addresses = address_pattern.findall(content)
                    all_addresses.update(addresses)
                    
                except Exception as e:
                    # Skip files that can't be read
                    continue
        
        # Convert sets to sorted lists for consistent output
        clean_mnemonics = sorted(list(all_mnemonics))
        clean_addresses = sorted(list(all_addresses))
        
        # 3. Save mnemonics to file
        with open(mnemonics_file, 'w', encoding='utf-8') as f:
            for m in clean_mnemonics:
                f.write(m + '\n')
        
        # 4. Save addresses to file
        with open(addresses_file, 'w', encoding='utf-8') as f:
            for addr in clean_addresses:
                f.write(addr + '\n')
        
        print(f"İşlem Tamamlandı!")
        print(f"-----------------")
        print(f"Taranan Dosya Sayısı    : {files_scanned}")
        print(f"Bulunan Mnemonic Sayısı : {len(clean_mnemonics)} -> '{mnemonics_file}' dosyasına kaydedildi.")
        print(f"Bulunan Adres Sayısı    : {len(clean_addresses)} -> '{addresses_file}' dosyasına kaydedildi.")
    
    except Exception as e:
        print(f"Bir hata oluştu: {e}")

if __name__ == "__main__":
    # Scan current directory and all subdirectories
    extract_wallets_from_directory('.')
