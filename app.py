import streamlit as st

# ==========================================
# KELAS NODE ORGANISASI (GENERAL TREE)
# ==========================================
class OrganisasiNode:
    def __init__(self, nama_jabatan):
        self.nama = nama_jabatan
        self.bawahan = []

    # Menambahkan bawahan
    def tambah_bawahan(self, node_baru):
        self.bawahan.append(node_baru)

    # Menampilkan struktur organisasi
    def tampilkan_struktur(self, level=0):
        indentasi = "    " * level
        simbol = "↳ " if level > 0 else "👑 "
        
        hasil = f"{indentasi}{simbol}{self.nama}"

        for bawahan in self.bawahan:
            hasil += "\n" + bawahan.tampilkan_struktur(level + 1)

        return hasil

    # Mencari jabatan tertentu
    def cari_jabatan(self, target):
        if self.nama.lower() == target.lower():
            return self

        for bawahan in self.bawahan:
            hasil = bawahan.cari_jabatan(target)
            if hasil:
                return hasil

        return None

    # Mencari jalur organisasi
    def cari_jalur(self, target, path=""):
        jalur_saat_ini = path + " > " + self.nama if path else self.nama

        if self.nama.lower() == target.lower():
            return jalur_saat_ini

        for bawahan in self.bawahan:
            hasil = bawahan.cari_jalur(target, jalur_saat_ini)
            if hasil:
                return hasil

        return None


# ==========================================
# STREAMLIT UI
# ==========================================

st.set_page_config(
    page_title="Struktur Organisasi",
    page_icon="🏢"
)

st.title("🏢 Struktur Organisasi - General Tree")
st.write("Simulasi struktur organisasi menggunakan struktur data General Tree.")

# Session State
if "root" not in st.session_state:
    st.session_state.root = None

# ==========================================
# MEMBUAT ROOT / PIMPINAN
# ==========================================
if st.session_state.root is None:

    st.info("Silakan buat jabatan tertinggi terlebih dahulu.")

    nama_root = st.text_input(
        "Masukkan Jabatan Tertinggi:",
        value="Direktur Utama"
    )

    if st.button("Buat Struktur Organisasi", type="primary"):
        st.session_state.root = OrganisasiNode(nama_root)
        st.rerun()

# ==========================================
# MENU UTAMA
# ==========================================
else:

    root = st.session_state.root

    tab1, tab2, tab3 = st.tabs([
        "Lihat Struktur",
        "Tambah Jabatan",
        "Cari Jalur"
    ])

    # ==========================================
    # TAB 1 - LIHAT STRUKTUR
    # ==========================================
    with tab1:

        st.subheader("📌 Struktur Organisasi")

        struktur = root.tampilkan_struktur()

        st.code(struktur, language="text")

    # ==========================================
    # TAB 2 - TAMBAH JABATAN
    # ==========================================
    with tab2:

        st.subheader("➕ Tambah Jabatan Baru")

        nama_atasan = st.text_input(
            "Masukkan nama atasan:"
        )

        nama_baru = st.text_input(
            "Masukkan jabatan bawahan:"
        )

        if st.button("Tambah Jabatan"):

            if nama_atasan and nama_baru:

                atasan_node = root.cari_jabatan(nama_atasan)

                if atasan_node:

                    atasan_node.tambah_bawahan(
                        OrganisasiNode(nama_baru)
                    )

                    st.success(
                        f"'{nama_baru}' berhasil ditambahkan di bawah '{nama_atasan}'"
                    )

                else:
                    st.error(
                        f"Jabatan '{nama_atasan}' tidak ditemukan!"
                    )

            else:
                st.warning("Semua kolom harus diisi!")

    # ==========================================
    # TAB 3 - CARI JALUR
    # ==========================================
    with tab3:

        st.subheader("🔍 Cari Jalur Jabatan")

        target = st.text_input(
            "Masukkan jabatan yang dicari:"
        )

        if st.button("Cari Jalur"):

            if target:

                hasil = root.cari_jalur(target)

                if hasil:
                    st.success("Jabatan ditemukan!")
                    st.info(f"Jalur Organisasi: {hasil}")

                else:
                    st.error("Jabatan tidak ditemukan!")

            else:
                st.warning("Masukkan nama jabatan terlebih dahulu.")

    # ==========================================
    # RESET SISTEM
    # ==========================================
    st.divider()

    if st.button("🔄 Reset Struktur Organisasi"):

        st.session_state.root = None
        st.rerun()