import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import time

def process_file(file_path, mnemonic_pattern, address_pattern):
    """
    Process a single file and extract mnemonics and addresses.
    Returns a tuple: (mnemonics_set, addresses_set)
    """
    mnemonics = set()
    addresses = set()
    
    try:
        # Read file with error handling for binary/non-UTF-8 files
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Extract and clean mnemonics
        raw_mnemonics = mnemonic_pattern.findall(content)
        for m in raw_mnemonics:
            # Clean up line breaks and extra spaces
            clean_m = ' '.join(m.split())
            if clean_m:
                mnemonics.add(clean_m)
        
        # Extract ETH addresses
        addresses_found = address_pattern.findall(content)
        addresses.update(addresses_found)
        
    except Exception as e:
        # Skip files that can't be read
        pass
    
    return (mnemonics, addresses)

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
    
    # Thread safety lock for aggregating results
    results_lock = Lock()
    files_scanned = 0
    
    # Collect all file paths to process
    files_to_process = []
    for root, dirs, files in os.walk(directory_path):
        for filename in files:
            # Skip output files and the script itself
            if filename in skip_files:
                continue
            file_path = os.path.join(root, filename)
            files_to_process.append(file_path)
    
    total_files = len(files_to_process)
    print(f"Found {total_files} files to scan. Starting processing...")
    
    try:
        # Process files in parallel using ThreadPoolExecutor
        max_workers = min(32, (os.cpu_count() or 1) * 4)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all file processing tasks
            future_to_file = {
                executor.submit(process_file, file_path, mnemonic_pattern, address_pattern): file_path
                for file_path in files_to_process
            }
            
            # Process completed tasks and aggregate results
            for future in as_completed(future_to_file):
                mnemonics, addresses = future.result()
                
                # Thread-safe aggregation of results
                with results_lock:
                    all_mnemonics.update(mnemonics)
                    all_addresses.update(addresses)
                    files_scanned += 1
                    
                    # Print progress every 100 files or at completion
                    if files_scanned % 100 == 0 or files_scanned == total_files:
                        print(f"Progress: {files_scanned}/{total_files} files processed...")
        
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
