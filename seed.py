from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.schema import Base, CatalogDB

def seed_food_beverage_catalogs():
    db: Session = SessionLocal()
    
    # Clear existing catalog data before re-seeding
    db.query(CatalogDB).delete()
    db.commit()

    dummies = [
        {
            "user_id": "628000000001",
            "product_name": "Nasi Goreng Gila Gondrong",
            "location": "Jakarta Selatan",
            "menus": ["Nasi Goreng Gila", "Mie Goreng Spesial", "Kwetiau Seafood"],
            "unique_selling_point": "Porsi kuli banget dan pedesnya nampol, gratis kerupuk."
        },
        {
            "user_id": "628000000002",
            "product_name": "Kopi Senja Bahagia",
            "location": "Bandung",
            "menus": ["Es Kopi Susu Aren", "Americano Dingin", "Roti Bakar Coklat Keju", "Croissant Butter"],
            "unique_selling_point": "Biji kopi asli Gayo, suasana estetik cocok buat nugas sore."
        },
        {
            "user_id": "628000000003",
            "product_name": "Sate Madura Bintang Lima",
            "location": "Bekasi",
            "menus": ["Sate Ayam Bumbu Kacang", "Sate Kambing Muda", "Sop Kambing", "Sate Taichan"],
            "unique_selling_point": "Daging 100% empuk tanpa lemak, bumbu kacang rahasia turun temurun."
        },
        {
            "user_id": "628000000004",
            "product_name": "Kedai Seblak Jeletot Parah",
            "location": "Bogor",
            "menus": ["Seblak Ceker Mercon", "Seblak Mie Sosis", "Seblak Tulang", "Es Teh Jumbo"],
            "unique_selling_point": "Pedesnya bikin nangis, kuah kental kaldu ayam asli."
        },
        {
            "user_id": "628000000005",
            "product_name": "Ayam Geprek Mozzarella Juara",
            "location": "Yogyakarta",
            "menus": ["Geprek Keju Lumer", "Geprek Sambal Matah", "Jamur Crispy", "Es Jeruk Peras"],
            "unique_selling_point": "Tingkat pedas level 1-10, nasinya ambil sendiri sepuasnya."
        },
        {
            "user_id": "628000000006",
            "product_name": "Bakso Urat Raksasa Wong Solo",
            "location": "Solo",
            "menus": ["Bakso Beranak", "Bakso Mercon", "Mie Ayam Pangsit", "Es Teler"],
            "unique_selling_point": "Bakso segede mangkok full daging sapi asli kualitas tinggi."
        },
        {
            "user_id": "628000000007",
            "product_name": "Toko Kue Manis Legit",
            "location": "Depok",
            "menus": ["Fudgy Brownies", "Bolu Kukus Pandan", "Kue Tart Ulang Tahun", "Dessert Box Cookies"],
            "unique_selling_point": "100% Gula asli tanpa pemanis buatan, hiasan kue *custom* gratis."
        },
        {
            "user_id": "628000000008",
            "product_name": "Es Campur Segar Bugar",
            "location": "Surabaya",
            "menus": ["Es Campur Spesial", "Es Teler Durian", "Es Oyen", "Alpukat Kocok"],
            "unique_selling_point": "Topping durian montong premium tebal anti pelit."
        },
        {
            "user_id": "628000000009",
            "product_name": "Pecel Lele Lamongan Mak Nyus",
            "location": "Tangerang",
            "menus": ["Lele Goreng Garing", "Ayam Bakar Madu", "Bebek Goreng Kremes", "Sate Usus"],
            "unique_selling_point": "Sambal terasinya juara, lalapan sepuasnya gratis tambah."
        },
        {
            "user_id": "628000000010",
            "product_name": "Sushi Merakyat Oishi",
            "location": "Jakarta Pusat",
            "menus": ["California Roll", "Spicy Salmon Maki", "Chicken Teriyaki Bento", "Takoyaki"],
            "unique_selling_point": "Kualitas ikan salmon sekelas restoran tapi harga kaki lima."
        },
        {
            "user_id": "628000000011",
            "product_name": "Boba Time Kekinian",
            "location": "Malang",
            "menus": ["Brown Sugar Boba Milk", "Matcha Latte Creme", "Taro Milk Tea", "Mango Yakult"],
            "unique_selling_point": "Boba kenyal empuk dimasak *fresh* setiap pagi."
        },
        {
            "user_id": "628000000012",
            "product_name": "Martabak Sultan Nikmat",
            "location": "Semarang",
            "menus": ["Martabak Manis Keju Coklat", "Martabak Toblerone", "Martabak Telur Daging Sapi", "Martabak Mozzarella"],
            "unique_selling_point": "Adonan martabak manis selembut kapas, pinggirannya super garing."
        }
    ]

    for data in dummies:
        new_item = CatalogDB(**data)
        db.add(new_item)
    
    db.commit()
    db.close()
    print("Successfully seeded 12 F&B catalogs into the database!")

if __name__ == "__main__":
    seed_food_beverage_catalogs()
