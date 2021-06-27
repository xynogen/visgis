class Rekap:
    import pandas as pd

    def __init__(self, namafile):
        self.namafile = namafile

    def generate(self):
        df = self.pd.read_csv(self.namafile, index_col=0)

        SUM_IRI_BAIK = df.IRI_BAIK.sum()
        SUM_IRI_SEDANG = df.IRI_SEDANG.sum()
        SUM_IRI_RUSAK_RINGAN = df.IRI_RUSAK_RINGAN.sum()
        SUM_IRI_RUSAK_BERAT = df.IRI_RUSAK_BERAT.sum()
        TOTAL_IRI = SUM_IRI_BAIK + SUM_IRI_SEDANG + \
            SUM_IRI_RUSAK_RINGAN + SUM_IRI_RUSAK_BERAT
        IRI_MANTAP = (SUM_IRI_BAIK + SUM_IRI_SEDANG) / TOTAL_IRI
        IRI_TIDAK_MANTAP = (SUM_IRI_RUSAK_RINGAN +
                            SUM_IRI_RUSAK_BERAT) / TOTAL_IRI

        SUM_SDI_BAIK = df.SDI_BAIK.sum()
        SUM_SDI_SEDANG = df.SDI_SEDANG.sum()
        SUM_SDI_RUSAK_RINGAN = df.SDI_RUSAK_RINGAN.sum()
        SUM_SDI_RUSAK_BERAT = df.SDI_RUSAK_BERAT.sum()
        TOTAL_SDI = SUM_SDI_BAIK + SUM_SDI_SEDANG + \
            SUM_SDI_RUSAK_RINGAN + SUM_SDI_RUSAK_BERAT
        SDI_MANTAP = (SUM_SDI_BAIK + SUM_SDI_SEDANG) / TOTAL_SDI
        SDI_TIDAK_MANTAP = (SUM_SDI_RUSAK_RINGAN +
                            SUM_SDI_RUSAK_BERAT) / TOTAL_SDI

        data = {
            "IRI": [SUM_IRI_BAIK, SUM_IRI_SEDANG, SUM_IRI_RUSAK_RINGAN, SUM_IRI_RUSAK_BERAT, TOTAL_IRI, IRI_MANTAP, IRI_TIDAK_MANTAP],
            "SDI": [SUM_SDI_BAIK, SUM_SDI_SEDANG, SUM_SDI_RUSAK_RINGAN, SUM_SDI_RUSAK_BERAT, TOTAL_SDI, SDI_MANTAP, SDI_TIDAK_MANTAP]
        }

        dataframe = self.pd.DataFrame(data, columns=["IRI", "SDI"])

        return dataframe
