import streamlit as st
import pandas as pd
from datetime import datetime

# Konfigurasi halaman web
st.set_page_config(page_title="Aplikasi Tiket Konser", page_icon="🎫", layout="wide")

# ---------------------------------------------------------
# STRUKTUR DATA: LINKED LIST
# ---------------------------------------------------------

# Node untuk nyimpen data tiap transaksi
class TicketNode:
    def __init__(self, kode, nama, konser, lokasi, kategori, seat, harga, jumlah, total, status, waktu):
        self.kode = kode
        self.nama = nama
        self.konser = konser
        self.lokasi = lokasi
        self.kategori = kategori
        self.seat = seat
        self.harga = harga
        self.jumlah = jumlah
        self.total = total
        self.status = status
        self.waktu = waktu
        self.next = None

# Class Linked List untuk manajemen transaksi tiket
class TicketLinkedList:
    def __init__(self):
        self.head = None

    # Masukin data baru di akhir node (Append)
    def tambah_tiket(self, kode, nama, konser, lokasi, kategori, seat, harga, jumlah, total, status, waktu):
        node_baru = TicketNode(kode, nama, konser, lokasi, kategori, seat, harga, jumlah, total, status, waktu)
        if self.head is None:
            self.head = node_baru
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = node_baru

    # Convert data linked list ke list-dict biasa buat dibaca Pandas DataFrame
    def tampilkan_data(self):
        data = []
        current = self.head
        while current:
            data.append({
                "Kode": current.kode,
                "Nama": current.nama,
                "Konser": current.konser,
                "Seat": current.seat,
                "Kategori": current.kategori,
                "Jumlah": current.jumlah,
                "Total": f"Rp {current.total:,}",
                "Status": current.status,
                "Waktu": current.waktu
            })
            current = current.next
        return data

    # Cek biar ga ada seat tabrakan di konser yang sama
    def cek_seat(self, konser, seat, kode=None):
        current = self.head
        while current:
            if current.konser == konser and current.seat == seat and current.kode != kode:
                return True
            current = current.next
        return False

    # Hapus transaksi tiket berdasarkan kode
    def hapus_tiket(self, kode):
        current = self.head
        prev = None
        while current:
            if current.kode == kode:
                # Balikin stok konser ke database sebelum dihapus
                st.session_state.konser_store[current.konser]["stok"] += current.jumlah
                if prev:
                    prev.next = current.next
                else:
                    self.head = current.next
                return True
            prev = current
            current = current.next
        return False

    # Update data tiket yang ada dengan validasi kuota/stok
    def update_tiket(self, kode, konser_baru, lokasi_baru, kategori_baru, seat_baru, harga_baru, jumlah_baru):
        current = self.head
        while current:
            if current.kode == kode:
                if current.status == "Lunas":
                    return "lunas"

                stok_tersedia = st.session_state.konser_store[konser_baru]["stok"]
                if current.konser == konser_baru:
                    stok_tersedia += current.jumlah # Balikin sementara buat dicek kelayakannya

                if jumlah_baru > stok_tersedia:
                    return "stok_habis"

                if self.cek_seat(konser_baru, seat_baru, kode):
                    return "seat_digunakan"

                # Eksekusi perubahan stok final
                st.session_state.konser_store[current.konser]["stok"] += current.jumlah
                st.session_state.konser_store[konser_baru]["stok"] -= jumlah_baru

                # Terapkan data baru ke node
                current.konser = konser_baru
                current.lokasi = lokasi_baru
                current.kategori = kategori_baru
                current.seat = seat_baru
                current.harga = harga_baru
                current.jumlah = jumlah_baru
                current.total = harga_baru * jumlah_baru
                return "berhasil"
            current = current.next
        return "tidak ditemukan"


# ---------------------------------------------------------
# INITIALIZATION STATE (Biar data ga hilang pas ganti menu/tab)
# ---------------------------------------------------------
if "tickets" not in st.session_state:
    st.session_state.tickets = TicketLinkedList()

if "admin_login" not in st.session_state:
    st.session_state.admin_login = False

if "next_trx_id" not in st.session_state:
    st.session_state.next_trx_id = 1

if "konser_store" not in st.session_state:
    st.session_state.konser_store = {
        "Coldplay World Tour": {
            "lokasi": "Jakarta International Stadium",
            "tanggal": "12 Juni 2026",
            "vip": 2500000,
            "regular": 1200000,
            "stok": 150,
            "genre": "Pop Rock",
            "guest": "Special Guest DJ"
        },
        "NIKI Live Concert": {
            "lokasi": "ICE BSD",
            "tanggal": "20 Juli 2026",
            "vip": 1800000,
            "regular": 850000,
            "stok": 100,
            "genre": "R&B",
            "guest": "Reality Club"
        },
        "Taylor Swift Eras Tour": {
            "lokasi": "Gelora Bung Karno",
            "tanggal": "10 Agustus 2026",
            "vip": 3500000,
            "regular": 2000000,
            "stok": 200,
            "genre": "Pop",
            "guest": "Sabrina Carpenter"
        }
    }

konser_data = st.session_state.konser_store


# ---------------------------------------------------------
# AUTENTIKASI ADMIN SIDEBAR
# ---------------------------------------------------------
USERNAME = "admin"
PASSWORD = "12345"

st.sidebar.subheader("🔐 Admin Panel")
if not st.session_state.admin_login:
    admin_user = st.sidebar.text_input("Username Admin")
    admin_pass = st.sidebar.text_input("Password Admin", type="password")
    if st.sidebar.button("Login Admin"):
        if admin_user == USERNAME and admin_pass == PASSWORD:
            st.session_state.admin_login = True
            st.rerun()
        else:
            st.sidebar.error("❌ Login gagal")
else:
    st.sidebar.success("✅ Admin Aktif")
    if st.sidebar.button("Logout Admin"):
        st.session_state.admin_login = False
        st.rerun()


# ---------------------------------------------------------
# INTERFACE UTAMA (SISTEM TABS)
# ---------------------------------------------------------
st.title("🎫 Aplikasi Pemesanan Tiket Konser")
st.write("Aplikasi interaktif untuk mensimulasikan struktur data Linked List pada pemesanan tiket.")

# Inisialisasi Menu menggunakan komponen Tabs murni
tab1, tab2, tab3 = st.tabs(["🎤 Daftar & Pesan Konser", "✏️ Update Data Tiket", "🔍 Cari Tiket"])

# --- TAB 1: DAFTAR & PESAN KONSER ---
with tab1:
    st.header("Jadwal Konser & Kuota")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        c1 = st.container(border=True)
        c1.subheader("Coldplay World Tour")
        c1.write("📍 Jakarta International Stadium\n\n📅 12 Juni 2026")
        c1.write(f"**🎫 Sisa Stok : {konser_data['Coldplay World Tour']['stok']}**")

    with col2:
        c2 = st.container(border=True)
        c2.subheader("NIKI Live Concert")
        c2.write("📍 ICE BSD\n\n📅 20 Juli 2026")
        c2.write(f"**🎫 Sisa Stok : {konser_data['NIKI Live Concert']['stok']}**")

    with col3:
        c3 = st.container(border=True)
        c3.subheader("Taylor Swift Eras Tour")
        c3.write("📍 Gelora Bung Karno\n\n📅 10 Agustus 2026")
        c3.write(f"**🎫 Sisa Stok : {konser_data['Taylor Swift Eras Tour']['stok']}**")

    st.divider()
    st.subheader("Form Pembelian Tiket")
    
    # Form input dipindah ke halaman utama biar ga menumpuk di sidebar
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        nama = st.text_input("👤 Nama Lengkap Pembeli")
        konser = st.selectbox("🎵 Pilih Konser Tujuan", list(konser_data.keys()))
        kategori = st.radio("🎫 Kategori Tiket", ["VIP", "Regular"])
    with col_f2:
        seat = st.selectbox("💺 Pilih Kode Seat", ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"])
        jumlah = st.number_input("🔢 Jumlah Tiket yang Dibeli", min_value=1, max_value=5, value=1)
        metode = st.selectbox("💳 Metode Pembayaran", ["QRIS", "Transfer Bank", "E-Wallet"])
        
    if st.button("🎟️ Kirim Pesanan Tiket", type="primary"):
        if nama.strip() == "":
            st.error("❌ Nama wajib diisi")
        elif jumlah > konser_data[konser]["stok"]:
            st.error("❌ Stok tiket tidak cukup")
        elif st.session_state.tickets.cek_seat(konser, seat):
            st.error("❌ Seat sudah digunakan")
        else:
            harga = konser_data[konser]["vip"] if kategori == "VIP" else konser_data[konser]["regular"]
            total = harga * jumlah
            
            kode = f"TRX-{st.session_state.next_trx_id}"
            st.session_state.next_trx_id += 1
            
            waktu = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            status = "Pending"

            st.session_state.konser_store[konser]["stok"] -= jumlah
            st.session_state.tickets.tambah_tiket(kode, nama, konser, konser_data[konser]["lokasi"], kategori, seat, harga, jumlah, total, status, waktu)

            st.success("✅ Tiket berhasil dipesan!")
            st.balloons()
            
            st.info(f"**Invoice Sementara Anda:** Code: {kode} | Total: Rp {total:,} | Status: {status}. Catat Kode TRX untuk melakukan update/pencarian.")
            st.rerun()

# --- TAB 2: UPDATE DATA TIKET ---
with tab2:
    st.subheader("Modifikasi Pesanan")
    st.write("Layanan perubahan jadwal konser atau kategori seat sebelum pembayaran dikonfirmasi lunas.")
    
    kode_update = st.text_input("Masukkan Kode Tiket yang Ingin Diubah:")
    
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        konser_baru = st.selectbox("Pilih Konser Baru:", list(konser_data.keys()), key="k_baru")
        kategori_baru = st.radio("Kategori Baru:", ["VIP", "Regular"], key="update")
    with col_u2:
        seat_baru = st.selectbox("Seat Baru:", ["A1", "A2", "B1", "B2", "C1", "C2"], key="seat_update")
        jumlah_baru = st.number_input("Jumlah Baru:", min_value=1, max_value=5, value=1, key="jumlah_update")

    if st.button("Simpan Perubahan Tiket"):
        if kode_update.strip() == "":
            st.error("❌ Harap isi kode tiket yang ingin diubah.")
        else:
            harga_baru = konser_data[konser_baru]["vip"] if kategori_baru == "VIP" else konser_data[konser_baru]["regular"]
            hasil = st.session_state.tickets.update_tiket(kode_update, konser_baru, konser_data[konser_baru]["lokasi"], kategori_baru, seat_baru, harga_baru, jumlah_baru)

            if hasil == "berhasil":
                st.success("✅ Transaksi tiket berhasil di-update!")
                st.rerun()
            elif hasil == "lunas":
                st.error("❌ Gagal, tiket tidak bisa diubah karena statusnya sudah Lunas!")
            elif hasil == "seat_digunakan":
                st.error("❌ Gagal, nomor seat sudah dipesan orang lain.")
            elif hasil == "stok_habis":
                st.error("❌ Gagal, kapasitas kuota konser tujuan sudah habis.")
            else:
                st.error("❌ Kode tiket tidak ditemukan.")

# --- TAB 3: CARI JALUR/INFO TIKET (PENCARIAN MANUAL USER) ---
with tab3:
    st.subheader("Cari Status Pesanan Anda")
    target_cari = st.text_input("Masukkan Kode Tiket (Contoh: TRX-1):")
    
    if st.button("Mulai Pencarian"):
        if target_cari:
            data_all = st.session_state.tickets.tampilkan_data()
            ditemukan = False
            for item in data_all:
                if item["Kode"].lower() == target_cari.strip().lower():
                    st.success("🎯 Data Transaksi Ditemukan!")
                    st.json(item)
                    ditemukan = True
                    break
            if not ditemukan:
                st.error("❌ Data tidak ditemukan. Cek kembali penulisan Kode Tiket Anda.")
        else:
            st.warning("Harap isi kode tiket yang ingin dicari.")


# ---------------------------------------------------------
# BACK-END ADMIN CONTROL (MUNCUL JIKA SUDAH LOGIN DI SIDEBAR)
# ---------------------------------------------------------
if st.session_state.admin_login:
    st.divider()
    st.header("📊 Database Management (Admin View)")
    
    data = st.session_state.tickets.tampilkan_data()
    
    if data:
        cari_nama = st.text_input("🔍 Filter Pencarian Berdasarkan Nama Pembeli:")
        if cari_nama:
            hasil_filter = [item for item in data if cari_nama.lower() in item["Nama"].lower()]
            df = pd.DataFrame(hasil_filter)
        else:
            df = pd.DataFrame(data)
            
        st.dataframe(df, use_container_width=True)
        
        # Hitung Penghasilan & Total Pesanan
        total_pembeli = len(data)
        total_penghasilan = 0
        current = st.session_state.tickets.head
        while current:
            if current.status == "Lunas":
                total_penghasilan += current.total
            current = current.next
            
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("💰 Total Omset Sukses (Lunas)", f"Rp {total_penghasilan:,}")
        with col_m2:
            st.metric("👥 Jumlah Antrean Tiket Masuk", total_pembeli)
            
        st.divider()
        col_adm1, col_adm2 = st.columns(2)
        
        with col_adm1:
            st.subheader("💳 Verifikasi Pembayaran")
            kode_bayar = st.text_input("Masukkan Kode Tiket yang Mau Dilunasi:")
            if st.button("Setujui Pembayaran"):
                current = st.session_state.tickets.head
                ketemu = False
                while current:
                    if current.kode == kode_bayar:
                        current.status = "Lunas"
                        ketemu = True
                        break
                    current = current.next
                if ketemu:
                    st.success("✅ Tiket divalidasi Lunas!")
                    st.rerun()
                else:
                    st.error("❌ Kode tidak terdaftar.")
                    
        with col_adm2:
            st.subheader("🗑️ Pembatalan / Hapus Tiket")
            kode_hapus = st.text_input("Masukkan Kode Tiket yang Mau Dihapus:")
            if st.button("Hapus Permanen"):
                if st.session_state.tickets.hapus_tiket(kode_hapus):
                    st.success("✅ Data berhasil dibersihkan dan kuota dipulihkan.")
                    st.rerun()
                else:
                    st.error("❌ Kode tidak ditemukan.")
    else:
        st.info("Belum ada antrean transaksi masuk saat ini.")
else:
    st.divider()
    st.caption("💡 Mode Guest Aktif: Silakan login lewat panel kiri jika ingin mengakses data master admin.")

# ---------------------------------------------------------
# GLOBAL RESET BUTTON
# ---------------------------------------------------------
st.divider()
if st.button("🔄 Reset Aplikasi Ke Awal"):
    st.session_state.clear()
    st.rerun()
