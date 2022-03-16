import geopandas as gpd
import pandas as pd
import numpy as np
import os
# from waitress import serve
from flask import Flask, redirect, url_for, request, session, render_template
from bokeh.layouts import layout
from bokeh.models import OpenURL, TapTool, HoverTool, Toggle, WheelZoomTool, CustomJS, Dropdown
from bokeh.embed import components
from bokeh.plotting import figure, ColumnDataSource
from bokeh.resources import INLINE
from bokeh.tile_providers import get_provider, OSM, ESRI_IMAGERY, CARTODBPOSITRON_RETINA, STAMEN_TERRAIN
from bokeh.palettes import brewer
from UFunc import Rekapitulasi as rk
from UFunc import Utils as ut
from UFunc import Statistik as st

app = Flask(__name__)
app.jinja_env.filters['zip'] = zip
app.secret_key = "24304fab8101a0859f4e4f7f53f1bbd3ca3632f6ea38c893512f39ce06da127d"
FILE = "./Kondisi_100/KONDISI_100.shp"
LOOKUPTABLE = "./Settings/table_stat.csv"
USER = "./Settings/users.json"


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if "user" in session:
            return redirect(url_for("dashboard"))
        return render_template("login.html")
    elif request.method == "POST":
        username = str(request.form.get("username"))
        password = str(request.form.get("password"))
        data = ut.loadData(USER)
        index = ut.indexOf(username, data)
        if index != None:
            if data["users"][index]["username"] == username and data["users"][index]["password"] == ut.hashOf(password):
                session["user"] = username
                return redirect(url_for("dashboard"))
        return redirect(url_for("login"))


@app.route("/dashboard/<tiles>", methods=["GET"])
def dashboard(tiles=OSM):
    if "user" in session:
        geodata = gpd.read_file(FILE)

        if 'COLOR_IRI' and "COLOR_SDI" and "COLOR_PERK" not in geodata.columns:
            geodata["COLOR_IRI"] = geodata["KONDISI_IR"].apply(ut.Color_Mapper_Kondisi)
            geodata["COLOR_SDI"] = geodata["KONDISI_SD"].apply(ut.Color_Mapper_Kondisi)
            geodata["COLOR_PERK"] = geodata["PERKERASAN"].apply(ut.Color_Mapper_Perkerasan)
            geodata.to_file(FILE)
           
        if "RIGID" in np.unique(geodata.PERKERASAN):
            if "BETON" not in np.unique(geodata.PERKERASAN):
                geodata.PERKERASAN.replace("RIGID", "BETON", inplace=True) 
                geodata.to_file(FILE)

        if not os.path.isfile(LOOKUPTABLE):
            Statistik = st(FILE)
            Statistik.generate()


        if tiles == "OSM" or tiles==None:
            tile = OSM
        elif tiles == "ESRI_IMAGERY":
            tile = ESRI_IMAGERY
        elif tiles == "CARTODBPOSITRON_RETINA":
            tile = CARTODBPOSITRON_RETINA
        elif tiles == "STAMEN_TERRAIN":
            tile = STAMEN_TERRAIN

        geodata.to_crs(epsg=3857, inplace=True)
        tile_provider = get_provider(tile)
        palette = brewer['BuGn'][8]
        palette = palette[::-1]

        p = figure()

        p.xgrid.visible = False
        p.ygrid.visible = False
        p.xaxis.major_tick_line_color = None
        p.xaxis.minor_tick_line_color = None
        p.yaxis.major_tick_line_color = None
        p.yaxis.minor_tick_line_color = None
        p.xaxis.major_label_text_font_size = '0pt'
        p.yaxis.major_label_text_font_size = '0pt'

        geodata['x'] = geodata.apply(ut.getLineCoords, geom='geometry', coord_type='x', axis=1)
        geodata['y'] = geodata.apply(ut.getLineCoords, geom='geometry', coord_type='y', axis=1)
        m_df = geodata.drop('geometry', axis=1).copy()

        msource = ColumnDataSource(m_df)

        hover = HoverTool(tooltips=[
            ("No Ruas", "@RUAS"),
            ("Nama Ruas", "@NAMA_RUAS"),
            ("STA", "@STA"),
            ("Lebar", "@LEBAR_JALA"),
            ("Perkerasan", "@PERKERASAN"),
            ("IRI", "@IRI"),
            ("SDI", "@SDI"),
            ("Kondisi IRI", "@KONDISI_IR"),
            ("Kondisi SDI", "@KONDISI_SD"),
            ("Bahu Kiri", "@BAHU_KIRI"),
            ("Bahu Kanan", "@BAHU_KANAN"),
            ("Trotoar Kiri", "@TROTOAR_KI"),
            ("Trotoar Kanan", "@TROTOAR_KA")
        ])

        url = "/edit/@index"

        taptool = TapTool(callback=OpenURL(url=url))
        p.add_tools(hover, taptool)
        p.toolbar.active_scroll = p.select_one(WheelZoomTool)

        p.add_tile(tile_provider)

        SDI_LINE = p.multi_line('x', 'y', source=msource, color="COLOR_SDI", line_width=3, legend_field='KONDISI_SD')
        IRI_LINE = p.multi_line('x', 'y', source=msource, color="COLOR_IRI", line_width=3)
        PERKERASAN_LINE = p.multi_line('x', 'y', source=msource, color="COLOR_PERK", line_width=3, legend_field='PERKERASAN')    
       
        toggle1 = Toggle(label="SDI Line", button_type="success", active=True, width=150)
        toggle1.js_link('active', SDI_LINE, 'visible')
        
        toggle2 = Toggle(label="IRI Line", button_type="success", active=True, width=150)
        toggle2.js_link('active', IRI_LINE, 'visible')
        
        toggle3 = Toggle(label="Perkerasan", button_type="success", active=True, width=150)
        toggle3.js_link('active', PERKERASAN_LINE, 'visible')
        
        menu = [("OSM", "OSM"), 
            ("ESRI_IMAGERY", "ESRI_IMAGERY"), 
            ("CARTODBPOSITRON_RETINA", "CARTODBPOSITRON_RETINA"), 
            ("STAMEN_TERRAIN", "STAMEN_TERRAIN")]

        dropdown = Dropdown(label="Tiles", button_type="success", menu=menu)
        dropdown.js_on_event("menu_item_click", 
        CustomJS(code="window.location.replace('/dashboard/' + this.item.toString());"))
        
        js_resources = INLINE.render_js()
        css_resources = INLINE.render_css()

        Layouts = layout([dropdown], [toggle1, toggle2, toggle3], [p], sizing_mode="scale_width")

        script, div = components(Layouts)
        df = pd.read_csv(LOOKUPTABLE, index_col=0)

        return render_template("dashboard.html",
                               plot_script=script,
                               plot_div=div,
                               js_resources=js_resources,
                               css_resources=css_resources,
                               user= session["user"],
                               row_data=list(df.values.tolist()),
                               format_uang=ut.format_uang,
                               round = round)
    return redirect(url_for("login"))


@app.route("/rekapitulasi", methods=["GET"])
def rekapitulasi():
    if "user" in session:
        data = rk.Rekap(LOOKUPTABLE)
        gen = data.generate()
        return render_template("rekapitulasi.html",
                                generate = gen,
                                user = session["user"],
                                round = round)
    return redirect(url_for("login"))


@app.route("/biaya", methods=["GET"])
def biaya():
    if "user" in session:
        data = rk.Rekap(LOOKUPTABLE)
        gen = data.generate()
        return render_template("biaya.html",
                                generate = gen,
                                round = round,
                                format_uang=ut.format_uang,
                                user = session["user"])
    return redirect(url_for("login"))


@app.route("/edit/<id>", methods=["GET"])
def edit_GET(id):
    if "user" in session:
        geodata = gpd.read_file(FILE)
        number = int(id)
        try:
            search = geodata.iloc[number,:]
            kolom = search.index.tolist()[0:-1]
            baris = search.values.tolist()[0:-1]
            ruas = baris[15]
        except NameError:
            return redirect("/")
        return render_template("edit.html",
                            user = session["user"],
                            column_names=kolom,
                            row_data=baris,
                            index = number,
                            ruas=ruas)

    return redirect(url_for("login"))


@app.route("/edit", methods=["POST"])
def edit_POST():
    if "user" in session:
        geodata = gpd.read_file(FILE)
        index = request.form.get("index")
        ruas = request.form.get("ruas")
        STA = request.form.get("STA")
        LEBAR_JALA = request.form.get("LEBAR_JALA")
        BAHU_KIRI = request.form.get("BAHU_KIRI")
        BAHU_KANAN = request.form.get("BAHU_KANAN")
        TROTOAR_KI = request.form.get("TROTOAR_KI")
        TROTOAR_KA = request.form.get("TROTOAR_KA")
        PERKERASAN = request.form.get("PERKERASAN")
        IRI = request.form.get("IRI")
        SDI = request.form.get("SDI")
        KONDISI_IR = request.form.get("KONDISI_IR")
        KONDISI_SD = request.form.get("KONDISI_SD")
        P_SEGMEN = request.form.get("P_SEGMEN")

        # save value pada data
        geodata.loc[int(index), "STA"] = STA
        geodata.loc[int(index), "LEBAR_JALA"] = LEBAR_JALA
        geodata.loc[int(index), "BAHU_KIRI"] = BAHU_KIRI
        geodata.loc[int(index), "BAHU_KANAN"] = BAHU_KANAN
        geodata.loc[int(index), "TROTOAR_KI"] = TROTOAR_KI
        geodata.loc[int(index), "TROTOAR_KA"] = TROTOAR_KA
        geodata.loc[int(index), "PERKERASAN"] = PERKERASAN
        geodata.loc[int(index), "IRI"] = IRI
        geodata.loc[int(index), "SDI"] = SDI
        geodata.loc[int(index), "KONDISI_IR"] = KONDISI_IR
        geodata.loc[int(index), "KONDISI_SD"] = KONDISI_SD
        geodata.loc[int(index), "P_SEGMEN"] = P_SEGMEN

        geodata.loc[int(index), "COLOR_IRI"] = ut.Color_Mapper_Kondisi(str(KONDISI_IR))
        geodata.loc[int(index), "COLOR_SDI"] = ut.Color_Mapper_Kondisi(str(KONDISI_SD))
        geodata.loc[int(index), "COLOR_PERK"] = ut.Color_Mapper_Perkerasan(str(PERKERASAN))

        geodata.to_file(FILE)
        
        Statistik = st(FILE, LOOKUPTABLE)
        Statistik.generate_partial(str(ruas))

        return redirect(url_for("edit_GET", id=index))

    return redirect(url_for("login"))


@app.route("/logout", methods=["GET"])
def logout():
    session.pop("user")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.add_url_rule('/dashboard/','dashboard',dashboard)
    # serve(app, host="0.0.0.0", port=5000)
    app.run(debug=True, host="0.0.0.0")
