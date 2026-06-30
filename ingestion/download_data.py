import os
import shutil

import kagglehub

print("Veri indiriliyor...")
path = kagglehub.dataset_download("olistbr/brazilian-ecommerce")
print("İndirilen konum:", path)

hedef = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(hedef, exist_ok=True)

for dosya in os.listdir(path):
    if dosya.endswith(".csv"):
        shutil.copy(os.path.join(path, dosya), os.path.join(hedef, dosya))
        print("Kopyalandı:", dosya)

print("Bitti. Tüm CSV'ler data/ klasöründe.")