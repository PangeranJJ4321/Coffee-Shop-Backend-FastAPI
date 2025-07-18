"""seed_coffee_menu_items

Revision ID: 10672d139a75
Revises: 67a53224a564'
Create Date: 2025-05-29 01:04:35.480149

"""
from datetime import datetime
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy import Text, Boolean, Integer, String, Float


# revision identifiers, used by Alembic.
revision: str = '10672d139a75'
down_revision: Union[str, None] = '67a53224a564'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Define table references
menu_items_table = table(
    'coffee_menus',
    column('id', UUID),
    column('name', String),
    column('price', Integer),
    column('description', Text),
    column('image_url', String),
    column('is_available', Boolean),
    column('average_rating', Float),
    column('total_ratings', Integer),
    column('long_description', Text),
    column('category', String),
    column('featured', Boolean), 
    column('tags', ARRAY(String)),
    column('preparation_time', String),
    column('caffeine_content', String),
    column('origin', String),
    column('roast_level', String),
    column('coffee_shop_id', UUID),
    column('created_at', sa.DateTime),
    column('updated_at', sa.DateTime),
)

coffee_variants_table = table(
    'coffee_variants',
    column('id', UUID),
    column('coffee_id', UUID),
    column('variant_id', UUID),
    column('is_default', Boolean),
    column('created_at', sa.DateTime),
    column('updated_at', sa.DateTime),
)

# Perbaiki casing category agar sesuai dengan frontend dan backend enum (jika ada)
# Pastikan nama-nama varian dan tipe varian juga sesuai persis dengan yang ada di DB.
menus_data_for_seed = [
    {
        "name": "Espresso Premium",
        "price": 25000,
        "description": "Kopi espresso dengan cita rasa yang kuat dan aroma yang menggugah selera.",
        "long_description": "Espresso Premium kami adalah hasil dari perpaduan sempurna antara tradisi dan inovasi. Menggunakan biji kopi arabica grade A yang dipetik langsung dari perkebunan terbaik di dataran tinggi Jawa Barat. Proses roasting dilakukan dengan hati-hati untuk menghasilkan profil rasa yang kompleks dengan notes cokelat gelap, karamel, dan sedikit sentuhan buah-buahan. Setiap shot espresso diekstrak dengan presisi menggunakan mesin espresso profesional untuk menghasilkan crema yang sempurna.",
        "is_available": True,
        "category": "COFFEE", 
        "featured": True,
        "tags": ["strong", "classic", "arabica", "premium"],
        "preparation_time": "3-5 menit",
        "caffeine_content": "Tinggi",
        "origin": "Jawa Barat, Indonesia",
        "roast_level": "Medium Dark"
    },
    {
        "name": "Cappuccino Spesial",
        "price": 32000,
        "description": "Perpaduan sempurna antara espresso, steamed milk, dan foam yang lembut.",
        "long_description": "Cappuccino spesial kami dibuat dengan satu shot espresso premium, susu segar yang di-steam hingga halus, dan lapisan foam lembut di atasnya. Disajikan dalam cangkir 6oz, minuman ini menawarkan keseimbangan sempurna antara kekuatan kopi dan kelembutan susu, dengan sedikit taburan bubuk cokelat di atasnya.",
        "is_available": True,
        "category": "COFFEE", 
        "featured": False,
        "tags": ["milk", "foam", "balanced", "classic"],
        "preparation_time": "4-6 menit",
        "caffeine_content": "Sedang",
        "origin": "Campuran",
        "roast_level": "Medium"
    },
    {
        "name": "Latte Art Classic",
        "price": 35000,
        "description": "Latte dengan seni foam yang indah, cocok untuk pecinta kopi dan seni.",
        "long_description": "Setiap Latte Art Classic kami adalah sebuah karya seni. Barista kami dengan ahli menuangkan susu yang di-steam untuk menciptakan pola indah di permukaan kopi Anda. Dibuat dengan double shot espresso dan susu pilihan, memberikan rasa creamy yang nikmat dengan sentuhan pahit dari kopi.",
        "is_available": True,
        "featured": False,
        "category": "COFFEE", 
        "tags": ["art", "milk", "sweet", "creamy"],
        "preparation_time": "5-7 menit",
        "caffeine_content": "Sedang",
        "origin": "Campuran",
        "roast_level": "Medium"
    },
    {
        "name": "Americano Dingin",
        "price": 28000,
        "description": "Kopi hitam dingin yang menyegarkan, perfect untuk cuaca panas.",
        "long_description": "Americano Dingin kami adalah pilihan sempurna untuk menyegarkan diri di hari yang panas. Double shot espresso yang pekat dicampur dengan air dingin dan disajikan dengan es batu. Rasanya yang bold dan bersih tanpa tambahan susu atau gula (opsional).",
        "is_available": True,
        "featured": False,
        "category": "ICED",  
        "tags": ["cold", "refreshing", "black", "simple"],
        "preparation_time": "2-3 menit",
        "caffeine_content": "Tinggi",
        "origin": "Campuran",
        "roast_level": "Dark"
    },
    {
        "name": "Matcha Latte Panas",
        "price": 33000,
        "description": "Minuman non-kopi dengan bubuk matcha premium dari Jepang.",
        "long_description": "Matcha Latte Panas kami dibuat dari bubuk matcha kualitas upacara dari Jepang, dicampur dengan susu pilihan yang di-steam hingga creamy. Memberikan rasa umami yang khas dengan sentuhan manis yang seimbang. Pilihan tepat untuk relaksasi.",
        "is_available": True,
        "featured": False,
        "category": "NON_COFFEE", 
        "tags": ["matcha", "japanese", "healthy", "warm"],
        "preparation_time": "4-6 menit",
        "caffeine_content": "Sedang (teh)",
        "origin": "Jepang",
        "roast_level": "N/A"
    },
    {
        "name": "Hot Chocolate Fudge",
        "price": 30000,
        "description": "Cokelat panas yang rich dan creamy, cocok untuk pecinta cokelat.",
        "long_description": "Nikmati kehangatan dan kekayaan Hot Chocolate Fudge kami. Dibuat dengan cokelat premium leleh dan susu kental, diakhiri dengan whipped cream dan taburan cokelat. Kenikmatan manis yang sempurna di setiap tegukan.",
        "is_available": True,
        "featured": False,
        "category": "NON_COFFEE", 
        "tags": ["chocolate", "sweet", "creamy", "indulgent"],
        "preparation_time": "5-8 menit",
        "caffeine_content": "Rendah",
        "origin": "Eropa",
        "roast_level": "N/A"
    }
]


def upgrade():
    now = datetime.utcnow()
    # Pastikan coffee_shop_id ini ada di tabel coffee_shops Anda
    coffee_shop_id = 'ed634a6f-c12d-4ed4-8975-1926a2ee4a43' 

    conn = op.get_bind()
    
    # Ambil ID variant_types dan variants dari database
    # Pastikan nama 'Size', 'Sugar Level', 'Milk Type', 'Temperature' ada di tabel variant_types
    results = conn.execute(sa.text("SELECT id, name FROM variant_types")).fetchall()
    variant_type_ids_map_from_db = {row.name: str(row.id) for row in results}

    results = conn.execute(sa.text("SELECT id, name, variant_type_id FROM variants")).fetchall()
    variant_ids_map_from_db = {
        (row.name, str(row.variant_type_id)): str(row.id) for row in results # Cast variant_type_id to str
    }

    # Dapatkan ID spesifik varian untuk koneksi
    # Pastikan nama-nama ini ada di tabel `variants` dengan `variant_type_id` yang benar.
    size_medium_id = variant_ids_map_from_db.get(('Medium', variant_type_ids_map_from_db.get('Size')))
    sugar_normal_id = variant_ids_map_from_db.get(('Normal Sugar', variant_type_ids_map_from_db.get('Sugar Level')))
    milk_regular_id = variant_ids_map_from_db.get(('Regular Milk', variant_type_ids_map_from_db.get('Milk Type'))) # Added for completeness
    temp_hot_id = variant_ids_map_from_db.get(('Hot', variant_type_ids_map_from_db.get('Temperature')))
    temp_cold_id = variant_ids_map_from_db.get(('Iced', variant_type_ids_map_from_db.get('Temperature'))) # <-- Biasanya ini 'Iced' jika di type Temperature

    menu_items_data = []
    coffee_variants_data = []

    for menu in menus_data_for_seed:
        coffee_id = str(uuid.uuid4())
        # image_url default ke None jika tidak ada di dict menu
        image_url = f"/images/{menu['name'].lower().replace(' ', '-')}.jpg" # Contoh path gambar lokal

        menu_items_data.append({
            'id': coffee_id,
            'name': menu['name'],
            'price': menu['price'],
            'description': menu['description'],
            'image_url': image_url, # Gunakan image_url yang sudah ditentukan
            'is_available': menu['is_available'],
            'average_rating': 0.0,
            'total_ratings': 0,
            'long_description': menu['long_description'],
            'category': menu['category'],
            'featured': menu['featured'], # Gunakan nilai featured dari data
            'tags': menu['tags'],
            'preparation_time': menu['preparation_time'],
            'caffeine_content': menu['caffeine_content'],
            'origin': menu['origin'],
            'roast_level': menu['roast_level'],
            'coffee_shop_id': coffee_shop_id,
            'created_at': now,
            'updated_at': now
        })

        # Koneksi varian default yang relevan untuk setiap menu
        # Anda mungkin perlu logika yang lebih spesifik di sini
        # untuk memastikan varian yang tepat terhubung ke setiap kopi.

        # Contoh: Koneksi varian dasar untuk semua kopi
        if size_medium_id:
            coffee_variants_data.append({
                'id': str(uuid.uuid4()), 'coffee_id': coffee_id, 'variant_id': size_medium_id,
                'is_default': True, 'created_at': now, 'updated_at': now
            })
        if sugar_normal_id:
            coffee_variants_data.append({
                'id': str(uuid.uuid4()), 'coffee_id': coffee_id, 'variant_id': sugar_normal_id,
                'is_default': True, 'created_at': now, 'updated_at': now
            })
        
        # Logika suhu: jika nama menu mengandung "Dingin" -> Cold, selain itu -> Hot
        if "Dingin" in menu['name'] and temp_cold_id:
            coffee_variants_data.append({
                'id': str(uuid.uuid4()), 'coffee_id': coffee_id, 'variant_id': temp_cold_id,
                'is_default': True, 'created_at': now, 'updated_at': now
            })
        elif temp_hot_id: # Untuk semua menu panas lainnya
            coffee_variants_data.append({
                'id': str(uuid.uuid4()), 'coffee_id': coffee_id, 'variant_id': temp_hot_id,
                'is_default': True, 'created_at': now, 'updated_at': now
            })
        
        # Contoh spesifik untuk Cappuccino Spesial atau Matcha Latte Panas
        if menu['name'] == "Cappuccino Spesial" and milk_regular_id:
            coffee_variants_data.append({
                'id': str(uuid.uuid4()), 'coffee_id': coffee_id, 'variant_id': milk_regular_id,
                'is_default': True, 'created_at': now, 'updated_at': now
            })
        elif menu['name'] == "Matcha Latte Panas" and milk_regular_id: # Atau jenis susu default lain
             coffee_variants_data.append({
                'id': str(uuid.uuid4()), 'coffee_id': coffee_id, 'variant_id': milk_regular_id,
                'is_default': True, 'created_at': now, 'updated_at': now
            })


    op.bulk_insert(menu_items_table, menu_items_data)
    op.bulk_insert(coffee_variants_table, coffee_variants_data)


def downgrade():
    menu_names = [menu['name'] for menu in menus_data_for_seed]
    # Menggunakan parameterized execute untuk downgrade
    op.execute(sa.text("""
        DELETE FROM coffee_variants
        WHERE coffee_id IN (
            SELECT id FROM coffee_menus WHERE name = ANY(:menu_names)
        )
    """), {'menu_names': menu_names})

    op.execute(sa.text("DELETE FROM coffee_menus WHERE name = ANY(:menu_names)"), {'menu_names': menu_names})