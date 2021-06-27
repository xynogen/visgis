class Statistik:
    import geopandas as gpd
    import pandas as pd
    import numpy as np
        
    def __init__(self, file:str, stat_file:str):
        self.file = file
        self.stat_file = stat_file
        
        self.data = self.gpd.read_file(self.file)
        self.panda = self.pd.read_csv(self.stat_file, index_col=0)
        
        self.data.P_SEGMEN = self.data.P_SEGMEN.astype(self.np.float64)
        self.data.LEBAR_JALA = self.data.LEBAR_JALA.astype(self.np.float32)
        self.data.BAHU_KIRI = self.data.BAHU_KIRI.astype(self.np.float32)
        self.data.BAHU_KANAN = self.data.BAHU_KANAN.astype(self.np.float32)
        self.data.TROTOAR_KI = self.data.TROTOAR_KI.astype(self.np.float32)
        self.data.TROTOAR_KA = self.data.TROTOAR_KA.astype(self.np.float32)
        self.data.IRI = self.data.IRI.astype(self.np.uint8)
        self.data.SDI = self.data.SDI.astype(self.np.uint8)
        
    def format_uang(self, angka: float):
        return "{:,.2f}".format(angka)

    def select(self, NO: str):
        selected = self.data[self.data.eq(NO).any(1)]
        return selected

    def nama_ruas(self, selected):
        return selected.loc[selected.index[1]].NAMA_RUAS

    def panjang(self, selected):
        return selected.P_SEGMEN.sum()

    def rata_kondisi(self, selected):
        P_SEG = selected.P_SEGMEN
        IRI = (P_SEG * selected.IRI).sum()
        SDI = (P_SEG * selected.SDI).sum()
        LEBAR = (P_SEG * selected.LEBAR_JALA).sum()
        N_DATA = P_SEG.sum()
        
        return IRI/N_DATA, SDI/N_DATA, LEBAR/N_DATA

    def panjang_per_kondisi(self, selected, col_name:str):
        baik = 0
        sedang = 0
        rusak_ringan = 0
        rusak_berat = 0

        for i, row in selected.iterrows():
            if (row[col_name] == "BAIK"):
                baik = baik + row["P_SEGMEN"]
            elif (row[col_name] == "SEDANG"):
                sedang = sedang + row["P_SEGMEN"]
            elif (row[col_name] == "RUSAK RINGAN"):
                rusak_ringan = rusak_ringan + row["P_SEGMEN"]
            elif (row[col_name] == "RUSAK BERAT"):
                rusak_berat = rusak_berat + row["P_SEGMEN"]

        baik = baik
        sedang = sedang
        rusak_ringan = rusak_ringan
        rusak_berat = rusak_berat
        total = baik + sedang + rusak_ringan + rusak_berat

        return baik, sedang, rusak_ringan, rusak_berat, total

    def lebar(self, selected):
        less_enam = 0
        enam_tujuh = 0
        tujuh_empat_belas = 0
        greater_empat_belas = 0
        
        for i, row in selected.iterrows():
            if (row["LEBAR_JALA"] <= 6):
                less_enam = less_enam + row["P_SEGMEN"]
            elif(row["LEBAR_JALA"] > 6 and row["LEBAR_JALA"] <= 7):
                enam_tujuh = enam_tujuh + row["P_SEGMEN"]
            elif(row["LEBAR_JALA"] > 7 and row["LEBAR_JALA"] <= 14):
                tujuh_empat_belas = tujuh_empat_belas + row["P_SEGMEN"]
            elif(row["LEBAR_JALA"] > 14):
                greater_empat_belas = greater_empat_belas + row["P_SEGMEN"]

        less_enam = less_enam
        enam_tujuh = enam_tujuh
        tujuh_empat_belas = tujuh_empat_belas
        greater_empat_belas = greater_empat_belas
        total = less_enam + enam_tujuh + tujuh_empat_belas + greater_empat_belas

        return less_enam, enam_tujuh, tujuh_empat_belas, greater_empat_belas, total

    def biaya(self, data_kondisi, sedang = 50_000_000, rusak_berat = 8_640_000_000, rusak_ringan = 4_096_000_000, baik = 50_000_000):
        return data_kondisi[0] * baik + data_kondisi[1] * sedang + data_kondisi[2] * rusak_ringan + data_kondisi[3] * rusak_berat
    
    def _indexInTable(self, NO_RUAS: str):
        index = self.panda.loc[self.panda['NO'] == str(NO_RUAS)].index[0]
        return index
        
    def generate(self):
        kolom = ["NO", "RUAS", "PANJANG", "IRI_RATA", "SDI_RATA", "LEBAR_RATA", "IRI_BAIK", "IRI_SEDANG", 
         "IRI_RUSAK_RINGAN","IRI_RUSAK_BERAT", "IRI_TOTAL", "SDI_BAIK", "SDI_SEDANG", "SDI_RUSAK_RINGAN", 
         "SDI_RUSAK_BERAT", "SDI_TOTAL","LESS_ENAM", "ENAM_TUJUH", "TUJUH_EMPAT_BELAS", 
         "GREATER_EMPAT_BELAS", "PANJANG_TOTAL", "BIAYA_IRI", "BIAYA_SDI"]
        df = self.pd.DataFrame(columns=kolom) 
        nomor_ruas = self.data.NO_RUAS.unique()
        
        for nomor in nomor_ruas:
            NO = str(nomor)
            SELECTED = self.select(NO)
            RUAS = self.nama_ruas(SELECTED)
            PANJANG = self.panjang(SELECTED)
            IRI_RATA, SDI_RATA, LEBAR_RATA = self.rata_kondisi(SELECTED)
            IRI_BAIK, IRI_SEDANG, IRI_RUSAK_RINGAN, IRI_RUSAK_BERAT, IRI_TOTAL = self.panjang_per_kondisi(SELECTED, "KONDISI_IR")
            SDI_BAIK, SDI_SEDANG, SDI_RUSAK_RINGAN, SDI_RUSAK_BERAT, SDI_TOTAL = self.panjang_per_kondisi(SELECTED, "KONDISI_SD")
            LESS_ENAM, ENAM_TUJUH, TUJUH_EMPAT_BELAS, GREATER_EMPAT_BELAS, PANJANG_TOTAL = self.lebar(SELECTED)
            BIAYA_IRI = self.biaya((IRI_BAIK, IRI_SEDANG, IRI_RUSAK_RINGAN, IRI_RUSAK_BERAT))
            BIAYA_SDI = self.biaya((SDI_BAIK, SDI_SEDANG, SDI_RUSAK_RINGAN, SDI_RUSAK_BERAT))
        
            new_row = {
                "NO" : NO,
                "RUAS" : RUAS, 
                "PANJANG" : PANJANG, 
                "IRI_RATA" : IRI_RATA, 
                "SDI_RATA" : SDI_RATA, 
                "LEBAR_RATA" : LEBAR_RATA, 
                "IRI_BAIK" : IRI_BAIK, 
                "IRI_SEDANG" : IRI_SEDANG, 
                "IRI_RUSAK_RINGAN" : IRI_RUSAK_RINGAN,
                "IRI_RUSAK_BERAT" : IRI_RUSAK_BERAT, 
                "IRI_TOTAL" : IRI_TOTAL, 
                "SDI_BAIK" : SDI_BAIK, 
                "SDI_SEDANG" : SDI_SEDANG, 
                "SDI_RUSAK_RINGAN" : SDI_RUSAK_RINGAN, 
                "SDI_RUSAK_BERAT" : SDI_RUSAK_BERAT, 
                "SDI_TOTAL" : SDI_TOTAL,
                "LESS_ENAM" : LESS_ENAM, 
                "ENAM_TUJUH" : ENAM_TUJUH, 
                "TUJUH_EMPAT_BELAS" : TUJUH_EMPAT_BELAS ,  
                "GREATER_EMPAT_BELAS" : GREATER_EMPAT_BELAS, 
                "PANJANG_TOTAL" : PANJANG_TOTAL , 
                "BIAYA_IRI" : BIAYA_IRI, 
                "BIAYA_SDI" : BIAYA_SDI
            }
            df = df.append(new_row, ignore_index=True)
        df.to_csv("./Settings/table_stat.csv")
        return True
    
    def generate_partial(self, NO_RUAS: str):
        NO = str(NO_RUAS)
        SELECTED = self.select(NO)
        RUAS = self.nama_ruas(SELECTED)
        PANJANG = self.panjang(SELECTED)
        IRI_RATA, SDI_RATA, LEBAR_RATA = self.rata_kondisi(SELECTED)
        IRI_BAIK, IRI_SEDANG, IRI_RUSAK_RINGAN, IRI_RUSAK_BERAT, IRI_TOTAL = self.panjang_per_kondisi(SELECTED, "KONDISI_IR")
        SDI_BAIK, SDI_SEDANG, SDI_RUSAK_RINGAN, SDI_RUSAK_BERAT, SDI_TOTAL = self.panjang_per_kondisi(SELECTED, "KONDISI_SD")
        LESS_ENAM, ENAM_TUJUH, TUJUH_EMPAT_BELAS, GREATER_EMPAT_BELAS, PANJANG_TOTAL = self.lebar(SELECTED)
        BIAYA_IRI = self.biaya((IRI_BAIK, IRI_SEDANG, IRI_RUSAK_RINGAN, IRI_RUSAK_BERAT))
        BIAYA_SDI = self.biaya((SDI_BAIK, SDI_SEDANG, SDI_RUSAK_RINGAN, SDI_RUSAK_BERAT))

        __index = self._indexInTable(NO_RUAS)
        self.panda.loc[__index, "PANJANG"] = PANJANG
        self.panda.loc[__index, "IRI_RATA"] = IRI_RATA
        self.panda.loc[__index, "SDI_RATA"] = SDI_RATA
        self.panda.loc[__index, "LEBAR_RATA"] = LEBAR_RATA
        self.panda.loc[__index, "IRI_BAIK"] = IRI_BAIK
        self.panda.loc[__index, "IRI_SEDANG"] = IRI_SEDANG
        self.panda.loc[__index, "IRI_RUSAK_RINGAN"] = IRI_RUSAK_RINGAN
        self.panda.loc[__index, "IRI_RUSAK_BERAT"] = IRI_RUSAK_BERAT
        self.panda.loc[__index, "IRI_TOTAL"] = IRI_TOTAL
        self.panda.loc[__index, "SDI_BAIK"] = SDI_BAIK
        self.panda.loc[__index, "SDI_SEDANG"] = SDI_SEDANG
        self.panda.loc[__index, "SDI_RUSAK_RINGAN"] = SDI_RUSAK_RINGAN
        self.panda.loc[__index, "SDI_RUSAK_BERAT"] = SDI_RUSAK_BERAT
        self.panda.loc[__index, "SDI_TOTAL"] = SDI_TOTAL
        self.panda.loc[__index, "LESS_ENAM"] = LESS_ENAM
        self.panda.loc[__index, "ENAM_TUJUH"] = ENAM_TUJUH
        self.panda.loc[__index, "TUJUH_EMPAT_BELAS"] = TUJUH_EMPAT_BELAS
        self.panda.loc[__index, "GREATER_EMPAT_BELAS"] = GREATER_EMPAT_BELAS
        self.panda.loc[__index, "PANJANG_TOTAL"] = PANJANG_TOTAL
        self.panda.loc[__index, "BIAYA_IRI"] = BIAYA_IRI
        self.panda.loc[__index, "BIAYA_SDI"] = BIAYA_SDI
        
        self.panda.to_csv("./Settings/table_stat.csv")
        return True
        