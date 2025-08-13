from flask import Flask, render_template, jsonify, send_from_directory
import fitz  # PyMuPDF
import os
import json
from pathlib import Path

app = Flask(__name__)

# Конфигурация
PDF_PATH = "SPARE PARTS CATALOGUE EVO12-16 2023.pdf"
EXTRACTED_IMAGES_DIR = "static/images/extracted"
IMAGE_MAPPING_FILE = "image_mapping.json"

# Сопоставление REF номеров с позициями в PDF
REF_MAPPING = {
    "ED018": {"page": 4, "index": 0, "description": "Fusible 500mA 250V"},
    "ED019": {"page": 4, "index": 1, "description": "Fusible 10A 250V"},
    "ED020": {"page": 4, "index": 2, "description": "FUSE 1A 250V"},
    "ED021": {"page": 4, "index": 3, "description": "Relay 24V"},
    "K190753-2": {"page": 4, "index": 4, "description": "Tracking Board"},
    "K200609-1A": {"page": 4, "index": 5, "description": "Tracking Board (2020)"},
    "K108019": {"page": 5, "index": 0, "description": "PC104 Board"},
    "K190777-1": {"page": 5, "index": 1, "description": "Encoder board"},
    "K190801-1": {"page": 6, "index": 0, "description": "Intcam Board Analogic type 1"},
    "K190801-2": {"page": 6, "index": 1, "description": "Intcam Board Analogic type 2"},
    "K190801-3": {"page": 6, "index": 2, "description": "Intcam Board Analogic type 3"},
    "K191188": {"page": 6, "index": 3, "description": "Numeric Intcam Board"},
    "K190874": {"page": 6, "index": 4, "description": "Spider 1 Board V1"},
    "K190874-1B": {"page": 7, "index": 0, "description": "Spider 1Board V2"},
    "K190877": {"page": 7, "index": 1, "description": "Spider 1Board V2"},
    "K191195-1": {"page": 7, "index": 2, "description": "Spider 2Board"},
    "K260301-0": {"page": 7, "index": 3, "description": "Spider 2Board NG (2022)"},
    "ED790": {"page": 7, "index": 4, "description": "Power supply 24V +/-15V"},
    "ED789": {"page": 7, "index": 5, "description": "Power supply 24V 5V"},
    "ED804": {"page": 8, "index": 0, "description": "Power supply E230V S+24V 12.5A 300W"},
    "ED501": {"page": 8, "index": 1, "description": "Power supply E230V S+12V 13A156W"},
    "ED619": {"page": 8, "index": 2, "description": "Air conditionning 1500W"},
    "ED576": {"page": 8, "index": 3, "description": "Ethernet Module"},
    "ED611": {"page": 8, "index": 4, "description": "Uninterruptible power supply (UPS)"},
    "K215409": {"page": 9, "index": 0, "description": "HD LCD Panel (21.5inches)"},
    "KLP2105": {"page": 9, "index": 1, "description": "LCD Panel"},
    "HV316": {"page": 9, "index": 2, "description": "Iris computer HD"},
    "HV305": {"page": 9, "index": 3, "description": "Iris computer HD"},
    "HV312": {"page": 9, "index": 4, "description": "Iris computer HD"},
    "HV316NEO": {"page": 10, "index": 0, "description": "Iris computer HD NEO"},
    "HV312NEO": {"page": 10, "index": 1, "description": "Iris computer HD NEO"},
    "HV006T": {"page": 10, "index": 2, "description": "Vision board"},
    "XE019": {"page": 10, "index": 3, "description": "Vision board fun"},
    "HV156": {"page": 10, "index": 4, "description": "Graphic board NG PC"},
    "K190200": {"page": 11, "index": 0, "description": "Acquisition board"},
    "HV095": {"page": 11, "index": 1, "description": "Analogic Solios board"},
    "K300100": {"page": 11, "index": 2, "description": "2 Serial links board"},
    "ED885": {"page": 11, "index": 3, "description": "Disque dur (1To)"},
    "HV129": {"page": 11, "index": 4, "description": "Encryption dongle"},
    "HV183": {"page": 11, "index": 5, "description": "Encryption dongle"},
    "ED586": {"page": 11, "index": 6, "description": "HD PC power supply"},
    "K182193": {"page": 12, "index": 0, "description": "Encoder cable Evo12length10m"},
    "HCBL162": {"page": 12, "index": 1, "description": "Cell cable 5m"},
    "K181383-300C": {"page": 12, "index": 2, "description": "Camera cable Teli CS8560 3m"},
    "K181383-500C": {"page": 12, "index": 3, "description": "Camera cable Teli CS8560 5m"},
    "HV340": {"page": 18, "index": 0, "description": "HD Camera EV16type 3(a2A)"},
    "HV150": {"page": 19, "index": 0, "description": "6 mm focal lens"},
    "HV155": {"page": 19, "index": 1, "description": "8 mm focal lens"},
    "HV160": {"page": 19, "index": 2, "description": "12mm focal lens"},
    "HV163": {"page": 19, "index": 3, "description": "16mmfocal lens"},
    "HV166": {"page": 19, "index": 4, "description": "25 mm focal lens"},
    "MK500497": {"page": 18, "index": 1, "description": "Full set neon light source"},
    "MK500395": {"page": 21, "index": 0, "description": "SET Encoder+ support+ cable"},
    "ED303": {"page": 21, "index": 1, "description": "Encoder 24V"},
    "ED024": {"page": 21, "index": 2, "description": "63mm encoderwheel"},
    "MR018": {"page": 21, "index": 3, "description": "Encoder coupling"},
    "ESP021": {"page": 22, "index": 0, "description": "Standard Spacer version 2"},
    "ESP022": {"page": 22, "index": 1, "description": "Easy set Spacer version 1"},
    "ESP012": {"page": 23, "index": 0, "description": "Long spacer standard"},
    "MK200616": {"page": 30, "index": 0, "description": "Compiet reject and support"},
    "PM011": {"page": 30, "index": 1, "description": "Reject valve 3/2"}
}

def extract_images():
    """Извлекает изображения из PDF и сохраняет их"""
    if not os.path.exists(PDF_PATH):
        print(f"Файл {PDF_PATH} не найден!")
        return False
    
    # Создаем директорию для изображений
    Path(EXTRACTED_IMAGES_DIR).mkdir(parents=True, exist_ok=True)
    
    try:
        doc = fitz.open(PDF_PATH)
        
        for ref, info in REF_MAPPING.items():
            page_num = info["page"]
            img_index = info["index"]
            
            if page_num < len(doc):
                page = doc[page_num]
                image_list = page.get_images()
                
                if img_index < len(image_list):
                    img = image_list[img_index]
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Сохраняем с именем REF номера
                    image_filename = f"{ref}.{image_ext}"
                    image_path = os.path.join(EXTRACTED_IMAGES_DIR, image_filename)
                    
                    with open(image_path, "wb") as image_file:
                        image_file.write(image_bytes)
        
        doc.close()
        return True
        
    except Exception as e:
        print(f"Ошибка при извлечении изображений: {e}")
        return False

@app.route('/')
def index():
    # Проверяем и извлекаем изображения при первом запуске
    if not os.path.exists(EXTRACTED_IMAGES_DIR) or not os.listdir(EXTRACTED_IMAGES_DIR):
        extract_images()
    
    # Группируем детали по категориям
    categories = {
        "electronics": {k: v for k, v in REF_MAPPING.items() if k.startswith(('ED', 'K19', 'K20', 'K26'))},
        "pc-iris": {k: v for k, v in REF_MAPPING.items() if k.startswith(('HV', 'K21'))},
        "cables": {k: v for k, v in REF_MAPPING.items() if k.startswith('K18')},
        "optics": {k: v for k, v in REF_MAPPING.items() if k.startswith(('HV0', 'MK50'))},
        "encoder": {k: v for k, v in REF_MAPPING.items() if k.startswith(('MK500395', 'ED303', 'ED024', 'MR018'))},
        "spacer": {k: v for k, v in REF_MAPPING.items() if k.startswith('ESP')},
        "pneumatic": {k: v for k, v in REF_MAPPING.items() if k.startswith(('MK200616', 'PM'))},
        "others": {k: v for k, v in REF_MAPPING.items() if k.startswith(('CA', 'XE', 'ED05', 'ED16'))}
    }
    
    return render_template('index.html', categories=categories)

@app.route('/api/search/<ref>')
def search_part(ref):
    """API для поиска детали по REF"""
    part = REF_MAPPING.get(ref.upper())
    if part:
        image_path = f"/{EXTRACTED_IMAGES_DIR}/{ref}.{get_image_extension(ref)}"
        return jsonify({
            "found": True,
            "part": part,
            "image": image_path
        })
    return jsonify({"found": False})

def get_image_extension(ref):
    """Определяет расширение файла изображения"""
    for ext in ['jpg', 'jpeg', 'png', 'gif']:
        if os.path.exists(os.path.join(EXTRACTED_IMAGES_DIR, f"{ref}.{ext}")):
            return ext
    return 'jpg'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)