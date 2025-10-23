# KILL Bet365 League 2025-2026 — 
# - Legenda solo "Punti"
# - Scheda POLLO con "Danno" (prodotto 5 quote × stake)
# - Ricariche: numero (7, 7.5) o data "gg/mm/aa", etichette RG… in grafico e tabella
# - Grafico cassa con emoji centrali: 💩 (con alone bianco), 💵, 🪙, 😟, 😱
# - Asse X: "Giornate"
# - Volpi ordinate per conteggio decrescente

import streamlit as st
import pandas as pd
import numpy as np
from itertools import cycle
import re as _re
import altair as alt
import streamlit.components.v1 as components
import os
import pickle

# ==================== INIZIALIZZAZIONE OGGETTI GLOBALI ====================

# Crea il contenitore per le celebrazioni se non esiste ancora
if "celebration_box" not in st.session_state:
    st.session_state["celebration_box"] = st.empty()
    
# Inizializza anche altri stati comuni, per evitare errori in caso di primo avvio
if "giornata_flag" not in st.session_state:
    st.session_state["giornata_flag"] = {}
if "cashouts" not in st.session_state:
    st.session_state["cashouts"] = {}
if "ricariche" not in st.session_state:
    st.session_state["ricariche"] = {}
if "fino_a" not in st.session_state:
    st.session_state["fino_a"] = 1

st.set_page_config(page_title="🐔💰 KillBet League 2025-2026 💰🦊", layout="wide")

# ===== DEVICE & ORIENTATION DETECTION (versione universale e sicura) =====
import streamlit as st

# Manteniamo sempre le stesse variabili di stato
if "view" not in st.session_state:
    st.session_state.view = "home"

# === Protezione anti-reset per slider ===
if "fino_a" in st.session_state:
    st.session_state.setdefault("slider_fino_a", st.session_state["fino_a"])

# Imposta manualmente l'aspetto
device = "unified"
st.session_state.device = device





# ===== MENU ICONICO (ordine definitivo e nomi finali) =====

menu_mobile = [
    {"label": "📊 Filippoide",        "view": "filippoide"},
    {"label": "🏆 Killbet Arena",     "view": "classifica"},
    {"label": "📅 Giornate",          "view": "giornate"},
    {"label": "ℹ️ Legenda",           "view": "legenda"},
    {"label": "🐔 Polli & Volpi",     "view": "polli_volpi"},
    {"label": "💰 Cassa",             "view": "movimenti"},
]


def torna_home():
    st.session_state.view = "home"


                    # ==================== PANNELLO 1: FILIPPOIDE ====================

def mostra_filipp():
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("## 🧮 Classifica Storica <b>Filippoide</b>", unsafe_allow_html=True)

    # ===== SLIDER GIORNATA (solo per questa sezione) =====
    ultima = 1
    for g in sorted(df["giornata"].unique()):
        # Se la giornata ha tutti gli esiti compilati, la consideriamo completata
        if not df[df["giornata"] == g]["esito"].isna().any():
            ultima = g

    # 🔹 Memorizza e ricarica automaticamente l’ultima giornata completata
    if "slider_fino_a" not in st.session_state:
        st.session_state["slider_fino_a"] = ultima
    elif ultima > st.session_state["slider_fino_a"]:
        st.session_state["slider_fino_a"] = ultima

    fino_a = st.slider(
        "Mostra la situazione aggiornata fino alla giornata n°",
        1,
        NUM_GIORNATE,
        value=st.session_state["slider_fino_a"],
        key=f"slider_{st.session_state.view}"  # chiave unica per ogni sezione
    )

    st.session_state["slider_fino_a"] = fino_a

    # Inizializzazione preventiva per evitare warning "non definito"
    giornata_flag = {}
    giornate_all_win = []
    cashout_days = []

    celebration_box = st.empty()  # ✅ box locale per le celebrazioni


    # --- MINI COMPUTE (ricalcolo locale per avere flag e vincite) ---
    try:
        (_classifica, _df_polli, _df_volpi, _df_tab, _df_fili2, _df_gen2,
        giornata_flag, _df_cassa, _df_mov, _df_seg,
        giorno_player_extra, pollo_name, volpe_name,
        last_all_win, giornate_all_win, cashout_days) = compute_all(
            st.session_state.data,
            fino_a=fino_a,
            ricariche=st.session_state.get("ricariche", {}),
            cashouts=st.session_state.get("cashouts", {})
        )
    except Exception:
        pass

    # --- LOGICA UNICA DI ATTIVAZIONE CELEBRAZIONI (usa celebration_box) ---
    try:
        selected_day = int(fino_a)

        # Dati base dalla session (importi cashout)
        cashouts = (st.session_state.get("cashouts", {}) or {})
        co_val = cashouts.get(selected_day)

        # Giorni 5/5 (no cash-out) -> {giornata: importo}
        _allwin_amount = {g: imp for g, imp in (giornate_all_win or [])}

        # Flag robusto
        flag = (
            (st.session_state.get("giornata_flag") or {}).get(selected_day)
            or (giornata_flag or {}).get(selected_day)
        )

        has_cashout = (co_val is not None) and (float(co_val) != 0.0)
        is_allwin_list = selected_day in _allwin_amount

        # Svuota SEMPRE prima; se non deve mostrare nulla, resta vuoto
        celebration_box.empty()

        # Attiva SOLO la celebrazione corretta
        if has_cashout:
            if flag == "CASH_ALL_WIN":
                celebrate_cashout_allwin(selected_day, co_val)
            elif flag in ("CASH_POLLO", "CASH_POLLO_FANTASMA"):
                celebrate_cashout_quasi(selected_day, co_val)
            elif flag and str(flag).startswith("CASH_"):
                celebrate_cashout(selected_day, co_val)
        elif is_allwin_list:
            celebrate_allwin(selected_day, _allwin_amount[selected_day])

    except Exception as _cele_e:
        # Non bloccare mai l'app per le celebrazioni
        pass

    # Tabella compatta con 👑 a MG78IT
    det_rows = []
    df_giorno = st.session_state.data[st.session_state.data["giornata"]==fino_a]
    for p in PLAYERS:
        saldo = df_fili[p].iloc[fino_a] if fino_a < len(df_fili) else df_fili[p].iloc[-1]
        try:
            d_val = float(saldo - df_fili[p].iloc[fino_a-1]) if fino_a-1 >= 0 else float(saldo)
        except:
            d_val = 0.0
        q_vis=""
        qrow = df_giorno[df_giorno["giocatore"] == p]
        if not qrow.empty:
            q_raw = qrow.iloc[0].get("quota")
            qf = _try_float(q_raw)
            q_vis = "" if qf is None else fmt1(qf)
        else:
            q_vis = ""
        display_name = p + (" 👑" if p=="MG78IT" else "")
        det_rows.append({"GIOCATORE": display_name, "Saldo": saldo, "Quota giornata": q_vis, "Δ giornata": d_val})

    df_fili_rank = pd.DataFrame(det_rows).sort_values("Saldo", ascending=False).reset_index(drop=True)

    # Convertiamo "Quota giornata" in numerico per forzare l'allineamento automatico a destra
    if "Quota giornata" in df_fili_rank.columns:
        df_fili_rank["Quota giornata"] = (
            df_fili_rank["Quota giornata"]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .apply(lambda x: float(x) if x.replace('.', '', 1).isdigit() else None)
        )

        # Manteniamo l'ordine visivo delle colonne
        df_fili_rank = df_fili_rank[["GIOCATORE", "Saldo", "Δ giornata", "Quota giornata"]]


    def paint_fili_compact(df_in):
        # colonne numeriche/di contenuto da centrare
        cols_nums = ["Saldo", "Quota giornata", "Δ giornata"]

        def name_style(v):
            base_name = str(v)
            key = "MG78IT" if base_name.startswith("MG78IT") else base_name
            fg = NAME_COLORS.get(key, ("#e9e9e9", None))[0]
            # testo nome colorato e centrato
            return f"color:{fg}; font-weight:800; text-align:center;"

        # applichiamo stile al nome, poi forziamo il centramento di header e celle con set_table_styles
        sty = df_in.style.applymap(name_style, subset=["GIOCATORE"])

        # proprietà per le colonne numeriche: centratura e colore
        sty = sty.set_properties(**{"text-align": "center"}, subset=cols_nums)
            # Sposta leggermente a destra solo la colonna "Quota giornata"
        if "Quota giornata" in df_in.columns:
            sty = sty.set_properties(subset=["Quota giornata"], **{"text-align": "right", "padding-right": "10px"})

        sty = sty.set_properties(**{"color": "#ffffff"}, subset=cols_nums)

        # dimensioni/celle fisse (opzionale ma aiuta la leggibilità)
        for c in cols_nums:
            if c in df_in.columns:
                sty = sty.set_properties(subset=[c], **{"min-width": "90px", "width": "90px", "max-width": "90px"})

        # Forziamo l'allineamento centrato anche per header e per tutte le celle (più robusto)
        sty = sty.set_table_styles([
            {"selector": "th.col_heading", "props": [("text-align", "center")]},
            {"selector": "td", "props": [("text-align", "center")]},
        ], overwrite=False)

        return sty

    # Allinea a destra solo la colonna "Quota giornata" nel widget st.dataframe
    st.markdown(
        """
        <style>
        /* Trova la colonna Quota giornata (4ª colonna) e allinea i valori a destra */
        [data-testid="stDataFrame"] div[role="gridcell"][aria-colindex="4"],
        [data-testid="stDataFrame"] div[role="columnheader"][aria-colindex="4"] {
            justify-content: flex-end !important;
            text-align: right !important;
            padding-right: 14px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Funzione di formattazione sicura per evitare errori con celle None o vuote
    def safe_fmt(x):
        try:
            return f"{x:.2f}" if pd.notnull(x) else ""
        except Exception:
            return ""

    st.dataframe(
        paint_fili_compact(
            df_fili_rank.round({"Quota giornata": 2})  # Arrotonda solo la colonna visiva
        ).format({
            "Saldo": fmt1,
            "Δ giornata": fmt1,
            "Quota giornata": safe_fmt,  # <-- usa formattazione sicura
        }),
        hide_index=True,
        use_container_width=True
    )

                # Grafico Filippoide
    try:
        if not df_fili.empty:
            df_cut=df_fili[df_fili["Giornata"]<=fino_a].copy()
            df_cut["Giornata"]=df_cut["Giornata"].astype(int)
            if "MG78IT" in df_cut.columns:
                df_cut = df_cut.rename(columns={"MG78IT":"MG78IT 👑"})
            long=df_cut.melt(id_vars=["Giornata"], var_name="Giocatore", value_name="Valore")
            alt_colors={"ANGEL":"#0B5ED7","GARIBALDI":"#FF00FF","CHRIS":"#19a319","MG78IT 👑":"#FFFFFF","FILLIP":"#00BFFF"}
            ch=alt.Chart(long).mark_line(point=True).encode(
                x=alt.X('Giornata:O', sort=None),
                y=alt.Y('Valore:Q', title='Filippoide cumulata'),
                color=alt.Color('Giocatore:N', scale=alt.Scale(domain=list(alt_colors.keys()), range=list(alt_colors.values()))),
                tooltip=['Giornata','Giocatore','Valore']
            ).properties(height=320)
            st.altair_chart(ch, use_container_width=True)
    except Exception:
        pass
    

                # ==================== PANNELLO 2: POLLI & VOLPI ====================

def mostra_polli_volpi():
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("### 🐔 Polli + Danno")

    df_polli_view = df_polli.copy()
    if "POLLI" in df_polli_view.columns and "DANNO" in df_polli_view.columns:
        try:
            df_polli_view["DANNO_num"] = (
                df_polli_view["DANNO"]
                .astype(str)
                .str.extract(r"([\d,\.]+)")[0]
                .str.replace(",", ".", regex=False)
                .astype(float)
                .fillna(0)
            )
            df_polli_view = (
                df_polli_view.sort_values(
                    by=["POLLI", "DANNO_num"],
                    ascending=[False, False],
                    kind="mergesort"
                )
                .drop(columns=["DANNO_num"])
                .reset_index(drop=True)
            )
        except Exception as e:
            st.warning(f"Impossibile ordinare Polli+Danno: {e}")
    else:
        df_polli_view = df_polli.copy()

    st.dataframe(
        paint_names_only(df_polli_view).set_properties(
            subset=["POLLI"], **{"min-width": "60px", "width": "60px", "max-width": "60px", "text-align": "center"}
        ).set_properties(
            subset=["DANNO"], **{"min-width": "160px", "width": "160px", "max-width": "160px", "text-align": "center"}
        ),
        hide_index=True,
        use_container_width=True
    )

    st.markdown("### 🦊 Volpi")
    df_volpi_view = (
        df_volpi.copy()
        .sort_values("VOLPI", ascending=False, kind="mergesort")
        .reset_index(drop=True)
    )
    st.dataframe(
        paint_names_only(df_volpi_view).set_properties(
            subset=["VOLPI"], **{"min-width": "60px", "width": "60px", "max-width": "60px", "text-align": "center"}
        ),
        hide_index=True,
        use_container_width=True
    )
    st.markdown("</div>", unsafe_allow_html=True)




                    # === PANNELLO KILLBET ARENA ===

def mostra_classifica():
    st.session_state.view = "classifica"
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("### 🏆 Killbet Arena")

    classifica = pd.DataFrame()
    df_gen = pd.DataFrame()

    df = st.session_state.data.copy()  # ✅ usa sempre i dati aggiornati
    
        # ===== SLIDER GIORNATA =====
    df0 = st.session_state.data
    ultima = 1
    for g in sorted(df0["giornata"].unique()):
        if not df0[df0["giornata"] == g]["esito"].isna().any():
            ultima = g


    if "slider_fino_a" not in st.session_state:
        st.session_state["slider_fino_a"] = ultima
    elif ultima > st.session_state["slider_fino_a"]:
        st.session_state["slider_fino_a"] = ultima

    fino_a = st.slider(
        "Mostra la situazione aggiornata fino alla giornata n°",
        1,
        NUM_GIORNATE,
        value=st.session_state["slider_fino_a"],
        key=f"slider_{st.session_state.view}_fix"  # fix stabile per evitare reset o schermo nero
    )
    st.session_state["slider_fino_a"] = fino_a
    st.session_state["fino_a"] = fino_a


    # Inizializzazione preventiva
    giornata_flag = {}
    giornate_all_win = []
    cashout_days = []

    # Usa sempre il contenitore globale
    celebration_box = st.session_state["celebration_box"]
    # Recupera eventuali DataFrame salvati dalla sessione
    classifica = st.session_state.get("classifica", pd.DataFrame())
    df_gen = st.session_state.get("df_gen", pd.DataFrame())
    df_polli = st.session_state.get("df_polli", pd.DataFrame())
    df_volpi = st.session_state.get("df_volpi", pd.DataFrame())

    # ===== RICALCOLO DATI =====
    try:
        (classifica, df_polli, df_volpi, df_tab, df_fili, df_gen,
        giornata_flag, df_cassa, df_mov, df_seg,
        giorno_player_extra, pollo_name, volpe_name,
        last_all_win, giornate_all_win, cashout_days) = compute_all(
            st.session_state.data,
            fino_a=fino_a,
            ricariche=st.session_state.get("ricariche", {}),
            cashouts=st.session_state.get("cashouts", {})
        )

        # salva i flag in sessione per le celebrate_*
        st.session_state["giornata_flag"] = giornata_flag or {}

        # ✅ Salva i DataFrame principali in sessione per evitare reset allo spostamento dello slider
        st.session_state["classifica"] = classifica
        st.session_state["df_gen"] = df_gen
        st.session_state["df_polli"] = df_polli
        st.session_state["df_volpi"] = df_volpi

    
    except Exception as e:
        st.warning(f"Errore ricalcolo dati o celebrazioni: {e}")
        # ✅ Reset completo delle variabili locali usate nel pannello Killbet Arena
        classifica = pd.DataFrame()
        df_gen = pd.DataFrame()
        df_polli = pd.DataFrame()
        df_volpi = pd.DataFrame()


    # --- LOGICA UNICA DI ATTIVAZIONE CELEBRAZIONI ---
    try:
        selected_day = int(fino_a)
        celebration_box.empty()

        # Dati base dalla session (importi cashout)
        cashouts = (st.session_state.get("cashouts", {}) or {})
        co_val = cashouts.get(selected_day)

        # Giorni 5/5 (no cash-out)
        _allwin_amount = {g: imp for g, imp in (giornate_all_win or [])}

        # Flag robusto
        flag = (
            (st.session_state.get("giornata_flag") or {}).get(selected_day)
            or (giornata_flag or {}).get(selected_day)
        )

        has_cashout = (co_val is not None) and (float(co_val) != 0.0)
        is_allwin_list = selected_day in _allwin_amount

        # Attiva SOLO la celebrazione corretta
        if has_cashout:
            if flag == "CASH_ALL_WIN":
                celebrate_cashout_allwin(selected_day, co_val)
            elif flag in ("CASH_POLLO", "CASH_POLLO_FANTASMA"):
                celebrate_cashout_quasi(selected_day, co_val)
            elif flag and str(flag).startswith("CASH_"):
                celebrate_cashout(selected_day, co_val)
        elif is_allwin_list:
            celebrate_allwin(selected_day, _allwin_amount[selected_day])

    except Exception:
        # Non bloccare mai l'app per le celebrazioni
        pass

    # ===== TABELLA CLASSIFICA =====
    cols = [
        "GIOCATORE", "Totale", "Punti base",
        "Penalità quote basse",
        "Bonus differenza quote", "Malus differenza quote",
        "Bonus Volpe", "Malus Pollo", "Malus Pollo Fantasma",
        "Bonus Champions", "Bonus Coraggio",
        "Malus Fantasmino",
        "Bonus Tutti Vincenti", "Malus Tutti Perdenti"
    ]

    if isinstance(classifica, pd.DataFrame) and set(cols).issubset(classifica.columns):
        st.dataframe(
            paint_names_only(classifica[cols]).format({
                "Totale": fmt1, "Punti base": fmt1,
                "Penalità quote basse": fmt1,
                "Bonus differenza quote": fmt1, "Malus differenza quote": fmt1,
                "Bonus Volpe": fmt1, "Malus Pollo": fmt1, "Malus Pollo Fantasma": fmt1,
                "Bonus Champions": fmt1,
                "Malus Fantasmino": fmt1,
                "Bonus Coraggio": fmt1,
                "Bonus Tutti Vincenti": fmt1,
                "Malus Tutti Perdenti": fmt1,
            }),
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("Nessun dato classifica disponibile per la giornata selezionata.")

    # ===== GRAFICO KILLBET ARENA =====
    try:
        if not df_gen.empty:
            df_gen_cut = df_gen[df_gen["Giornata"] <= fino_a].copy()
            df_gen_cut = df_gen_cut.dropna(axis=1, how="all")

            long = df_gen_cut.melt(id_vars=["Giornata"], var_name="Giocatore", value_name="Punti")

            alt_colors = {
                "ANGEL": "#0B5ED7",
                "GARIBALDI": "#FF00FF",
                "CHRIS": "#19a319",
                "MG78IT": "#FFFFFF",
                "FILLIP": "#00BFFF"
            }

            ch_lines = alt.Chart(long).mark_line(opacity=0.85).encode(
                x=alt.X('Giornata:O', sort=None),
                y=alt.Y('Punti:Q', title='Killbet Arena (progressione)', scale=alt.Scale(zero=False, nice=True)),
                color=alt.Color('Giocatore:N', scale=alt.Scale(domain=list(alt_colors.keys()), range=list(alt_colors.values()))),
                tooltip=['Giornata', 'Giocatore', 'Punti']
            )

            long["same_score"] = long.groupby("Giornata")["Punti"].transform(lambda v: v.duplicated(keep=False))

            base = alt.Chart(long).transform_window(
                rank='row_number()',
                sort=[alt.SortField('Giocatore', order='ascending')],
                groupby=['Giornata', 'Punti']
            )

            ch_points_single = base.mark_point(filled=True, size=40, strokeWidth=1).encode(
                x='Giornata:O',
                y='Punti:Q',
                color=alt.Color('Giocatore:N', scale=alt.Scale(domain=list(alt_colors.keys()), range=list(alt_colors.values())), legend=None)
            )

            ch_points_full = base.transform_filter('datum.same_score == true').mark_point(filled=True, size=200, strokeWidth=2).encode(
                x='Giornata:O',
                y='Punti:Q',
                color=alt.Color('Giocatore:N', scale=alt.Scale(domain=list(alt_colors.keys()), range=list(alt_colors.values())), legend=None)
            )

            ch_points_conc = base.transform_filter('datum.same_score == true && datum.rank > 1').mark_point(filled=False, strokeWidth=4).encode(
                x='Giornata:O',
                y='Punti:Q',
                size=alt.Size('rank:O', scale=alt.Scale(range=[130, 170, 210, 250, 290]), legend=None),
                color=alt.Color('Giocatore:N', scale=alt.Scale(domain=list(alt_colors.keys()), range=list(alt_colors.values())), legend=None)
            )

            ch = (ch_lines + ch_points_single + ch_points_full + ch_points_conc).properties(height=320)
            st.altair_chart(ch, use_container_width=True)

    except Exception:
        pass

    st.markdown("</div>", unsafe_allow_html=True)




                        # === PANNELLO LEGENDA PUNTI ===

def mostra_legenda():
    df_legenda = pd.DataFrame([
        {"Sezione": "Punti base (1v1)", "Regola": "Uno vince / uno perde", "Valore": "3 (V) - 0 (P)"},
        {"Sezione": "Punti base (1v1)", "Regola": "Entrambi vincono", "Valore": "2 a testa"},
        {"Sezione": "Punti base (1v1)", "Regola": "Entrambi perdono", "Valore": "1 a testa"},
        {"Sezione": "Bonus Coraggio", "Regola": "Assegnato solo ai vincenti; posizione per quota (decrescente); soglia ≤ 1,50 → 0", "Valore": "Temerario +1,10; Audace +0,80; Prudente +0,50; Braccino corto +0,30; Fifone +0,10"},
        {"Sezione": "🚽 Penalità quota bassa (1,40–1,60)", "Regola": "Si applica nei confronti diretti (V–P, V–V, P–P) ai giocatori che scelgono quote prudenti. Il simbolo 🚽 indica scommesse troppo 'comode' o poco coraggiose.", "Valore": "V vincente −1,5 / V–V −1 ciascuno / P–P −0,5 ciascuno"},
        {"Sezione": "🤡 Penalità quota Ridiculus (<1,40)", "Regola": "Si applica nei confronti diretti (V–P, V–V, P–P) ai giocatori che scelgono quote troppo basse o 'ridicole'. Il simbolo 🤡 identifica la fascia più penalizzante.", "Valore": "V vincente −2 / V–V −1,5 ciascuno / P–P −1 ciascuno"},
        {"Sezione": "⚖️👍 Bonus differenza quote", "Regola": "Assegnato al giocatore con la quota più alta nei casi V–V e V–P.", "Valore": "+Δquote (max +3)"},
        {"Sezione": "⚖️👎 Malus differenza quote", "Regola": "Assegnato al giocatore con la quota più bassa (V–P) o più alta (P–P).", "Valore": "−Δquote (max −3)"},
        {"Sezione": "Tutti Vincenti (5V)", "Regola": "Senza cash-out: +5/+4/+3/+2/+1 dalla quota più alta alla più bassa", "Valore": "+5 / +4 / +3 / +2 / +1"},
        {"Sezione": "Tutti Perdenti (5P)", "Regola": "Quota più alta −1 … quota più bassa −5", "Valore": "−1 / −2 / −3 / −4 / −5"},
        {"Sezione": "🦊 Volpe (unico vincente)", "Regola": "Quota più alta +6 … più bassa +2 (se quote uguali, conta la più favorevole)", "Valore": "+6 / +5 / +4 / +3 / +2"},
        {"Sezione": "🐔 Pollo (unico perdente)", "Regola": "Quota più bassa −6 … più alta −2 (se quote uguali, conta la più favorevole)", "Valore": "−6 / −5 / −4 / −3 / −2"},
        {"Sezione": "Champions League", "Regola": "Per ogni 'V' in giornata Champions", "Valore": "+2 × quota"},
        {"Sezione": "👻 Fantasmino", "Regola": "Mancata scommessa= -5. L’avversario: se V = +2, se P = +1 e subisce eventuali penalità per quote 🚽/🤡).", "Valore": "👻 −5 / Avversario +2 o +1"},
        {"Sezione": "Filippoide", "Regola": "V: quota − 1 • P: −1 • 👻 Fantasmino: −1", "Valore": "cumulata da giornata 0"},
    ])

    st.markdown("### ℹ️ Legenda punti")
    st.markdown("""
    <style>
    table {width: 100%; border-collapse: collapse; font-size: 1.1rem;}
    th, td {border: 1px solid #444; padding: 8px 10px; text-align: center;}
    th {background-color: #0a2a6b; color: white; font-weight: 900; text-transform: uppercase;}
    tr:nth-child(even) {background-color: #111;}
    tr:nth-child(odd) {background-color: #1a1a1a;}
    tr:hover {background-color: #222;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(df_legenda.to_html(index=False, escape=False), unsafe_allow_html=True)


                        # PANNELLO GIORNATE

def mostra_giornate():
    def giornata_card_html(g, subdf):
        # Importo da mostrare
        amount_html = ""
        imp_val = None

        # 1) Cash-out vince sempre la priorità
        if g in cashout_days:
            imp_val = st.session_state.get("cashouts", {}).get(g)

        # 2) Nessun cash-out → se la giornata è ALL_WIN e hai messo una vincita manuale, mostra quella
        elif (giornata_flag or {}).get(g) == "ALL_WIN":
            mv = (st.session_state.get("manual_wins", {}) or {}).get(g)
            if mv is not None:
                imp_val = float(mv)


        # Recupera lo stake salvato in quella giornata
        day_stake = None
        try:
            day_stake = df[df["giornata"] == g]["stake"].iloc[0]
        except Exception:
            day_stake = None

        # Flag della giornata
        flag = (giornata_flag or {}).get(g)

        # Default
        base_class = "card"
        title = f"Giornata {g}"

        if flag == "CASH_ALL_WIN":
            base_class = "card card-cashout"
            title = f"💸 Giornata {g} — CASH OUT TUTTI VINCENTI"
            try:
                # Estraggo solo i vincenti reali della giornata
                subset = df[df["giornata"] == g]
                subset = subset[subset["esito"] == "V"]

                # Mappa {giocatore: quota}
                quote_map = subset.groupby("giocatore")["quota"].first().to_dict()

                if len(quote_map) == 5:
                    # Ordina le quote in modo decrescente
                    sorted_players = sorted(quote_map.items(), key=lambda x: x[1], reverse=True)
                    bonus_map = {
                        sorted_players[0][0]: 5,
                        sorted_players[1][0]: 4,
                        sorted_players[2][0]: 3,
                        sorted_players[3][0]: 2,
                        sorted_players[4][0]: 1
                    }

                    # Applica i bonus sommando ai punteggi cumulativi (non azzera!)
                    for pl, bonus_val in bonus_map.items():
                        # Recupera punteggio precedente
                        prev_pts = df_gen.loc[df_gen["Giornata"] == g - 1, pl].iloc[-1] if g > 1 and not df_gen.empty else 0
                        # Aggiorna la colonna Bonus Tutti Vincenti (se esiste)
                        df.loc[df["giocatore"] == pl, "bonus_allwin"] = (
                            df.get("bonus_allwin", 0) + bonus_val
                        )
                        # Aggiorna la Killbet Arena mantenendo la progressione
                        df_gen.loc[df_gen["Giornata"] == g, pl] = prev_pts + bonus_val

            except Exception as e:
                st.warning(f"Errore nel calcolo bonus CASH OUT TUTTI VINCENTI: {e}")
            
        elif flag == "CASH_FANTASMA":
            base_class = "card card-cashfantasma"
            title = f"👻 Giornata {g} — CASH OUT con FANTASMA{amount_html}"
            
        elif flag == "CASH_POLLO":
            base_class = "card card-cashpollo"
            loser = color_span(pollo_name.get(g, "")) or ""
            title = f"🐔 Giornata {g} — CASH OUT con POLLO: {loser}{amount_html}"
        
        elif flag == "CASH_OUT":  # generico
            base_class = "card card-cashout"
            title = f"🪙 Giornata {g} — CASH OUT QUASI TUTTI VINCENTI{amount_html}"
        
        elif flag == "QUASI_ALL_WIN":
            base_class = "card card-quasiwin"
            title = f"🥈 Giornata {g} — I Fanta Vincenti 👻 (Quasi Tutti Vincenti)"
        
        elif flag == "ALL_WIN":
            base_class = "card card-allwin"
            title = f"🪙🪙🪙🪙🪙 Giornata {g} — TUTTI VINCENTI"
        
        elif flag in ("POLLO", "POLLO_FANTASMA"):
            loser = color_span(pollo_name.get(g, ""))
            base_class = "card card-pollo"
            if flag == "POLLO_FANTASMA":
                emoji, label = "🐔👻", "POLLO FANTASMA"
            else:
                emoji, label = "🐔", "POLLO"

            # Danno economico SOLO da “Perdita Pollo” (manuale)
            man_loss = (st.session_state.get("manual_losses", {}) or {}).get(g)
            title = f"{emoji} Giornata {g} — {label}: {loser}"
            if man_loss is not None:
                title += f" — Danno: <span style='font-weight:900'>{eur(man_loss)} €</span>"

            # Mostra sempre lo stake del giorno se presente
            if day_stake not in (None, "", "null"):
                title += (
                    f"<div style='text-align:right; color:#ff3333; font-weight:900;'>"
                    f"💶 Giocata: {eur(day_stake)} €</div>"
                )

                        
        elif flag == "VOLPE":
            base_class = "card card-volpe"
            winner = color_span(volpe_name.get(g, "")) or ""
            title = f"🦊 Giornata {g} — VOLPE: {winner}"
            
        elif flag == "ALL_LOSE":
            base_class = "card card-alllose"
            title = f"<span style='font-size:26px;'>💩💩💩💩💩</span> Giornata {g} — TUTTI PERDENTI"

        else:
            base_class = "card"
            title = f"Giornata {g}"

            # --- SOLO per ALL_WIN aggiungo importo e stake nel titolo ---
        if flag == "ALL_WIN":
            if imp_val not in (None, "", "null"):
                title += f"<div style='font-weight:900'>{eur(imp_val)} €</div>"
            if day_stake not in (None, "", "null"):
                title += (
                    f"<div style='text-align:right; color:#ff3333; font-weight:900;'>"
                    f"💶 Giocata: {eur(day_stake)} €</div>"
                )    

        # Variabili di supporto
        champs = st.session_state.get("champions_days", [])
        cashouts = (st.session_state.get("cashouts", {}) or {})

        # Importo del cash out
        co_raw = cashouts.get(g, None)
        co_val = _try_float(co_raw)
        co_val_f = co_val if co_val is not None else 0.0
        has_cashout = (co_val_f > 0)

        amount_html = ""
        if has_cashout:
            amount_html = f" — Importo: <span style='font-weight:900'>{eur(co_val_f)} €</span>"

        # Assegna classi e titoli
        if (g in champs) and (not has_cashout):
            base_class = 'card card-champday'
            title = f'🏆🏆🏆🏆🏆 Giornata Champions {g}'

        elif has_cashout:
            if flag == "CASH_FANTASMA":
                base_class = "card card-cashfantasma"
                title = f"👻 Giornata {g} — CASH OUT con FANTASMA{amount_html}"

            elif flag == "CASH_POLLO_FANTASMA":
                base_class = "card card-cashpollofantasma"
                loser = color_span(pollo_name.get(g, ""))
                title = f"🐔👻 Giornata {g} — CASH OUT con POLLO + FANTASMA: {loser}{amount_html}"

            elif flag == "CASH_POLLO":
                base_class = "card card-cashpollo"
                loser = color_span(pollo_name.get(g, ""))
                title = f"🐔 Giornata {g} — CASH OUT con POLLO: {loser}{amount_html}"

            else:  # cash out generico
                base_class = "card card-cashout"
                title = f"💸 Giornata {g} — CASH OUT{amount_html}"

            # In tutti i tipi di cash out mostriamo anche lo stake
            if day_stake not in (None, "", "null"):
                title += (
                    f"<div style='text-align:right; color:#ff3333; font-weight:900;'>"
                    f"💶 Giocata: {eur(day_stake)} €</div>"
                )

        extras = giorno_player_extra.get(g, {})

        # --- Extra (bonus/malus con icone) ---
                        
        def extra_for(player_name):
            ICON = {
                "fox": "🦊",
                "hen": "🐔",
                "hen_ghost": "🐔👻",
                "ghost": "👻",
                "champ": "✖️2",
                "allwin": "🏅",
                "alllose": "💩",
            }
            def courage_emoji(why):
                w = (why or "").lower()
                if "temerario" in w: return "🦁"
                if "audace" in w:    return "💪"
                if "prudente" in w:  return "🐢"
                if "braccino" in w:  return "🤏"
                if "fifone" in w:    return "🐇"
                return "🔥"
            out = ""
            fg = NAME_COLORS.get(player_name, ("#e9e9e9", None))[0]
            for kind, pts, why in extras.get(player_name, []):
                emoji = courage_emoji(why) if kind == "courage" else ICON.get(kind, "")
                if pts is None:
                    out += f"<span class='chip' style='color:{fg}'>{emoji} <small>({why})</small></span>"
                else:
                    sign = "+" if float(pts) >= 0 else ""
                    out += f"<span class='chip' style='color:{fg}'>{emoji} {sign}{fmt1(pts)} <small>({why})</small></span>"
            return out

        # --- Match 1vs1 ---

        def row(partita):
            if not (subdf["partita"] == partita).any():
                return ""
            p = subdf[subdf["partita"] == partita].iloc[0]
            casa_name = p["CASA"]
            osp_name = p["OSPITE"]

            q_casa = f" ({float(p['Q_CASA']):.2f})" if p.get("Q_CASA") not in (None, "") else ""
            q_osp = f" ({float(p['Q_OSP']):.2f})" if osp_name and p.get("Q_OSP") not in (None, "") else ""

            def _is_ghost(name):
                return any(k == "ghost" for (k, _, _) in extras.get(name, []))
            if _is_ghost(casa_name):
                q_casa = " <span class='qbr'>👻</span>"
            if osp_name and _is_ghost(osp_name):
                q_osp = " <span class='qbr'>👻</span>"

            casa_col = NAME_COLORS.get(casa_name, ("#e9e9e9", None))[0]
            osp_col = NAME_COLORS.get(osp_name, ("#e9e9e9", None))[0] if osp_name else "#e9e9e9"
            casa = f"<span style='color:{casa_col};font-weight:800'>{casa_name}{q_casa}</span>"
            osp = f"<span style='color:{osp_col};font-weight:800'>{osp_name}{q_osp}</span>" if osp_name else ""

            def esito_display(esito, is_ghost):
                if is_ghost:
                    return "👻"
                return esito_colored(esito)

            e_c = esito_display(p["E_CASA"], p.get("F_CASA", False))
            e_o = esito_display(p["E_OSP"], p.get("F_OSP", False))

            def fval(key):
                try: return float(p.get(key, 0) or 0)
                except Exception: return 0.0

            tot_casa = fval("BASE_CASA") + fval("B_CASA") + fval("M_CASA") + fval("HALF_CASA")
            tot_osp = fval("BASE_OSP") + fval("B_OSP") + fval("M_OSP") + fval("HALF_OSP")
            for _, pts, _ in extras.get(casa_name, []):
                if pts: tot_casa += float(pts)
            for _, pts, _ in extras.get(osp_name, []):
                if pts: tot_osp += float(pts)

            def fmt_result(v):
                return str(int(v)) if float(v).is_integer() else f"{v:.2f}"
            risultato = (
                f"<div class='es'><b>Risultato goliardico:</b> "
                f"<span style='color:{casa_col}'>{casa_name} {fmt_result(tot_casa)}</span> – "
                f"<span style='color:{osp_col}'>{fmt_result(tot_osp)} {osp_name}</span></div>"
            )

            def chip(label, val, color, icon=""):
                if val == 0 or val == "" or val is None: return ""
                sign = "+" if float(val) > 0 else ""
                return f"<span class='chip' style='color:{color}'>{icon} {label}: {sign}{fmt1(val)}</span>"

            # --- Sezione visualizzazione punteggi casa/ospite con penalità aggiornate ---
            # Determina la descrizione corretta del tipo di penalità in base alla quota
            def label_penalita(q):
                if q is None:
                    return None
                try:
                    qf = float(q)
                    if qf < 1.40:
                        return "🤡 Penalità quota Ridiculus"
                    elif 1.40 <= qf <= 1.60:
                        return "🚽 Penalità quota bassa"
                except Exception:
                    return None
                return None

            # Determina il simbolo e il testo dinamico
            pen_casa_label = label_penalita(p.get("Q_CASA"))
            pen_osp_label = label_penalita(p.get("Q_OSP"))

            casa_steps = (
                f"<div class='steps'>"
                f"{chip('punti base', fval('BASE_CASA'), casa_col, '🎯')}"
                f"{chip('Bonus diff. quote', fval('B_CASA'), casa_col, '⚖️👍')}"
                f"{chip(pen_casa_label if pen_casa_label else '—', fval('HALF_CASA'), casa_col, '') if pen_casa_label else ''}"
                f"{chip('malus diff.quote', fval('M_CASA'), casa_col, '⚖️👎')}"
                f"{extra_for(casa_name)}"
                f"</div>"
                f"<span class='chip strong' style='color:{casa_col}'>💰 Totale punti giornata di {casa_name.upper()}: {fmt1(tot_casa)}</span>"
            )

            osp_steps = ""
            if osp_name:
                osp_steps = (
                    f"<div class='steps'>"
                    f"{chip('punti base', fval('BASE_OSP'), osp_col, '🎯')}"
                    f"{chip('Bonus diff. quote', fval('B_OSP'), osp_col, '⚖️👍')}"
                    f"{chip(pen_osp_label if pen_osp_label else '—', fval('HALF_OSP'), osp_col, '') if pen_osp_label else ''}"
                    f"{chip('malus diff.quote', fval('M_OSP'), osp_col, '⚖️👎')}"
                    f"{extra_for(osp_name)}"
                    f"</div>"
                    f"<span class='chip strong' style='color:{osp_col}'>💰 Totale punti giornata di {osp_name.upper()}: {fmt1(tot_osp)}</span>"
                )


            return (
                f"<div class='riga'>"
                f"<div class='vs'>{casa} vs {osp}</div>"
                f"<div class='es'>{e_c} – {e_o}</div>"
                f"{risultato}"
                f"{casa_steps}{osp_steps}"
                f"</div>"
            )

        # --- Giocatore a riposo 🛌 ---
                        
        def row_riposo(player_name):
            fg = NAME_COLORS.get(player_name, ("#e9e9e9", None))[0]
            tot = 0.0
            for _, pts, _ in extras.get(player_name, []):
                if pts:
                    try: tot += float(pts)
                    except: pass
            chips = extra_for(player_name)
            total_chip = (
                f"<span class='chip strong' style='color:{fg}'>"
                f"💰 Totale punti giornata di {player_name.upper()}: {fmt1(tot)}</span>"
            )
            return (
                f"<div class='riga'>"
                f"<div class='vs'><span style='color:{fg};font-weight:800'>{player_name} 🛌 — RIPOSO</span></div>"
                f"<div class='steps'>{chips}</div>"
                f"{total_chip}"
                f"</div>"
            )

        # --- RIP dal DF ---
        rip_html = ""
        if (subdf["partita"] == "RIP").any():
            rp = subdf[subdf["partita"] == "RIP"].iloc[0]
            try:
                row_rip_df = st.session_state.data[
                    (st.session_state.data["giornata"] == g) & 
                    (st.session_state.data["slot"] == "RIP")
                ].iloc[0]
                is_ghost_rip = bool(row_rip_df.get("fantasmino", False))
            except Exception:
                is_ghost_rip = False

            name_txt = rp["CASA"]
            rip_col = NAME_COLORS.get(name_txt, ('#e9e9e9', None))[0]

            if is_ghost_rip:
                qtxt = f" <span style='color:{rip_col};font-weight:800'>👻</span>"
                e_c = "👻"
            else:
                q_val = _try_float(rp.get("Q_CASA"))
                qtxt = f" <span style='color:{rip_col}'>({fmt1(q_val)})</span>" if q_val is not None else ""
                e_c = esito_colored(rp["E_CASA"])

            name = color_span(name_txt)


            # Usa la stessa logica degli altri giocatori (extra_for)
            rip_extra = extra_for(name_txt)
            
            # Calcolo totale punti del RIP dal giorno_player_extra
            tot_rip = 0.0
            for kind, pts, why in extras.get(name_txt, []):
                if pts is not None:
                    try:
                        tot_rip += float(pts)
                    except:
                        pass

            # Costruzione finale del riposo con chip e totale
            rip_html = (
                f"<div class='rip'><b style='color:{GOLD}'>RIPOSO</b>: "
                f"<span class='ripname'>{name}</span>{qtxt} — Esito: <b>{e_c}</b>"
                f"<div class='steps'>{rip_extra}</div>"
                f"<span class='chip strong' style='color:{NAME_COLORS.get(name_txt,('#e9e9e9',None))[0]}'>"
                f"💰 Totale punti giornata di {name_txt.upper()}: {fmt1(tot_rip)}</span>"
                f"</div>"
            )

                            # --- Corpo card finale ---
                            
        card_body = f"{row('1')}{row('2')}{rip_html}"
        return f"<div class='{base_class}'><div class='card-head'>{title}</div><div class='card-body'>{card_body}</div></div>"

    def subdf_for_g(g):
        sub=df_tab[df_tab["giornata"]==g]
        if sub.empty:
            f=FIXTURES[g-1]
            rows=[{"giornata":g,"partita":"1","CASA":f["CASA1"],"OSPITE":f["OSP1"],"Q_CASA":None,"Q_OSP":None,"E_CASA":None,"E_OSP":None},
                {"giornata":g,"partita":"2","CASA":f["CASA2"],"OSPITE":f["OSP2"],"Q_CASA":None,"Q_OSP":None,"E_CASA":None,"E_OSP":None},
                {"giornata":g,"partita":"RIP","CASA":f["RIP"],"OSPITE":"","Q_CASA":None,"Q_OSP":None,"E_CASA":None,"E_OSP":None}]
            return pd.DataFrame(rows)
        return sub

    CARDS_PER_ROW=4
    for start in range(1, NUM_GIORNATE+1, CARDS_PER_ROW):
        cols=st.columns(CARDS_PER_ROW)
        for i,col in enumerate(cols):
            g=start+i
            if g>NUM_GIORNATE: break
            with col: st.markdown(giornata_card_html(g, subdf_for_g(g)), unsafe_allow_html=True)
            
    st.markdown("</div>", unsafe_allow_html=True)




# ==================== PANNELLO 4: CASSA ====================

def mostra_movimenti():
    st.session_state.view = "movimenti"
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<h3 class='goldcell'>📊 Fondo Speculazioni Sportive 📊</h3>", unsafe_allow_html=True)
    
    df = st.session_state.data.copy()  # ✅ usa sempre i dati aggiornati

    # ===== SLIDER GIORNATA =====
    df0 = st.session_state.data  # ✅ stesso comportamento di Filippoide
    ultima = 1
    for g in sorted(df0["giornata"].unique()):
        if not df0[df0["giornata"] == g]["esito"].isna().any():
            ultima = g


    if "slider_fino_a" not in st.session_state:
        st.session_state["slider_fino_a"] = ultima
    elif ultima > st.session_state["slider_fino_a"]:
        st.session_state["slider_fino_a"] = ultima

    fino_a = st.slider(
        "Mostra la situazione aggiornata fino alla giornata n°",
        1, NUM_GIORNATE,
        value=st.session_state["slider_fino_a"],
        key=f"slider_{st.session_state.view}_fix"
    )
    st.session_state["slider_fino_a"] = fino_a
    st.session_state["fino_a"] = fino_a


    # Inizializzazione preventiva
    giornata_flag = {}
    giornate_all_win = []
    cashout_days = []

    # Usa il contenitore globale già creato
    celebration_box = st.session_state["celebration_box"]

    # ===== RICALCOLO DATI =====
    try:
        (classifica, df_polli, df_volpi, df_tab, df_fili, df_gen,
        giornata_flag, df_cassa, df_mov, df_seg,
        giorno_player_extra, pollo_name, volpe_name,
        last_all_win, giornate_all_win, cashout_days) = compute_all(
            st.session_state.data,
            fino_a=fino_a,
            ricariche=st.session_state.get("ricariche", {}),
            cashouts=st.session_state.get("cashouts", {})
        )

        # salva i flag per uso nelle celebrazioni
        st.session_state["giornata_flag"] = giornata_flag or {}

    except Exception as e:
        st.warning(f"Errore ricalcolo dati o celebrazioni: {e}")
        df_cassa = pd.DataFrame()
        df_mov = pd.DataFrame()
        df_seg = pd.DataFrame()

    # --- LOGICA CELEBRAZIONI ---
    try:
        selected_day = int(fino_a)
        celebration_box.empty()

        cashouts = (st.session_state.get("cashouts", {}) or {})
        co_val = cashouts.get(selected_day)
        _allwin_amount = {g: imp for g, imp in (giornate_all_win or [])}

        flag = (
            (st.session_state.get("giornata_flag") or {}).get(selected_day)
            or (giornata_flag or {}).get(selected_day)
        )

        has_cashout = (co_val is not None) and (float(co_val) != 0.0)
        is_allwin_list = selected_day in _allwin_amount

        if has_cashout:
            if flag == "CASH_ALL_WIN":
                celebrate_cashout_allwin(selected_day, co_val)
            elif flag in ("CASH_POLLO", "CASH_POLLO_FANTASMA"):
                celebrate_cashout_quasi(selected_day, co_val)
            elif flag and str(flag).startswith("CASH_"):
                celebrate_cashout(selected_day, co_val)
        elif is_allwin_list:
            celebrate_allwin(selected_day, _allwin_amount[selected_day])

    except Exception:
        pass

    # ===== GRAFICO CASSA =====
    try:
        if not df_seg.empty and not df_cassa.empty:
            col_domain = ["GOLD", "GREEN", "ORANGE", "RED", "BROWN"]
            col_range = [GOLD, "#16c60c", ORANGE, "#ff3b3b", BROWN]

                # ultima giornata utile (robusta anche se i valori non sono stringhe)
            try:
                if not df_mov.empty and "Giornata" in df_mov.columns:
                    s = (
                        df_mov["Giornata"]
                        .astype(str)                                 # converte sempre in stringa
                        .str.replace(",", ".", regex=False)          # es. RG5,0 → RG5.0
                        .str.extract(r"(\d+(?:\.\d+)?)")[0]          # estrae il numero 5 o 5.0
                    )
                    s = pd.to_numeric(s, errors="coerce")            # trasforma in numerico
                    last_day = int(s.dropna().max()) if not s.dropna().empty else 1
                else:
                    last_day = 1
            except Exception:
                last_day = 1

            # asse X con etichette personalizzate
            _ticks_df = (
                df_cassa.sort_values("x")[["x", "Giornata"]]
                .drop_duplicates(subset=["x"])
                .round(2)
            )
            _tick_vals = _ticks_df["x"].tolist()
            _map = {f"{v:.2f}": str(lbl) for v, lbl in _ticks_df.to_records(index=False)}
            _label_expr = "(" + "{%s}" % ", ".join([f"'{k}': '{v}'" for k, v in _map.items()]) + ")" + "[format(datum.value, '.2f')]"

            line = alt.Chart(df_seg).mark_line(size=4).encode(
                x=alt.X("x:Q",
                        title="Giornata",
                        axis=alt.Axis(values=_tick_vals, labelExpr=_label_expr,
                                    labelFlush=False, labelOverlap=True),
                        scale=alt.Scale(domain=(0, last_day + 0.5))),
                y=alt.Y("y:Q", title="Cassa €"),
                color=alt.Color("Colore:N",
                                scale=alt.Scale(domain=col_domain, range=col_range),
                                legend=None),
                detail="seg_id:N",
                order="ord:O"
            ).properties(height=340)

            chart = line + alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(
                color="#8B4513", strokeWidth=6
            ).encode(y="y:Q")

            # marker finale e valore attuale
            if not df_cassa.empty:
                last_pt = df_cassa.iloc[[-1]]
                chart += alt.Chart(last_pt).mark_point(size=160, color="gold", shape="diamond").encode(x="x:Q", y="y:Q")
                chart += alt.Chart(last_pt).mark_text(align="left", dx=10, dy=-10,
                                                    fontSize=16, fontWeight="bold",
                                                    color="gold").encode(
                    x="x:Q", y="y:Q", text=alt.Text("y:Q", format=".2f")
                )

            # emoji centrali
            all_emojis = []
            for seg_id, rows in df_seg.groupby("seg_id"):
                if len(rows) == 2:
                    p1, p2 = rows.to_dict("records")
                    mid_x = (p1["x"] + p2["x"]) / 2
                    mid_y = (p1["y"] + p2["y"]) / 2
                    col = p2["Colore"]
                    emoji = None
                    if p2["y"] > p1["y"]:
                        emoji = {"GREEN": "💵", "GOLD": "🪙", "ORANGE": "💶",
                                "BROWN": "💸", "RED": "👍"}.get(col)
                    elif p2["y"] < p1["y"]:
                        emoji = {"GOLD": "🤩", "GREEN": "🙂",
                                "ORANGE": "😟", "RED": "😱"}.get(col)
                    if emoji:
                        all_emojis.append({"x": mid_x, "y": mid_y, "Emoji": emoji})

            if all_emojis:
                df_emojis = pd.DataFrame(all_emojis)
                chart += alt.Chart(df_emojis).mark_text(fontSize=30, dy=-30).encode(x="x:Q", y="y:Q", text="Emoji:N")

            # modalità di visualizzazione
            mode = st.radio(
                "Visualizzazione grafico",
                ["Compatto con scroll", "Tutte le giornate compresse", "Schermo intero automatico"],
                index=0
            )

            if mode == "Compatto con scroll":
                chart_scroll = chart.properties(width=3000, height=340)
                st.markdown("<div style='overflow-x:auto; border:2px solid #444; border-radius:10px; padding:6px;'>",
                            unsafe_allow_html=True)
                st.altair_chart(chart_scroll, use_container_width=False)
                st.markdown("</div>", unsafe_allow_html=True)
            elif mode == "Tutte le giornate compresse":
                st.altair_chart(chart.properties(height=340), use_container_width=True)
            else:
                st.altair_chart(chart.properties(height=400), use_container_width=True)

            st.caption("💡 Suggerimento: su smartphone la modalità 'Compatto con scroll' è più leggibile.")
    except Exception:
        pass

    # ===== TABELLA MOVIMENTI =====
    if not df_mov.empty:
        giornata_corrente = df_mov["Giornata"].iloc[-1]
        cassa_attuale = df_mov["Cassa dopo €"].iloc[-1]
        st.markdown(f"<h4 style='color:gold'>💰 Cassa attuale {giornata_corrente}: "
                    f"<span style='font-size:1.5em;'>{cassa_attuale}</span></h4>", unsafe_allow_html=True)
        st.markdown("#### 📒 Movimenti cassa")
        st.dataframe(df_mov, hide_index=True, use_container_width=True)
    else:
        st.markdown(f"<h4 style='color:gold'>💰 Cassa attuale G1: "
                    f"<span style='font-size:1.5em;'>{eur(CASSA_START)}</span></h4>", unsafe_allow_html=True)
        st.markdown("#### 📒 Movimenti cassa")
        st.caption("Nessun movimento ancora registrato.")

    st.markdown("</div>", unsafe_allow_html=True)



# -------------------- Percorsi file di salvataggio --------------------

# Tutti i file vengono ora salvati e caricati nella sottocartella "data"
DATA_DIR = "data"

# Se la cartella non esiste, la crea automaticamente
os.makedirs(DATA_DIR, exist_ok=True)

# Percorsi completi dei file di salvataggio
SAVE_FILE = os.path.join(DATA_DIR, "dati_giornate.pkl")
CASHOUTS_FILE = os.path.join(DATA_DIR, "cashouts.pkl")
RICARICHE_FILE = os.path.join(DATA_DIR, "ricariche.pkl")
WINS_FILE = os.path.join(DATA_DIR, "manual_wins.pkl")
LOSSES_FILE = os.path.join(DATA_DIR, "manual_losses.pkl")
CHAMP_FILE = os.path.join(DATA_DIR, "champions.pkl")
STAKE_FILE = os.path.join(DATA_DIR, "stake.pkl")

def save_all():
    """Salva tutti i dati amministratore su file pickle (nella cartella data/)."""
    try:
        # Data principale
        st.session_state.data.to_pickle(SAVE_FILE)

        # Cashout e ricariche
        with open(CASHOUTS_FILE, "wb") as f:
            pickle.dump(st.session_state.get("cashouts", {}), f)
        with open(RICARICHE_FILE, "wb") as f:
            pickle.dump(st.session_state.get("ricariche", {}), f)

        # Vincite e perdite manuali
        with open(WINS_FILE, "wb") as f:
            pickle.dump(st.session_state.get("manual_wins", {}), f)
        with open(LOSSES_FILE, "wb") as f:
            pickle.dump(st.session_state.get("manual_losses", {}), f)

        # Champions Days
        with open(CHAMP_FILE, "wb") as f:
            pickle.dump(st.session_state.get("champions_days", []), f)

        # Stake
        with open(STAKE_FILE, "wb") as f:
            pickle.dump(st.session_state.get("stake_value", 10), f)

    except Exception as e:
        st.error(f"Errore salvataggio dati: {e}")

def load_all():
    """Carica tutti i dati se esistono i file pickle (dalla cartella data/)."""
    try:
        if os.path.exists(SAVE_FILE):
            st.session_state.data = pd.read_pickle(SAVE_FILE)

        if os.path.exists(CASHOUTS_FILE):
            with open(CASHOUTS_FILE, "rb") as f:
                st.session_state["cashouts"] = pickle.load(f)
        if os.path.exists(RICARICHE_FILE):
            with open(RICARICHE_FILE, "rb") as f:
                st.session_state["ricariche"] = pickle.load(f)

        if os.path.exists(WINS_FILE):
            with open(WINS_FILE, "rb") as f:
                st.session_state["manual_wins"] = pickle.load(f)
        if os.path.exists(LOSSES_FILE):
            with open(LOSSES_FILE, "rb") as f:
                st.session_state["manual_losses"] = pickle.load(f)

        if os.path.exists(CHAMP_FILE):
            with open(CHAMP_FILE, "rb") as f:
                st.session_state["champions_days"] = pickle.load(f)

        if os.path.exists(STAKE_FILE):
            with open(STAKE_FILE, "rb") as f:
                st.session_state["stake_value"] = pickle.load(f)

    except Exception as e:
        st.error(f"Errore caricamento dati: {e}")


                    # Effetti (facoltativi)
celebration_box = st.empty()  # contenitore unico per tutte le celebrazioni
try:
    from streamlit_extras.let_it_rain import rain
    celebration_box = st.empty()
    HAS_RAIN = True
except ImportError:
    HAS_RAIN = False
    def rain(*args, **kwargs):  # safe stub se la libreria manca
        pass



        # -------------------- COSTANTI --------------------

TITLE = "🐔💰 KillBet League 2025-2026 💰🦊"
PLAYERS = ["ANGEL","GARIBALDI","CHRIS","MG78IT","FILLIP"]
NUM_GIORNATE = 40
# Stake di default
STAKE_DEFAULT = 10.0  # schedina totale a giornata (default)
# Stake persistente in sessione
if "stake_value" not in st.session_state:
    st.session_state["stake_value"] = STAKE_DEFAULT
# Valore corrente (persistito nella sessione Streamlit)
if "stake_value" not in st.session_state:
    st.session_state["stake_value"] = STAKE_DEFAULT
# Variabile globale usata da tutti i calcoli
STAKE = float(st.session_state["stake_value"])
CASSA_START = 46.83      # cassa iniziale
ADMIN_PIN = "ET2856"

# Colori nomi
NAME_COLORS = {
    "ANGEL":     ("#0B5ED7", None),
    "MG78IT":    ("#FFFFFF", "#2B2B2B"),
    "GARIBALDI": ("#FF00FF", None),
    "CHRIS":     ("#19a319", None),
    "FILLIP":    ("#00BFFF", None),
}
GOLD   = "#d4af37"
ORANGE = "#ff8c00"
BROWN  = "#8B4513"
SILVER = "#C0C0C0"
GREEN  = "#16c60c"


            # -------------------- UTIL --------------------
            
def esito_colored(ch):
    if ch=="V": return "<span class='good'>V</span>"
    if ch=="P": return "<span class='bad'>P</span>"
    return ""

def color_span(name_text):
    if name_text is None: return ""
    name = str(name_text).strip()
    if name in NAME_COLORS:
        fg, bg = NAME_COLORS[name]
        style = f"color:{fg}; font-weight:800;"
        if bg: style += f" background:{bg}; padding:1px 4px; border-radius:6px;"
        return f"<span style='{style}'>{name}</span>"
    return f"<span style='font-weight:800'>{name}</span>"

def eur(x: float) -> str:
    try:
        s = f"{float(x):,.2f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "0,00"

def fmt1(x: float) -> str:
    """
    Interi senza decimali (es. 3), non-interi con 2 decimali (es. 2,50).
    Usa la virgola come separatore decimale.
    """
    try:
        v = float(x)
        if v.is_integer():
            # Niente decimali se il valore è intero
            return str(int(v))
        # Due decimali se non intero
        return f"{v:.2f}".replace(".", ",")
    except Exception:
        return ""


def paint_names_only(df_in, col="GIOCATORE"):
    def cell(v):
        key = str(v).replace(" 👑","")
        if key in NAME_COLORS:
            fg,_=NAME_COLORS[key]; return f"color:{fg}; font-weight:800; text-align:center;"
        return "text-align:center;"
    return df_in.style.applymap(cell, subset=[col]).set_properties(**{"text-align":"center"})

def _try_float(x):
    try:
        if x in (None, ""): return None
        return float(str(x).replace(",", "."))
    except:
        return None

        # -------------------- CALENDARIO --------------------
        
def generate_schedule(players, rounds):
    teams = players[:]
    if len(teams) % 2 == 1:
        teams.append("BYE")
    n = len(teams); half = n//2; rounds_single = n-1
    order = teams[:]; single = []
    for _ in range(rounds_single):
        left = order[:half]; right = list(reversed(order[half:]))
        pairs = []
        for a,b in zip(left,right):
            if "BYE" in (a,b):
                rip = a if b=="BYE" else b
                pairs.append(("RIP", rip))
            else:
                pairs.append((a,b))
        single.append(pairs)
        order = [order[0]] + [order[-1]] + order[1:-1]
    out=[]; cyc=cycle(single)
    for _ in range(rounds):
        out.append(next(cyc))
    return out

def giornata_map(pairs):
    matches = [(a,b) for a,b in pairs if a!="RIP"]
    rips    = [b    for a,b in pairs if a=="RIP"]
    rip = rips[0] if rips else None
    (c1,o1),(c2,o2) = matches
    return {"CASA1":c1,"OSP1":o1,"CASA2":c2,"OSP2":o2,"RIP":rip}

FIXTURES = [giornata_map(p) for p in generate_schedule(PLAYERS, NUM_GIORNATE)]

            # -------------------- STATE --------------------
            
def init_state():
    if "champions_days" not in st.session_state:
        st.session_state["champions_days"] = []
    if "data" not in st.session_state:
        rows = []
        for g, f in enumerate(FIXTURES, start=1):
            for slot, key in [
                ("CASA1", "CASA1"),
                ("OSP1", "OSP1"),
                ("CASA2", "CASA2"),
                ("OSP2", "OSP2"),
                ("RIP", "RIP"),
            ]:
                rows.append({
                    "giornata": g,
                    "slot": slot,
                    "giocatore": f[key],
                    "esito": None,
                    "quota": None,
                    "fantasmino": False,
                })
        st.session_state.data = pd.DataFrame(rows)

    # Impostazioni di sessione standard
    st.session_state.setdefault("admin_pin_ok", False)
    st.session_state.setdefault("ricariche_text", "")
    st.session_state.setdefault("cashouts", {})    # {giornata_int: importo_float}
    st.session_state.setdefault("ricariche", {})

    # Se ci sono file salvati, ricaricali
    load_all()


                # ===== BOOTSTRAP SLIDER/STATO GIORNATA =====
try:
    df0 = st.session_state.data
    # Individua l’ultima giornata COMPLETATA (tutte le righe con 'esito' non NaN)
    ultima_completata = 1
    for g in sorted(df0["giornata"].unique()):
        if not df0[df0["giornata"] == g]["esito"].isna().any():
            ultima_completata = int(g)
except Exception:
    ultima_completata = 1

# ===== SINCRONIZZAZIONE STATO =====
# Se non esiste, crea il riferimento principale
if "fino_a" not in st.session_state:
    st.session_state["fino_a"] = ultima_completata

# Se lo slider non esiste, allinealo
if "slider_fino_a" not in st.session_state:
    st.session_state["slider_fino_a"] = st.session_state["fino_a"]

# Se è apparsa una giornata nuova, aggiorna automaticamente
if ultima_completata > st.session_state["fino_a"]:
    st.session_state["fino_a"] = ultima_completata
    st.session_state["slider_fino_a"] = ultima_completata

# Crea alias di comodo usato nel resto del codice
fino_a = int(st.session_state["fino_a"])



# -------------------- PUNTEGGI BASE (storici) --------------------
def base_points(eh, ea):
    if eh is None or ea is None: return 0,0
    if eh=="V" and ea=="P": return 3,0
    if eh=="P" and ea=="V": return 0,3
    if eh=="V" and ea=="V": return 2,2
    if eh=="P" and ea=="P": return 1,1
    return 0,0

def bonus_points(eh, ea, qh, qa, diff_thr=0.5):
    bH = bA = 0.0; side = ""
    try:
        qh = _try_float(qh)
        qa = _try_float(qa)
    except:
        return bH, bA, side
    if (qh is None) or (qa is None): return bH, bA, side

    if eh == "V" and ea == "V":
        if abs(qh - qa) >= diff_thr:
            if qh > qa: bH = 0.5; side="H"
            elif qa > qh: bA = 0.5; side="A"
        return bH,bA,side
    if eh == "V" and ea == "P":
        if (qh - qa) >= diff_thr: bH=0.5; side="H"
        return bH,bA,side
    if eh == "P" and ea == "V":
        if (qa - qh) >= diff_thr: bA=0.5; side="A"
        return bH,bA,side
    return bH,bA,side

def malus_points(eh, ea, qh, qa, diff_thr=0.5):
    mH=mA=0.0; side=""
    try:
        qh = _try_float(qh)
        qa = _try_float(qa)
    except:
        return mH,mA,side
    if eh=="P" and ea=="P" and (qh is not None) and (qa is not None):
        if abs(qh - qa) >= diff_thr:
            if qh < qa: mH=-0.5; side="H"
            elif qa < qh: mA=-0.5; side="A"
    return mH,mA,side

# -------------------- EXTRA VOLPE/POLLO (NUOVE REGOLE) --------------------
def _eq(a,b,eps=1e-9): return abs(a-b) < eps

def classify_rank(q_vals, q):
    qmin, qmax = min(q_vals), max(q_vals)
    if _eq(q, qmax):
        ties = sum(1 for v in q_vals if _eq(v, qmax))
        return "max" if ties==1 else "max_tie"
    if _eq(q, qmin):
        ties = sum(1 for v in q_vals if _eq(v, qmin))
        return "min" if ties==1 else "min_tie"
    return "mid"

def compute_volpe_extra_new(quotes_map, volpe_name):
    """
    Bonus Volpe basato su POSIZIONE (giornata):
    Ordina quote DESC (più alta -> più bassa) e assegna:
        1 -> +6, 2 -> +5, 3 -> +4, 4 -> +3, 5 -> +2
    Parità: tutti i pari prendono la POSIZIONE MIGLIORE del gruppo (bonus più alto).
    Ritorna: (punti_float, spiegazione_str)
    """
    if not quotes_map or volpe_name not in quotes_map:
        return 0.0, ""

    # normalizza e scarta None/NaN
    norm = {}
    for p, q in quotes_map.items():
        qf = _try_float(q)
        if qf is not None:
            norm[str(p)] = float(qf)
    if not norm or volpe_name not in norm:
        return 0.0, ""

    # ordina DESC (più alta -> più bassa)
    items = sorted(norm.items(), key=lambda kv: (-kv[1], kv[0]))
    players = [p for p, _ in items]
    quotas  = [q for _, q in items]

    # assegna POSIZIONI con "best rank" per i pari (pos minima del gruppo)
    pos_map = {}
    i = 0
    n = len(players)
    pos = 1
    while i < n:
        j = i + 1
        while j < n and abs(quotas[j] - quotas[i]) < 1e-9:
            j += 1
        for k in range(i, j):
            pos_map[players[k]] = pos
        pos += (j - i)
        i = j

    # mappa posizione -> bonus
    bonus_by_pos = {1: +6.0, 2: +5.0, 3: +4.0, 4: +3.0, 5: +2.0}
    ppos = int(pos_map.get(volpe_name, 5))
    pts = float(bonus_by_pos.get(ppos, +2.0))

    # descrizione leggibile
    label = {
        1: "1ª quota più alta",
        2: "2ª quota più alta",
        3: "quota intermedia",
        4: "2ª quota più bassa",
        5: "quota più bassa",
    }.get(ppos, "")

    return pts, label

def compute_pollo_extra_new(quotes_map, pollo_name):
    """
    Malus Pollo basato su POSIZIONE (giornata):
    Ordina quote ASC (più bassa -> più alta) e assegna:
        1 -> −6, 2 -> −5, 3 -> −4, 4 -> −3, 5 -> −2
    Parità: tutti i pari prendono la POSIZIONE PIÙ FAVOREVOLE (malus più leggero).
    """
    if not quotes_map or pollo_name not in quotes_map:
        return 0.0, ""

    norm = {}
    for p, q in quotes_map.items():
        qf = _try_float(q)
        if qf is not None:
            norm[str(p)] = float(qf)
    if not norm or pollo_name not in norm:
        return 0.0, ""

    # ordina ASC (più bassa -> più alta)
    items = sorted(norm.items(), key=lambda kv: (kv[1], kv[0]))
    players = [p for p, _ in items]
    quotas  = [q for _, q in items]

    pos_map = {}
    i = 0
    n = len(players)
    pos = 1
    while i < n:
        j = i + 1
        while j < n and abs(quotas[j] - quotas[i]) < 1e-9:
            j += 1
        # ⬇️ Cambiamento qui: assegniamo la POSIZIONE MASSIMA del gruppo
        for k in range(i, j):
            pos_map[players[k]] = pos + (j - i) - 1
        pos += (j - i)
        i = j

    malus_by_pos = {1: -6.0, 2: -5.0, 3: -4.0, 4: -3.0, 5: -2.0}
    ppos = int(pos_map.get(pollo_name, 5))
    pts = float(malus_by_pos.get(ppos, -2.0))

    label = {
        1: "quota più bassa",
        2: "2ª quota più bassa",
        3: "quota intermedia",
        4: "2ª quota più alta",
        5: "quota più alta",
    }.get(ppos, "")

    return pts, label

def compute_courage_rank(quotes_map, winners_set, rank_points=None, threshold=1.50):
    """
    Rank-based Bonus Coraggio (definitivo).
    - quotes_map: dict player -> quota (float)
    - winners_set: set(player) che hanno esito "V" (solo loro possono ricevere bonus)
    - rank_points: dict posizione->punti (pos 1..5)
    - threshold: se quota <= threshold -> pts = 0 (anche se vincente)
    Ritorna: dict player -> (pts_float, title_str_or_None)
    """
    import math
    out = {}
    if rank_points is None:
        rank_points = {1:1.10, 2:0.80, 3:0.50, 4:0.30, 5:0.10}

    # normalizza quote in float (filtra None/NaN)
    norm = {}
    for p, q in (quotes_map or {}).items():
        try:
            if q is None or q == "" or (isinstance(q, float) and pd.isna(q)):
                continue
            qf = _try_float(q) if not isinstance(q, (int, float)) else float(q)
            if qf is None: continue
            norm[p] = float(qf)
        except Exception:
            continue

    if not norm:
        return out

    # ordina desc (quota maggiore => posizione 1)
    items = sorted(norm.items(), key=lambda kv: kv[1], reverse=True)
    players = [it[0] for it in items]
    quotas = [it[1] for it in items]

    # assegna posizioni gestendo tie: players con stessa quota ricevono la stessa posizione (min pos)
    positions = {}
    pos = 1
    i = 0
    n = len(players)
    while i < n:
        j = i + 1
        while j < n and abs(quotas[j] - quotas[i]) < 1e-9:
            j += 1
        for k in range(i, j):
            positions[players[k]] = pos
        pos += (j - i)
        i = j

    title_map = {
        1: ("Temerario 💥", rank_points.get(1, 0.0)),
        2: ("Audace 🔥",     rank_points.get(2, 0.0)),
        3: ("Prudente 🧐",   rank_points.get(3, 0.0)),
        4: ("Braccino corto ✋", rank_points.get(4, 0.0)),
        5: ("Fifone 🐇",     rank_points.get(5, 0.0)),
    }

    for pl in players:
        qv = norm.get(pl, 0.0)
        ppos = positions.get(pl, None)
        if ppos is None:
            out[pl] = (0.0, None)
            continue
        title, base_pts = title_map.get(ppos, ("Fifone 🐇", 0.0))

        # soglia minima: se sotto soglia => pts 0 (mostriamo Fifone)
        if qv <= threshold:
            pts = 0.0
            title = "Fifone 🐇"
        else:
            # assegna i punti di posizione base
            pts = float(base_pts)
        # applica solo ai vincenti; ai non vincenti assegniamo (0.0, None)
        if pl in (winners_set or set()):
            out[pl] = (round(pts, 2), title)
        else:
            out[pl] = (0.0, None)

    return out

# ==================== NUOVE REGOLE 1v1 (integrazione) ====================

USE_SFIDA_RULES = True
LOW_ODDS_THRESHOLD = 1.50

def _fascia_bonus(diff: float) -> float:
    if diff >= 4.0: return 4.0
    if diff >= 3.0: return 3.0
    if diff >= 2.0: return 2.0
    if diff >= 1.0: return 1.0
    if diff >= 0.5: return 0.5
    return 0.0

def _fmt_signed(v):
    s = f"{v:.1f}".replace(".", ",")
    return ("+" + s) if v > 0 else s


# -------------------- CALCOLI --------------------

# --- Wrapper Fantasmino: se c'è il fantasma in una delle due posizioni,
#     applica le regole speciali e NON considera differenze/dimezzi. ---
def compute_points_pair(eh, ea, qh, qa):
    """
    Regole 1v1 aggiornate (Struttura B):

    - V–P / P–V:
        • Vincente prende 3 punti.
        • Se la sua quota ≤ 1,60 → penalità −1,5 (totale 1,5).
        • Bonus differenza quote al vincente solo se ha la quota più alta (Δq >= 0.5 → +0.5, >=1 → +1, >=2 → +2, >=3 → +3, >=4 → +4).
        • Malus differenza quote al perdente solo se ha la quota più bassa.

    - V–V:
        • Base 2–2.
        • Penalità −1 a ciascun vincente con quota ≤ 1,60 (indipendente).
        • Bonus differenza quote al giocatore con quota più alta se Δq >= 0.5.

    - P–P:
        • Base 1–1.
        • Penalità −0.5 a ciascun perdente con quota ≤ 1,60 (indipendente).
        • Malus ulteriore: se diff >1.5 → −1 al più alto; se diff >=3 → −2.

    Restituisce 10 valori:
    baseH, baseA, bH, bA, mH, mA, halfH, halfA, indic_casa, indic_osp
    """

    qh_f = _try_float(qh)
    qa_f = _try_float(qa)
    indic_casa = ""
    indic_osp = ""

    baseH = baseA = 0.0
    bH = bA = 0.0
    mH = mA = 0.0
    halfH = halfA = 0.0

    if USE_SFIDA_RULES and (eh in ("V", "P")) and (ea in ("V", "P")) and (qh_f is not None) and (qa_f is not None):

        # --- V–V ---
        if eh == "V" and ea == "V":
            baseH = baseA = 2.0

            # Penalità quote basse (fasce distinte)
            if qh_f < 1.40:
                halfH -= 1.5
                indic_casa += f" ⚠️ quota <1.40 −1.5"
            elif 1.40 <= qh_f <= 1.60:
                halfH -= 1.0
                indic_casa += f" ⚠️ quota 1.40–1.60 −1.0"

            if qa_f < 1.40:
                halfA -= 1.5
                indic_osp += f" ⚠️ quota <1.40 −1.5"
            elif 1.40 <= qa_f <= 1.60:
                halfA -= 1.0
                indic_osp += f" ⚠️ quota 1.40–1.60 −1.0"

            # Bonus differenza quote (proporzionale, max ±3)
            diff = round(abs(qh_f - qa_f), 2)
            extra = min(diff, 3.0)
            if qh_f > qa_f:
                bH += extra
                indic_casa += f" ⚖️👍 diff quote {diff:.2f} +{fmt1(extra)}"
            elif qa_f > qh_f:
                bA += extra
                indic_osp += f" ⚖️👍 diff quote {diff:.2f} +{fmt1(extra)}"

            return baseH, baseA, bH, bA, mH, mA, halfH, halfA, indic_casa.strip(), indic_osp.strip()

        # --- V–P ---
        if eh == "V" and ea == "P":
            baseH, baseA = 3.0, 0.0

            # Penalità quote basse per il vincente (fasce distinte)
            if qh_f < 1.40:
                halfH -= 2.0
                indic_casa += f" ⚠️ quota <1.40 −2.0"
            elif 1.40 <= qh_f <= 1.60:
                halfH -= 1.5
                indic_casa += f" ⚠️ quota 1.40–1.60 −1.5"

            # Bonus differenza quote
            diff = round(abs(qh_f - qa_f), 2)
            # Bonus differenza quote (proporzionale, max ±3)
            diff = round(abs(qh_f - qa_f), 2)
            extra = min(diff, 3.0)
            if qh_f > qa_f:
                bH += extra
                indic_casa += f" ⚖️👍diff quote {diff:.2f} +{fmt1(extra)}"
            if qa_f < qh_f:
                mA -= extra
                indic_osp += f" ⚖️👍 diff quote {diff:.2f} −{fmt1(extra)}"


            return baseH, baseA, bH, bA, mH, mA, halfH, halfA, indic_casa.strip(), indic_osp.strip()

        # --- P–V ---
        if eh == "P" and ea == "V":
            baseH, baseA = 0.0, 3.0

            # Penalità quote basse per il vincente (fasce distinte)
            if qa_f < 1.40:
                halfA -= 2.0
                indic_osp += f" ⚠️ quota <1.40 −2.0"
            elif 1.40 <= qa_f <= 1.60:
                halfA -= 1.5
                indic_osp += f" ⚠️ quota 1.40–1.60 −1.5"

            # Bonus differenza quote
            diff = round(abs(qh_f - qa_f), 2)
            # Bonus differenza quote (proporzionale, max ±3)
            diff = round(abs(qh_f - qa_f), 2)
            extra = min(diff, 3.0)
            if qa_f > qh_f:
                bA += extra
                indic_osp += f" ⚖️👍 diff quote {diff:.2f} +{fmt1(extra)}"
            if qh_f < qa_f:
                mH -= extra
                indic_casa += f" ⚖️👍 diff quote {diff:.2f} −{fmt1(extra)}"

            return baseH, baseA, bH, bA, mH, mA, halfH, halfA, indic_casa.strip(), indic_osp.strip()

        # --- P–P ---
        if eh == "P" and ea == "P":
            baseH = baseA = 1.0

            # Penalità quote basse (fasce distinte)
            if qh_f < 1.40:
                halfH -= 1.0
                indic_casa += f" ⚠️ quota <1.40 −1.0"
            elif 1.40 <= qh_f <= 1.60:
                halfH -= 0.5
                indic_casa += f" ⚠️ quota 1.40–1.60 −0.5"

            if qa_f < 1.40:
                halfA -= 1.0
                indic_osp += f" ⚠️ quota <1.40 −1.0"
            elif 1.40 <= qa_f <= 1.60:
                halfA -= 0.5
                indic_osp += f" ⚠️ quota 1.40–1.60 −0.5"

            # Malus differenza quote (resta invariato)
            # Malus differenza quote proporzionale (max −3)
            diff = round(abs(qh_f - qa_f), 2)
            malus_delta = min(diff, 3.0)  # fino a −3 massimo
            if qh_f > qa_f:
                mH -= malus_delta
                indic_casa += f" ⚖️👎 Δquote {diff:.2f} −{fmt1(malus_delta)}"
            elif qa_f > qh_f:
                mA -= malus_delta
                indic_osp += f" ⚖️👎 Δquote {diff:.2f} −{fmt1(malus_delta)}"

            return baseH, baseA, bH, bA, mH, mA, halfH, halfA, indic_casa.strip(), indic_osp.strip()

    return baseH, baseA, bH, bA, mH, mA, halfH, halfA, indic_casa.strip(), indic_osp.strip()


    # ritorno neutro se non ha fatto return prima
    return baseH, baseA, bH, bA, mH, mA, halfH, halfA, indic_casa.strip(), indic_osp.strip()

import math

def _rank_desc(values):
    """Assegna rank (1=quota più alta, 5=quota più bassa) con gestione parità."""
    enumerated = list(enumerate(values))
    enumerated.sort(key=lambda x: (-x[1], x[0]))
    ranks = [0.0]*len(values)
    i = 0
    while i < len(enumerated):
        j = i
        while j+1 < len(enumerated) and math.isclose(enumerated[j+1][1], enumerated[i][1], rel_tol=1e-9, abs_tol=1e-9):
            j += 1
        avg_rank = (i+1 + j+1) / 2.0
        for k in range(i, j+1):
            idx = enumerated[k][0]
            ranks[idx] = avg_rank
        i = j+1
    return ranks

def bonus_tutti_vincenti(players, quotes):
    """
    Assegna punti INTERI (5,4,3,2,1) e una descrizione posizione
    quando TUTTI sono vincenti (5V). Gestisce i pareggi:
    a parità di quota, TUTTI i pari prendono la posizione migliore occupata dal gruppo.
    Ritorna: { player: (points_int, descrizione) }
    """
    POS = {
        1: (5, "Quota più alta"),
        2: (4, "Seconda quota più alta"),
        3: (3, "Quota intermedia"),
        4: (2, "Seconda quota più bassa"),
        5: (1, "Quota più bassa"),
    }

    def _qf(x):
        if x in (None, ""): return None
        try:
            return float(str(x).replace(",", "."))
        except Exception:
            return None

    pairs = [(p, _qf(q)) for p, q in zip(players, quotes)]
    pairs_sorted = sorted(pairs, key=lambda t: (-1e18 if t[1] is None else -t[1], t[0]))

    out = {}
    pos = 1
    i = 0
    n = len(pairs_sorted)
    while i < n and pos <= 5:
        q_i = pairs_sorted[i][1]
        j = i
        while j < n and pairs_sorted[j][1] == q_i:
            j += 1
        pts, why = POS.get(pos, (0, ""))
        for k in range(i, j):
            player_k = pairs_sorted[k][0]
            out[player_k] = (pts, why)
        pos += (j - i)
        i = j

    for p, q in pairs_sorted:
        if p not in out:
            out[p] = (0, "")

    return out


def malus_tutti_perdenti(players, quotes):
    """
    Assegna malus INTERI (−5..−1) e una descrizione posizione
    quando TUTTI sono perdenti (5P). Gestisce i pareggi:
    a parità di quota, TUTTI i pari prendono la posizione migliore occupata dal gruppo.
    Ritorna: { player: (malus_int, descrizione) }
    """
    POS = {
        1: (-1, "Quota più alta"),
        2: (-2, "Seconda quota più alta"),
        3: (-3, "Quota intermedia"),
        4: (-4, "Seconda quota più bassa"),
        5: (-5, "Quota più bassa"),
    }

    def _qf(x):
        if x in (None, ""): return None
        try:
            return float(str(x).replace(",", "."))
        except Exception:
            return None

    pairs = [(p, _qf(q)) for p, q in zip(players, quotes)]
    pairs_sorted = sorted(pairs, key=lambda t: (-1e18 if t[1] is None else -t[1], t[0]))

    out = {}
    pos = 1
    i = 0
    n = len(pairs_sorted)
    while i < n and pos <= 5:
        q_i = pairs_sorted[i][1]
        j = i
        while j < n and pairs_sorted[j][1] == q_i:
            j += 1
        pts, why = POS.get(pos, (0, ""))
        for k in range(i, j):
            player_k = pairs_sorted[k][0]
            out[player_k] = (pts, why)
        pos += (j - i)
        i = j

    for p, q in pairs_sorted:
        if p not in out:
            out[p] = (0, "")

    return out

def compute_points_pair_fantasmino(eh, ea, qh, qa, fh=False, fa=False):
    """
    Gestione 👻 Fantasmino:
    - Se esattamente uno è fantasmino (fh XOR fa):
          * l'avversario prende SOLO punti base: V→2, P→1 (nessun bonus/malus/penalità quote basse)
          * al fantasmino si applica il malus −5
    - Se nessuno è fantasmino, usa le regole standard (compute_points_pair)
    - Se entrambi fantasmino: entrambi 0, e ciascuno −5
    Ritorna: baseH, baseA, bH, bA, mH, mA, halfH, halfA, indic_casa, indic_osp
    """
    # Default: calcolo standard
    baseH, baseA, bH, bA, mH, mA, halfH, halfA, indic_casa, indic_osp = compute_points_pair(eh, ea, qh, qa)

    # Caso: esattamente uno è fantasmino
    if bool(fh) ^ bool(fa):
        # azzera bonus/malus/dimezzi iniziali
        bH = bA = mH = mA = halfH = halfA = 0.0

        # 👻 Casa è ghost → assegna base all'ospite (V=2, P=1)
        if fh:
            if ea == "V":
                baseA = 2.0
            elif ea == "P":
                baseA = 1.0
            else:
                baseA = 0.0

            # penalità per il giocatore reale (ospite)
            qa_f = _try_float(qa)
            if qa_f is not None:
                if qa_f < 1.40:
                    halfA -= 2.0
                    indic_osp += " 🤡 quota <1.40 −2.0"
                elif 1.40 <= qa_f <= 1.60:
                    halfA -= 1.5
                    indic_osp += " 🚽 quota ≤1.60 −1.5"

            indic_osp = (indic_osp + " 👻 vs Fantasmino: solo punti base").strip()

        # 👻 Ospite è ghost → assegna base al casa (V=2, P=1)
        elif fa:
            if eh == "V":
                baseH = 2.0
            elif eh == "P":
                baseH = 1.0
            else:
                baseH = 0.0

            # penalità per il giocatore reale (casa)
            qh_f = _try_float(qh)
            if qh_f is not None:
                if qh_f < 1.40:
                    halfH -= 2.0
                    indic_casa += " 🤡 quota <1.40 −2.0"
                elif 1.40 <= qh_f <= 1.60:
                    halfH -= 1.5
                    indic_casa += " 🚽 quota ≤1.60 −1.5"

            indic_casa = (indic_casa + " 👻 vs Fantasmino: solo punti base").strip()

    # Malus Fantasmino: NON va in mH/mA, ma solo come descrizione
    if fh:
        indic_casa = (indic_casa + " 👻 Fantasmino −5").strip()
    if fa:
        indic_osp = (indic_osp + " 👻 Fantasmino −5").strip()

    return baseH, baseA, bH, bA, mH, mA, halfH, halfA, indic_casa, indic_osp

def compute_all(df, fino_a=None, ricariche=None, cashouts=None):

    if fino_a is not None:
        # includo anche stake e movimenti frazionari della stessa giornata
        df = df[df["giornata"] <= int(fino_a) + 0.5].copy()
    if ricariche is None:  ricariche = {}
    if cashouts  is None:  cashouts  = {}
    base={p:0.0 for p in PLAYERS}
    bonus_diff={p:0.0 for p in PLAYERS}
    malus_diff={p:0.0 for p in PLAYERS}
    half_adj={p:0.0 for p in PLAYERS}
    volpe_extra={p:0.0 for p in PLAYERS}
    pollo_extra={p:0.0 for p in PLAYERS}
    champions_bonus={p:0.0 for p in PLAYERS}
    courage_bonus = {p:0.0 for p in PLAYERS}   # Bonus Coraggio cumulato (definitivo)
    
    # Safety: se il DF non ha ancora la colonna 'fantasmino', la creo a False
    if "fantasmino" not in df.columns:
        df = df.copy()
        df["fantasmino"] = False

    # per grafico Killbet Arena (progressione per giornata)
    per_day_points = {p:[] for p in PLAYERS}
    per_day_totals = {p:0.0 for p in PLAYERS}
    
    # Malus Fantasmino per classifica
    ghost_penalty = {p: 0.0 for p in PLAYERS}

    W={p:0 for p in PLAYERS}; D={p:0 for p in PLAYERS}; L={p:0 for p in PLAYERS}
    PG={p:0 for p in PLAYERS}
    tab=[]; fil_deltas={p:[] for p in PLAYERS}
    giornata_flag={}; pollo_name={}; volpe_name={}
    giorno_player_extra = {}

    max_g = int(df["giornata"].max() or 0)
    for g in range(1, max_g+1):
        dfg = df[df["giornata"]==g].set_index("slot")
        if dfg.empty: break
        c1,o1 = dfg.loc["CASA1"], dfg.loc["OSP1"]
        c2,o2 = dfg.loc["CASA2"], dfg.loc["OSP2"]
        rip   = dfg.loc["RIP"]

        # -------- Partita 1
        baseH,baseA,bH,bA,mH,mA,halfH,halfA,indic_casa,indic_osp = compute_points_pair_fantasmino(
            c1["esito"], o1["esito"], c1["quota"], o1["quota"],
            fh=bool(c1.get("fantasmino", False)), fa=bool(o1.get("fantasmino", False))
        )

        base[c1["giocatore"]]      += baseH
        base[o1["giocatore"]]      += baseA
        bonus_diff[c1["giocatore"]] += bH
        bonus_diff[o1["giocatore"]] += bA
        malus_diff[c1["giocatore"]] += mH
        malus_diff[o1["giocatore"]] += mA
        half_adj[c1["giocatore"]]   += halfH
        half_adj[o1["giocatore"]]   += halfA

        if c1["esito"] in ("V","P") and o1["esito"] in ("V","P"):
            PG[c1["giocatore"]]+=1; PG[o1["giocatore"]]+=1
            sH=(baseH+bH+mH+halfH); sA=(baseA+bA+mA+halfA)
            if sH>sA: W[c1["giocatore"]]+=1; L[o1["giocatore"]]+=1
            elif sA>sH: W[o1["giocatore"]]+=1; L[c1["giocatore"]]+=1
            else: D[c1["giocatore"]]+=1; D[o1["giocatore"]]+=1

        tab.append({
            "giornata":g,"partita":"1",
            "CASA":c1["giocatore"],"Q_CASA":c1["quota"],"OSPITE":o1["giocatore"],"Q_OSP":o1["quota"],
            "E_CASA":c1["esito"],"E_OSP":o1["esito"],
            "BONUS":"", "MALUS":"",
            "INDIC_CASA":indic_casa,"INDIC_OSP":indic_osp,
            "BASE_CASA":baseH,"BASE_OSP":baseA,
            "B_CASA":bH,"B_OSP":bA,"M_CASA":mH,"M_OSP":mA,
            "HALF_CASA":halfH,"HALF_OSP":halfA,
            "P_CASA":(baseH+bH+mH+halfH),"P_OSP":(baseA+bA+mA+halfA),
            "F_CASA": bool(c1.get("fantasmino", False)),
            "F_OSP":  bool(o1.get("fantasmino", False))
        })

        # -------- Partita 2
        baseH,baseA,bH,bA,mH,mA,halfH,halfA,indic_casa,indic_osp = compute_points_pair_fantasmino(
            c2["esito"], o2["esito"], c2["quota"], o2["quota"],
            fh=bool(c2.get("fantasmino", False)), fa=bool(o2.get("fantasmino", False))
        )

        base[c2["giocatore"]]      += baseH
        base[o2["giocatore"]]      += baseA
        bonus_diff[c2["giocatore"]] += bH
        bonus_diff[o2["giocatore"]] += bA
        malus_diff[c2["giocatore"]] += mH
        malus_diff[o2["giocatore"]] += mA
        half_adj[c2["giocatore"]]   += halfH
        half_adj[o2["giocatore"]]   += halfA

        if c2["esito"] in ("V","P") and o2["esito"] in ("V","P"):
            PG[c2["giocatore"]]+=1; PG[o2["giocatore"]]+=1
            sH=(baseH+bH+mH+halfH); sA=(baseA+bA+mA+halfA)
            if sH>sA: W[c2["giocatore"]]+=1; L[o2["giocatore"]]+=1
            elif sA>sH: W[o2["giocatore"]]+=1; L[c2["giocatore"]]+=1
            else: D[c2["giocatore"]]+=1; D[o2["giocatore"]]+=1

        tab.append({
            "giornata":g,"partita":"2",
            "CASA":c2["giocatore"],"Q_CASA":c2["quota"],"OSPITE":o2["giocatore"],"Q_OSP":o2["quota"],
            "E_CASA":c2["esito"],"E_OSP":o2["esito"],
            "BONUS":"","MALUS":"",
            "INDIC_CASA":indic_casa,"INDIC_OSP":indic_osp,
            "BASE_CASA":baseH,"BASE_OSP":baseA,
            "B_CASA":bH,"B_OSP":bA,"M_CASA":mH,"M_OSP":mA,
            "HALF_CASA":halfH,"HALF_OSP":halfA,
            "P_CASA":(baseH+bH+mH+halfH),"P_OSP":(baseA+bA+mA+halfA),
            "F_CASA": bool(c2.get("fantasmino", False)),
            "F_OSP":  bool(o2.get("fantasmino", False))
        })

        # --- Malus Fantasmino: -5 a ogni giocatore marcato 'fantasmino' in questa giornata ---
        # Recupero anche il giocatore a riposo (RIP) per applicare il malus se marcato
        try:
            rip = dfg.loc["RIP"].to_dict()
        except Exception:
            rip = {"giocatore": None, "fantasmino": False}

        for r in (c1, o1, c2, o2, rip):
            # compatibile sia con dict sia con pd.Series
            try:
                is_ghost = bool(r.get("fantasmino", False))
            except AttributeError:
                try:
                    is_ghost = bool(r["fantasmino"])
                except Exception:
                    is_ghost = False

            if is_ghost:
                # 👻 Extra visivo Fantasmino: mostra -5 ma non ricontabilizza
                try:
                    giorno_player_extra.setdefault(g, {}).setdefault(r["giocatore"], []).append(
                        ("ghost", -5.0, "Fantasmino")
                    )
                except Exception:
                    pass

            
        # RIPOSO (può avere esito e quota → includerlo per extra Volpe/Pollo)
        tab.append({
            "giornata":g,"partita":"RIP","CASA":rip["giocatore"],"Q_CASA":rip["quota"],
            "OSPITE":"","Q_OSP":None,"E_CASA":rip["esito"],"E_OSP":"",
            "BONUS":"","MALUS":"",
            "P_BASE_CASA":0.0,"P_BASE_OSP":"",
            "B_CASA":0.0,"B_OSP":"", "M_CASA":0.0,"M_OSP":"",
            "P_CASA":0.0,"P_OSP":""
        })


        # Filippoide Δ (tutti e 5 inclusi anche RIP)
        dfg2 = df[df["giornata"] == g].copy()
        for p in PLAYERS:
            r = dfg2[dfg2["giocatore"] == p]
            if r.empty:
                fil_deltas[p].append(0.0)
            else:
                es = r.iloc[0]["esito"]
                q = r.iloc[0]["quota"]
                is_ghost = bool(r.iloc[0].get("fantasmino", False))

                if is_ghost:
                    # 👻 Fantasmino → sempre delta -1
                    fil_deltas[p].append(-1.0)
                elif es == "V" and q is not None:
                    qv = _try_float(q)
                    fil_deltas[p].append((qv - 1.0) if qv is not None else 0.0)
                elif es == "P":
                    fil_deltas[p].append(-1.0)
                else:
                    fil_deltas[p].append(0.0)

        # Flag giornata base (ignora i 👻 nel controllo completezza)
        day = df[df["giornata"] == g].copy()
        is_ghost_mask = day.get("fantasmino", False).fillna(False).astype(bool)
        day_real = day.loc[~is_ghost_mask]  # solo giocatori "reali"

        if not day_real["esito"].isna().any():
            es = day_real["esito"].to_numpy()
            n_p = int((es == "P").sum())
            n_v = int((es == "V").sum())
            n_f = int(is_ghost_mask.sum())  # numero di fantasmini in giornata

            has_co = (g in (cashouts or {})) and (cashouts.get(g) is not None)

            if n_p == 1:
                loser = day_real.iloc[np.where(es == "P")[0][0]]["giocatore"]
                pollo_name[g] = loser

                if has_co:
                    # con cash out → distingui fantasma o no
                    if n_f >= 1:
                        giornata_flag[g] = "CASH_POLLO_FANTASMA"
                    else:
                        giornata_flag[g] = "CASH_POLLO"
                else:
                    # senza cash out
                    if n_f >= 1:
                        giornata_flag[g] = "POLLO_FANTASMA"  # 👻🐔
                    elif n_v == 4 and n_f == 0:
                        giornata_flag[g] = "POLLO"
                    else:
                        giornata_flag[g] = None

            elif n_v == 1 and not has_co:
                winner = day_real.iloc[np.where(es == "V")[0][0]]["giocatore"]
                giornata_flag[g] = "VOLPE"
                volpe_name[g] = winner

            elif n_v == 5 and not has_co:
                giornata_flag[g] = "ALL_WIN"

            elif n_v == 4 and n_f == 1 and not has_co:
                giornata_flag[g] = "QUASI_ALL_WIN"

            elif n_p == 5 and not has_co:
                giornata_flag[g] = "ALL_LOSE"

            elif has_co:
                # cash out senza pollo
                if n_f >= 1:
                    giornata_flag[g] = "CASH_FANTASMA"
                elif n_v == 5:
                    giornata_flag[g] = "CASH_ALL_WIN"
                else:
                    giornata_flag[g] = "CASH_OUT"

            else:
                giornata_flag[g] = None


            # Extra punti Tutti Vincenti / Tutti Perdenti
            giocatori = list(day["giocatore"])
            quote = [_try_float(q) for q in day["quota"]]
            giorno_player_extra.setdefault(g, {})

            # 🔹 BONUS anche per CASH OUT TUTTI VINCENTI
            if giornata_flag.get(g) in ("ALL_WIN", "CASH_ALL_WIN"):
                extra_map = bonus_tutti_vincenti(giocatori, quote)  # {player: (pts, descrizione)}
                for pl, (pts, why) in extra_map.items():
                    why2 = why if giornata_flag.get(g) == "ALL_WIN" else f"{why} (CASH OUT)"
                    giorno_player_extra[g].setdefault(pl, []).append(("allwin", pts, why2))

            elif giornata_flag.get(g) == "ALL_LOSE":
                extra_map = malus_tutti_perdenti(giocatori, quote)
                for pl, (pts, why) in extra_map.items():
                    giorno_player_extra[g].setdefault(pl, []).append(("alllose", pts, why))

        else:
            giornata_flag[g] = None
    
        # Extra 🦊/🐔 (NUOVE REGOLE) — includono RIP
        day2 = df[df["giornata"] == g].copy()
        is_ghost2 = day2.get("fantasmino", False).fillna(False).astype(bool)
        day2_real = day2.loc[~is_ghost2]  # escludi i 👻 dal gate e dai calcoli

        if not day2_real["esito"].isna().any():
            # quote solo per i reali (no 👻) e non-NaN
            quotes_map = {}
            for _, row in day2_real.iterrows():
                qv = _try_float(row.get("quota"))
                if qv is not None:
                    quotes_map[row["giocatore"]] = qv

            if g not in giorno_player_extra:
                giorno_player_extra[g] = {}

            # Bonus Champions (solo vincitori reali)
            champs = st.session_state.get("champions_days", [])
            if g in champs:
                for _, r in day2_real.iterrows():
                    pl = r["giocatore"]; esv = r["esito"]; qv = _try_float(r["quota"])
                    if esv == "V" and (qv is not None):
                        champions_bonus[pl] += (2.0 * qv)
                        giorno_player_extra[g].setdefault(pl, []).append(("champ", 2.0 * qv, "bonus champions"))
        
        # ---------- Bonus Coraggio (ranking globale su TUTTE le quote reali; attivo anche con CASH OUT) ----------
        
        try:
            # 🔸 Calcola il Bonus Coraggio solo se NON è una giornata Tutti Vincenti o Cash Out Tutti Vincenti
            if giornata_flag.get(g) not in ("ALL_WIN", "CASH_ALL_WIN"):

                # Costruisco il ranking su TUTTI i reali della giornata (incluso RIP), esclusi i 👻
                quotes_all: dict[str, float] = {}
                for _, r in day2.iterrows():  # day2 = tutti i 5 slot di giornata (1vs1 + RIP)
                    if bool(r.get("fantasmino", False)):
                        continue                         # 👻 escluso dal ranking
                    qf = _try_float(r.get("quota"))
                    if qf is None:
                        continue                         # salta vuoti/NaN
                    quotes_all[str(r["giocatore"])] = float(qf)

                # Set dei SOLI vincitori reali (esito = "V" e non 👻)
                winners_real = {
                    str(r["giocatore"])
                    for _, r in day2.iterrows()
                    if r.get("esito") == "V" and not bool(r.get("fantasmino", False))
                }

                # Calcolo: assegno punti SOLO ai vincenti, in base alla posizione nel ranking globale
                if quotes_all and winners_real:
                    courage_today = compute_courage_rank(
                        quotes_map=quotes_all,
                        winners_set=winners_real,
                        threshold=1.50,           # sotto o uguale a 1.50 → niente punti, ma il titolo resta descrittivo
                    )
                    for pl, (pts, title) in (courage_today or {}).items():
                        if pts and float(pts) != 0.0:
                            courage_bonus[pl] += float(pts)
                            giorno_player_extra[g].setdefault(pl, []).append(
                                ("courage", float(pts), f"Bonus Coraggio: {title}")
                            )
        except Exception as e:
            print(f"[ERRORE Bonus Coraggio G{g}]: {e}")
        
        
        
        # --- VOLPE / POLLO extra (sempre; indipendente da Champions) ---
        #    Ricostruiamo qui una quotes_map robusta sui soli REALI (RIP incluso), esclusi i 👻.
        if giornata_flag.get(g) in ("VOLPE", "POLLO", "CASH_POLLO", "POLLO_FANTASMA", "CASH_POLLO_FANTASMA"):
            quotes_map2 = {}
            for _, r in day2_real.iterrows():  # day2_real = day2 senza fantasmini
                qv = _try_float(r.get("quota"))
                if qv is not None:
                    quotes_map2[str(r["giocatore"])] = float(qv)

            # safety: contenitore extra della giornata
            giorno_player_extra.setdefault(g, {})

            flag = giornata_flag.get(g)

            # 🦊 VOLPE = unico vincente reale (no cashout)
            if flag == "VOLPE":
                w = volpe_name.get(g)
                if w and (w in quotes_map2):
                    pts, why = compute_volpe_extra_new(quotes_map2, w)
                    volpe_extra[w] += pts
                    giorno_player_extra[g].setdefault(w, []).append(("fox", pts, why))

            # 🐔 POLLO = unico perdente reale (4V/1P, no 👻, no cashout)
            elif flag == "POLLO":
                l = pollo_name.get(g)
                if l and (l in quotes_map2):
                    pts, why = compute_pollo_extra_new(quotes_map2, l)
                    pollo_extra[l] += pts
                    giorno_player_extra[g].setdefault(l, []).append(("hen", pts, why))

            # 💸🐔 CASH POLLO = unico perdente reale MA giornata con cash-out
            # Se in giornata è presente ≥1 fantasmino, il malus è alleggerito di 1 punto.
            elif flag == "CASH_POLLO":
                l = pollo_name.get(g)
                if l and (l in quotes_map2):
                    pts, why = compute_pollo_extra_new(quotes_map2, l)
                    n_ghosts = int(is_ghost2.sum())  # is_ghost2 è già definita sopra
                    if n_ghosts >= 1:
                        pts_adj = float(pts) + 1.0   # alleggerito di 1 (es. -6→-5)
                        tag = "hen_ghost"
                        desc = f"Pollo Fantasma — {why} (−1 rispetto al Pollo, CASH OUT)"
                    else:
                        pts_adj = float(pts)
                        tag = "hen"
                        desc = f"{why} (CASH OUT)"
                    pollo_extra[l] += pts_adj
                    giorno_player_extra[g].setdefault(l, []).append((tag, pts_adj, desc))

            # 👻🐔 CASH POLLO FANTASMA = unico perdente reale con cash-out e presenza di fantasmino
            elif flag == "CASH_POLLO_FANTASMA":
                l = pollo_name.get(g)
                if l and (l in quotes_map2):
                    pts, why = compute_pollo_extra_new(quotes_map2, l)
                    pts_adj = float(pts) + 1.0   # alleggerito di 1 come POLLO FANTASMA
                    pollo_extra[l] += pts_adj
                    giorno_player_extra[g].setdefault(l, []).append(
                        ("hen_ghost", pts_adj, f"Pollo Fantasma — {why} (CASH OUT, −1 rispetto al Pollo)")
                    )

            # 👻🐔 POLLO FANTASMA = unico perdente reale e in giornata c’è ≥1 fantasmino
            elif flag == "POLLO_FANTASMA":
                l = pollo_name.get(g)
                if l and (l in quotes_map2):
                    pts, why = compute_pollo_extra_new(quotes_map2, l)  # es. -6..-2
                    pts_adj = float(pts) + 1.0                         # alleggerito di 1 → -6→-5, ...
                    pollo_extra[l] += pts_adj
                    giorno_player_extra[g].setdefault(l, []).append(
                        ("hen_ghost", pts_adj, f"Pollo Fantasma — {why} (−1 rispetto al Pollo)")
                    )

        # punti di giornata per grafico Killbet Arena (inclusi extra/malus)
        daily_add = {p: 0.0 for p in PLAYERS}

        # 1) punti base dalle partite
        for row in tab[-3:]:
            if row["giornata"] != g: 
                continue
            if row["partita"] in ("1", "2"):
                daily_add[row["CASA"]] += float(row["P_CASA"])
                daily_add[row["OSPITE"]] += float(row["P_OSP"])

        # 2) aggiungi anche gli extra della giornata (volpe, pollo, champ, courage, fantasmino, ecc.)
        for pl, extras in giorno_player_extra.get(g, {}).items():
            for _, pts, _ in extras:
                try:
                    daily_add[pl] += float(pts)
                except Exception:
                    pass

        # 3) aggiorna i cumulati e salva la progressione per il grafico
        for p in PLAYERS:
            per_day_totals[p] += daily_add.get(p, 0.0)
            per_day_points[p].append(per_day_totals[p])


                    # Killbet Arena
                    
    # Ricalcolo robusto dei malus Fantasmino direttamente dal DF filtrato (fino_a)
    if "fantasmino" in df.columns:
        _gp = (
            df[df["fantasmino"] == True]
            .groupby("giocatore")["fantasmino"]
            .size()
            .mul(-5.0)
            .to_dict()
        )
        ghost_penalty = {p: float(_gp.get(p, 0.0)) for p in PLAYERS}
    else:
        ghost_penalty = {p: 0.0 for p in PLAYERS}

    rows=[]
    for p in PLAYERS:
        P_base = base[p]
        P_bonus = bonus_diff[p]
        P_malus = malus_diff[p]
        P_half  = half_adj[p]
        P_volpe = volpe_extra[p]

        # Malus Pollo: separiamo classico e fantasma leggendo gli extra giornalieri
        P_pollo_classic = 0.0    # solo ("hen", …)
        P_pollo_ghost   = 0.0    # solo ("hen_ghost", …)

        P_champs = champions_bonus[p]
        P_courage = courage_bonus.get(p, 0.0)
        P_fantasmino = ghost_penalty.get(p, 0.0)

        P_allwin  = 0.0
        P_alllose = 0.0

        # Somma su TUTTE le giornate registrate in giorno_player_extra
        for gg, extras in (giorno_player_extra or {}).items():
            for extra in (extras.get(p, []) or []):
                try:
                    kind, pts, why = extra
                except Exception:
                    continue
                if kind == "hen":
                    try: P_pollo_classic += float(pts)
                    except Exception: pass
                elif kind == "hen_ghost":
                    try: P_pollo_ghost += float(pts)
                    except Exception: pass
                elif kind == "allwin":
                    try: P_allwin += float(pts)
                    except Exception: pass
                elif kind == "alllose":
                    try: P_alllose += float(pts)
                    except Exception: pass

        # Totale = somma reale di tutte le colonne (così coincide sempre con la tabella)
        P_tot = (
            float(P_base) + float(P_half) + float(P_bonus) + float(P_malus) +
            float(P_volpe) + float(P_pollo_classic) + float(P_pollo_ghost) +
            float(P_champs) + float(P_courage) +
            float(P_fantasmino) + float(P_allwin) + float(P_alllose)
        )

        rows.append({
            "GIOCATORE": p,
            "Totale": P_tot,
            "Punti base": P_base,
            "Penalità quote basse": P_half,
            "Bonus differenza quote": P_bonus,
            "Malus differenza quote": P_malus,
            "Bonus Volpe": P_volpe,
            "Malus Pollo": P_pollo_classic,
            "Malus Pollo Fantasma": P_pollo_ghost,
            "Bonus Champions": P_champs,
            "Bonus Coraggio": P_courage,
            "Malus Fantasmino": P_fantasmino,
            "Bonus Tutti Vincenti": P_allwin,
            "Malus Tutti Perdenti": P_alllose,
        })
        
    classifica = (
        pd.DataFrame(rows)
        .sort_values(["Totale"], ascending=False, kind="mergesort")
        .reset_index(drop=True)
    )

    # Polli/volpi + Danno economico (Pollo o Pollo Fantasma, NO in cash-out)
    polli = {p: 0 for p in PLAYERS}
    volpi = {p: 0 for p in PLAYERS}
    danni = {p: 0.0 for p in PLAYERS}
    # lista di (giornata, danno, is_pf) → is_pf=True se nella giornata c'era ≥1 Fantasmino
    danni_giornate = {p: [] for p in PLAYERS}
    giornate_all_win = []


    # Raccoglie TUTTE le quote reali (V o P) escludendo i Fantasmini e i vuoti
    def _real_quotes_excluding_ghosts(dfg_day):
        qs = []
        for _, r in dfg_day.iterrows():
            if bool(r.get("fantasmino", False)):
                continue  # niente quota per i 👻
            q = r.get("quota")
            if q in (None, ""):
                continue
            qf = _try_float(q)
            if qf is not None:
                qs.append(float(qf))
        return qs

    
    for g in sorted(df["giornata"].unique()):
        dfg = df[df["giornata"] == g].copy()
        # Ignora i fantasmini per verificare se i dati della giornata sono completi
        dfg_real = dfg.loc[~dfg.get("fantasmino", False).fillna(False).astype(bool)]
        if dfg_real["esito"].isna().any():
            continue

        has_co = (st.session_state.get("cashouts", {}).get(g) is not None)
        es = dfg_real["esito"].to_numpy()

        # Volpe (unico vincente) — conteggio sempre
        if (es == "V").sum() == 1:
            winner = dfg_real.iloc[np.where(es == "V")[0][0]]["giocatore"]
            volpi[winner] += 1

        # Tutti vincenti — importo (no cash-out)
        q_clean = dfg_real["quota"].apply(lambda v: None if v in (None, "") else str(v).replace(",", "."))
        qnum = pd.to_numeric(q_clean, errors="coerce")
        
        # Tutti vincenti — importo (no cash-out) → ORA prende SOLO dalla vincita manuale
        if (es == "V").sum() == 5 and not has_co:
            mv = (st.session_state.get("manual_wins", {}) or {}).get(g)
            if mv is not None:
                giornate_all_win.append((g, float(mv)))


        # Pollo / Pollo Fantasma — conteggio sempre; DANNI economici SOLO da manuale e SOLO se NON cash-out
        if (es == "P").sum() == 1:
            loser = dfg_real.iloc[np.where(es == "P")[0][0]]["giocatore"]
            polli[loser] += 1

            if not has_co:
                manual_loss = (st.session_state.get("manual_losses", {}) or {}).get(g)
                if manual_loss is not None:
                    n_ghosts_day = int(dfg.get("fantasmino", False).fillna(False).astype(bool).sum())
                    is_pf = (n_ghosts_day >= 1)
                    danni[loser] += float(manual_loss)
                    danni_giornate[loser].append((g, float(manual_loss), is_pf))

    def danno_descr(p):
        tot = danni[p]
        dettagli = danni_giornate[p]  # lista di tuple (giornata, danno, is_pf)
        if not dettagli:
            return eur(tot)
        # costruisci la lista: se is_pf è True aggiungi 👻 dopo la giornata
        parts = [
            f"G{g}{'👻' if is_pf else ''}:{eur(val)}"
            for (g, val, is_pf) in dettagli
        ]
        return f"{eur(tot)} ({' - '.join(parts)})"

    df_polli = pd.DataFrame({
        "GIOCATORE": PLAYERS,
        "POLLI": [polli[p] for p in PLAYERS],
        "DANNO": [danno_descr(p) for p in PLAYERS]
    })
    df_volpi = pd.DataFrame({
        "GIOCATORE": PLAYERS,
        "VOLPI": [volpi[p] for p in PLAYERS]
    })
    df_tab=pd.DataFrame(tab)

    # --- Render di una riga partita nella scheda giornata (niente 🐔 qui) ---
    def _render_partita_riga(row):
        # Quote da mostrare: 👻 se fantasmino, altrimenti (quota)
        quota_home_disp = row.get("DQ_CASA", "")
        quota_away_disp = row.get("DQ_OSP", "")

        casa = str(row.get("CASA", ""))
        osp  = str(row.get("OSPITE", ""))

        # Riga principale (nomi + quote/👻)
        st.markdown(
            f"<div class='match-row'>"
            f"<b>{casa}</b> {quota_home_disp} &nbsp; vs &nbsp; <b>{osp}</b> {quota_away_disp}"
            f"</div>",
            unsafe_allow_html=True
        )

        # Eventuale riga note Fantasmino (solo se presenti)
        note_casa = row.get("NOTE_CASA", "")
        note_osp  = row.get("NOTE_OSP", "")
        if note_casa or note_osp:
            st.markdown(
                f"<div class='nota-fantasma'>"
                f"{casa}: {note_casa} &nbsp;&nbsp;&nbsp; {osp}: {note_osp}"
                f"</div>",
                unsafe_allow_html=True
            )

    # Colonne di visualizzazione per quote: 👻 se fantasmino, altrimenti (quota)
    def _fmt_disp_quota(q):
        if q in (None, "", float("nan")): 
            return ""
        try:
            qs = str(q).replace(",", ".")
            return f"({qs})"
        except Exception:
            return ""

    # Assicura le colonne flag se non presenti (per giornate vecchie)
    for col in ("F_CASA","F_OSP"):
        if col not in df_tab.columns:
            df_tab[col] = False

    df_tab["DQ_CASA"] = np.where(df_tab["F_CASA"], "👻", df_tab["Q_CASA"].map(_fmt_disp_quota))
    df_tab["DQ_OSP"]  = np.where(df_tab["F_OSP"],  "👻", df_tab["Q_OSP"].map(_fmt_disp_quota))

    # Nota/malus da mostrare solo al giocatore fantasmino
    df_tab["NOTE_CASA"] = np.where(df_tab["F_CASA"], "−5 Fantasmino", "")
    df_tab["NOTE_OSP"]  = np.where(df_tab["F_OSP"],  "−5 Fantasmino", "")

    # Filippoide cumulata da G0
    max_len=max((len(v) for v in fil_deltas.values()), default=0)
    for p in PLAYERS:
        while len(fil_deltas[p])<max_len: fil_deltas[p].append(0.0)
        fil_deltas[p]=[0.0]+fil_deltas[p]
    giornate=list(range(0, max_len+1))
    cum={p: np.cumsum(fil_deltas[p]).tolist() for p in PLAYERS}
    df_fili=pd.DataFrame({"Giornata":giornate})
    
    for p in PLAYERS: df_fili[p]=cum[p]

    # Serie Killbet Arena per grafico (con Fantasmino incluso)
    df_gen = pd.DataFrame({"Giornata": list(range(1, max_len + 1))})
    for p in PLAYERS: df_fili[p]=cum[p]

    # Serie Killbet Arena per grafico (malus Fantasmino già incluso negli extra → no doppio conteggio)
    df_gen = pd.DataFrame({"Giornata": list(range(1, max_len + 1))})
    for p in PLAYERS:
        vals = []
        for i, v in enumerate(per_day_points[p][:len(df_gen)], start=1):
            # NON aggiungiamo più il malus qui, perché già conteggiato in giorno_player_extra
            vals.append(v)

        # 🔸 Fix: se la lunghezza non combacia (es. RIP o Fantasmino escluso), allinea con 0
        if len(vals) < len(df_gen):
            vals += [0] * (len(df_gen) - len(vals))
        elif len(vals) > len(df_gen):
            vals = vals[:len(df_gen)]

        df_gen[p] = vals

    # Arrotondo i valori della Killbet Arena a 2 decimali
    df_gen = df_gen.round(2)




                    # ===== MOVIMENTI CASSA (timeline) =====

    events = []  # (key, label, amount, kind) key=float(g) o "gg/mm/aa"

    # costo schedina e vincite/cashout
    for g in range(1, max_len+1):
        day = df[df["giornata"]==g]

        # usa lo stake salvato per quella giornata, altrimenti default
        if not day.empty and "stake" in day.columns and not day["stake"].isna().all():
            stake_val = float(day["stake"].iloc[0])
        else:
            stake_val = STAKE_DEFAULT

        events.append((float(g)-0.4, f"G{g} — 🟥 schedina -{eur(stake_val)}€", -stake_val, "bet"))

        if not day.empty:
            # === 1) CASH-OUT: registra SOLO se importo > 0 ===
            if g in (cashouts or {}) and float(cashouts.get(g) or 0) > 0:
                imp_val = float((cashouts or {}).get(g, st.session_state.get("cashouts", {}).get(g, 0.0)))
                flag = giornata_flag.get(g, "CASH_OUT")

                if flag == "CASH_FANTASMA":
                        ghosts = [str(r["giocatore"]) for _, r in day.iterrows() if bool(r.get("fantasmino", False))]
                        ghost_list = ", ".join(ghosts) if ghosts else "?"
                        events.append((float(g) + 0.3, f"G{g} — 👻 CASH OUT con FANTASMA {ghost_list}", imp_val, "cashout_fantasma"))

                elif flag == "CASH_POLLO_FANTASMA":
                        loser = pollo_name.get(g, "")
                        ghosts = [str(r["giocatore"]) for _, r in day.iterrows() if bool(r.get("fantasmino", False))]
                        ghost_list = ", ".join(ghosts) if ghosts else "?"
                        events.append((float(g) + 0.3, f"G{g} — 🐔👻 CASH OUT con POLLO {loser} + FANTASMA {ghost_list}", imp_val, "cashout_pollofantasma"))

                elif flag == "CASH_POLLO":
                        loser = pollo_name.get(g, "")
                        events.append((float(g) + 0.3, f"G{g} — 🐔 CASH OUT con POLLO {loser}", imp_val, "cashout_pollo"))

                elif flag == "CASH_ALL_WIN":
                    events.append((float(g) + 0.3, f"G{g} — 🪙 CASH OUT TUTTI VINCENTI 🪙", imp_val, "cashout_allwin"))

                else:
                        events.append((float(g) + 0.3, f"G{g} — 🪙 CASH OUT QUASI TUTTI VINCENTI", imp_val, "cashout"))
            
            else:
                # === Vincite (manuali) ===
                vm = st.session_state.get("manual_wins", {}).get(g, 0.0)
                if vm > 0:
                    if giornata_flag.get(g) == "ALL_WIN":
                        events.append((
                            float(g)+0.3,
                            f"G{g} — 🪙 TUTTI VINCENTI: {eur(vm)}",
                            vm,
                            "allwin"
                        ))
                    elif giornata_flag.get(g) == "QUASI_ALL_WIN":
                        events.append((
                            float(g)+0.3,
                            f"G{g} — 🥈 I fanta Vincenti (4V + 1👻): {eur(vm)}",
                            vm,
                            "quasiwin"
                        ))
                    else:
                        events.append((
                            float(g)+0.3,
                            f"G{g} — 🪙 Vincita: {eur(vm)}",
                            vm,
                            "win"
                        ))

                                            
    # RICARICHE (💸 con nomi corretti)
    _ric_source = ricariche.get("movimenti", ricariche) if isinstance(ricariche, dict) else ricariche
    for k, vals in (_ric_source or {}).items():
        try:
            imp_list = vals.get("importi", []) if isinstance(vals, dict) else vals
            players = vals.get("players", []) if isinstance(vals, dict) else []
            players_str = f" ({', '.join(players)})" if players else ""

            if isinstance(k, str) and "/" in k:
                # chiave = data (es. "05/10/25")
                for imp in imp_list:
                    events.append((
                        k,
                        f"{k} — 💸 Ricarica{players_str}",
                        float(imp),
                        "topup_date"
                    ))
            else:
                # chiave = numero di giornata (es. 6)
                key = float(k)
                for i, imp in enumerate(imp_list):
                    events.append((
                        key + i * 0.01,  # offset per ricariche multiple nella stessa giornata
                        f"RG{str(k).replace('.', ',')} — 💸 Ricarica{players_str}",
                        float(imp),
                        "topup"
                    ))
        except Exception:
            continue

                # === FILTRO EVENTI IN BASE ALLA GIORNATA SELEZIONATA (fino_a) ===
    try:
        if fino_a is not None:
            fino_a_val = float(fino_a)
            # Teniamo anche gli eventi leggermente successivi (es. +0.1)
            events = [
                ev for ev in events
                if not (
                    isinstance(ev[0], (int, float)) and ev[0] > fino_a_val + 0.4                )
            ]
    except Exception:
        pass



    # ordina: numerici per primi, poi date
    events.sort(key=lambda x: (x[0] if not (isinstance(x[0], str) and "/" in x[0]) else float("inf")))

    # timeline e punti grafico
    cur = CASSA_START
    mov_rows = []
    graph_pts = []
    last_num_x = 0.6
    bump_step = 0.2

    # mappa dei "kind" che consideriamo vincite (VG: vincita o cash-out)
    _KIND_VG = {
        "win", "allwin", "quasiwin",
        "cashout", "cashout_allwin", "cashout_fantasma",
        "cashout_pollo", "cashout_pollofantasma"
    }

    for key, label, amt, kind in events:
        cur += amt

        if isinstance(key, str) and "/" in key:
            # Ricarica con data → RG data
            last_num_x += bump_step
            x_val = last_num_x
            x_label = f"RG {key}"

            mov_rows.append({
                "Giornata": x_label,
                "Movimento": f"{x_label} — Ricarica",
                "Importo": eur(amt),
                "Cassa dopo €": eur(cur),
                "Tipo": kind
            })
            graph_pts.append({"Giornata": x_label, "x": float(x_val), "y": float(cur), "Tipo": kind})
            continue

        # numerico (giornata)
        x_val = float(key)
        last_num_x = x_val

        # 🔹 Mantiene il numero di giornata coerente con l’evento (senza sballare VG8/VG9)
        #    - Stake → g - 0.4
        #    - Ricariche → g + 0.01
        #    - Vincite / Cash-out → g + 0.3
        #    Tutti restano etichettati nella stessa giornata (es. G7, RG7, VG7)
        g_int = max(1, min(int(round(x_val)), max_len))

                
        # Se la ricarica è una lista di importi → somma
        if isinstance(amt, list):
            amt = sum(amt)
            
        if kind in ("topup", "topup_date"):
            # Mantiene l'etichetta originale con 💸 e nomi giocatori
            x_label = f"RG{str(x_val).replace('.', ',')}"
            mov_rows.append({
                "Giornata": x_label,
                "Movimento": label,  # usa la label già completa (💸 + nomi)
                "Importo": eur(amt),
                "Cassa dopo €": eur(cur),
                "Tipo": kind
            })


        elif kind in _KIND_VG:
            # Vincita o cash-out → VG#
            x_label = f"VG{g_int}"
            mov_rows.append({
                "Giornata": x_label,
                "Movimento": label,
                "Importo": eur(amt),
                "Cassa dopo €": eur(cur),
                "Tipo": kind
            })
        else:
            # Stake schedina → G#
            x_label = f"G{g_int}"
            mov_label = label.replace("💩", "💩")
            mov_rows.append({
                "Giornata": x_label,
                "Movimento": mov_label,
                "Importo": eur(amt),
                "Cassa dopo €": eur(cur),
                "Tipo": kind
            })

        graph_pts.append({"Giornata": x_label, "x": float(x_val), "y": float(cur), "Tipo": kind})

    df_mov = pd.DataFrame(mov_rows)
    df_cassa = pd.DataFrame(graph_pts)


    
    # Arrotondo i valori a 2 decimali per evitare problemi di float nei confronti/parità
    df_mov = df_mov.round(2)
    df_cassa = df_cassa.round(2)


    # ✅ Punto iniziale G0 (saldo prima di ogni stake/vincita)
    if not df_cassa.empty:
        df_cassa = pd.concat([
            pd.DataFrame([{
                "Giornata": "G0",
                "x": 0.0,
                "y": CASSA_START,
                "Tipo": "init"
            }]),
            df_cassa
        ], ignore_index=True)

    # Colori per soglie + ricariche
    def color_by_cash(c, kind=None):
        if kind in ("topup","topup_date"): return "BROWN"
        if c > 300: return "GOLD"
        if c > 100: return "GREEN"
        if c > 50:  return "ORANGE"
        return "RED"


    # Segmenti
    seg_rows=[]
    if not df_cassa.empty:
        pts_sorted = df_cassa.sort_values("x").to_dict("records")
        for i in range(1, len(pts_sorted)):
            prev = pts_sorted[i-1]
            curr = pts_sorted[i]
            col = color_by_cash(curr["y"], curr["Tipo"])
            seg_id = f"{prev['Giornata']}->{curr['Giornata']}"
            seg_rows.append({"seg_id":seg_id,"Giornata":prev["Giornata"],"x":float(prev["x"]),"y":float(prev["y"]),"Colore":col,"ord":0})
            seg_rows.append({"seg_id":seg_id,"Giornata":curr["Giornata"],"x":float(curr["x"]),"y":float(curr["y"]),"Colore":col,"ord":1})
    df_seg = pd.DataFrame(seg_rows)

        # flags festa
    last_all_win = max([g for g,_ in giornate_all_win], default=None)

    # giorni di cashout (solo numerici)
    cashout_days = []
    giornata_flag_cash = {}  # mappa locale SOLO per i movimenti cassa

    for key, _, __, kind in events:
        if kind == "cashout" and not (isinstance(key, str) and "/" in key):
            gnum = int(round(float(key) + 0.4))
            cashout_days.append(gnum)

            # --- Identificazione speciale dei cash out ---
            day = df[df["giornata"] == gnum]
            es = day["esito"].to_numpy() if ("esito" in day.columns and not day.empty) else np.array([])
            ghosts = int(day["fantasmino"].fillna(False).astype(bool).sum()) if "fantasmino" in day.columns else 0
            n_p = int((es == "P").sum()) if es.size > 0 else 0

            if n_p == 1 and ghosts >= 1:
                giornata_flag[gnum] = "CASH_POLLO_FANTASMA"
            elif n_p == 1:
                giornata_flag[gnum] = "CASH_POLLO"
            elif ghosts >= 1:
                giornata_flag[gnum] = "CASH_FANTASMA"
            else:
                giornata_flag[gnum] = "CASH_OUT"

            # --- Aggiorna anche events con tipo specifico ---
            for i, ev in enumerate(events):
                if ev[0] == float(gnum) + 0.1 and ev[3] == "cashout":
                    if giornata_flag[gnum] == "CASH_POLLO_FANTASMA":
                        events[i] = (ev[0], f"G{gnum} — 🐔👻 CASH OUT con POLLO+FANTASMA", ev[2], "cashout_pollofantasma")
                    elif giornata_flag[gnum] == "CASH_FANTASMA":
                        events[i] = (ev[0], f"G{gnum} — 👻 CASH OUT con FANTASMA", ev[2], "cashout_fantasma")
                    elif giornata_flag[gnum] == "CASH_POLLO":
                        events[i] = (ev[0], f"G{gnum} — 🐔 CASH OUT con POLLO", ev[2], "cashout_pollo")
                    else:
                        events[i] = (ev[0], f"G{gnum} — 💸 CASH OUT", ev[2], "cashout")

        cashout_days = sorted(set(cashout_days))

        return (classifica, df_polli, df_volpi, df_tab, df_fili, df_gen,
                giornata_flag, df_cassa, df_mov, df_seg,
                giorno_player_extra, pollo_name, volpe_name,
                last_all_win, giornate_all_win, cashout_days
        )

            # -------------------- UI --------------------

st.set_page_config(page_title=TITLE, layout="wide")

# 🔹 Mostra il titolo solo nella home page
if st.session_state.get("view", "home") == "home":
    st.title(TITLE)

    # 🔹 Centra e colora il titolo principale
    st.markdown("""
    <style>
    h1 {
        text-align: center !important;
        color: #d4af37 !important;
        font-weight: 1000 !important;
        margin-bottom: 0.3rem !important;
        text-shadow: 0 0 8px rgba(212,175,55,0.6);
    }
    </style>
    """, unsafe_allow_html=True)


def inject_css():
    st.markdown(f"""
    <style>
    .panel{{border:4px solid #1f4fb8; border-radius:16px; padding:10px 12px; margin:14px 0; background:#0b0b0b;}}
    .panel h2, .panel h3{{margin:6px 0 8px}}

    .cele-title{{font-size:48px;font-weight:900;color:{GOLD};text-align:center;
    text-shadow:0 0 6px #000, 0 0 12px #caa93a;margin:14px 0 6px}}
    .cele-sub{{font-size:26px;font-weight:800;color:{GOLD};text-align:center;margin-bottom:16px}}
    .cele-title-silver{{font-size:44px;font-weight:900;color:{SILVER};text-align:center;
    text-shadow:0 0 8px #000, 0 0 10px #999;margin:14px 0 6px}}
    .cele-sub-silver{{font-size:24px;font-weight:800;color:{SILVER};text-align:center;margin-bottom:16px}}

    .card{{border-radius:16px;border:1px solid #1f4fb8;background:#0b0b0b;color:#eee; margin-bottom:14px;}}
    .card-head{{background:#0a2a6b;color:#fff;border-radius:16px 16px 0 0;
    padding:10px 12px;font-weight:900;text-align:center;letter-spacing:.5px}}
    .card-body{{padding:10px 12px 12px}}

    .card-allwin{{background:#1a1400; border:2px solid {GOLD}; box-shadow:0 0 14px {GOLD}88;}}
    .card-pollo{{background:#2b0a0e; border:2px solid #b00020; box-shadow:0 0 12px #ff3b3b88;}}
    .card-volpe{{background:#2a1905; border:2px solid {ORANGE}; box-shadow:0 0 12px {ORANGE}88;}}
    .card-alllose{{background:#3e2f1c; border:2px solid #a67c52; box-shadow:0 0 14px #a67c5288;}}
    
    .card-cashout {{
        background:#041a08; 
        border:2px solid {GREEN}; 
        box-shadow:0 0 12px {GREEN}88;
    }}
    .card-cashout .card-head {{
        background:{GREEN}; 
        color:#111;
    }}

    .card-quasiwin {{
        background:#2b2b2b;         /* grigio scuro */
        border:2px solid #fff;      /* bordo bianco */
        box-shadow:0 0 14px #ccc;   /* alone chiaro */
        color:#eee;
    }}
    .card-quasiwin .card-head {{
        background:#C0C0C0;         /* argento */
        color:#111;
        font-weight:900;
    }}

    .card-cashfantasma {{
        background:#ffffff !important;   /* scheda bianca */
        border:3px solid #000;
        box-shadow:0 0 14px #999;
        color:#111;
    }}

    .card-cashfantasma .card-head {{
        background:#000;       /* intestazione nera */
        color:#fff;            /* testo bianco leggibile */
        font-weight:900;
    }}

    /* Etichetta nera attorno al testo bianco */
    .card-cashfantasma .card-body span,
    .card-cashfantasma .card-body div {{
        color:#fff !important;            /* testo bianco */
        background:#000 !important;       /* rettangolo nero dietro */
        display:inline-block;             /* così fa il rettangolino */
        padding:2px 6px;                  /* spaziatura interna */
        border-radius:4px;                /* angoli arrotondati */
        margin:2px 0;                     /* piccolo distacco verticale */
    }}

    /* Cash Out con Pollo */
    .card-cashpollo {{
        background:#041a08;              /* verde scuro */
        border:5px solid #b00020;        /* bordo rosso spesso */
        box-shadow:0 0 16px #b0002088;   /* alone rosso */
        color:#eee;
    }}
    .card-cashpollo .card-head {{
        background:#16c60c;              /* verde acceso */
        color:#111;
        font-weight:900;
    }}

    /* Cash Out con Pollo + Fantasma */
    .card-cashpollofantasma {{
        background:#041a08 !important;    /* verde scuro, forzato */
        border:4px solid #fff;            /* bordo bianco */
        box-shadow:0 0 16px #ff000088;    /* alone rosso */
        color:#eee;
    }}
    .card-cashpollofantasma .card-head {{
        background:#16c60c !important;    /* verde acceso come cash out normale */
        color:#111;                       /* testo scuro leggibile */
        font-weight:900;
        border-bottom:3px solid #fff;     /* riga bianca sotto per evidenziare */
    }}


    .card-champday {{
        background:#001a4d; 
        border:3px solid #ffffff; 
        box-shadow:0 0 16px #88aaff66;
    }}
    .card-champday .card-head {{
        background:#0a3a9a; 
        color:#ffffff;
    }}

    .total-pts{{font-weight:900; font-size:1.08rem;}}

    .card-allwin .card-head{{background:{GOLD}; color:#111;}}
    .card-pollo .card-head{{background:#b00020; color:#fff;}}
    .card-volpe .card-head{{background:{ORANGE}; color:#111;}}
    .card-alllose .card-head{{background:#a67c52; color:#111;}}
    .card-cashout .card-head{{background:{GREEN}; color:#111;}}
    
    .vs{{font-weight:800; text-align:left; color:#fafafa}}
    .es{{color:#e7e7e7;font-size:1.22rem;margin-top:4px}}
    .rip{{margin-top:6px;font-size:.93rem;color:{GOLD};background:#0b0b0b;border-left:4px solid {GOLD};
        padding:6px 8px;border-radius:6px}}
    .ripname{{color:{GOLD};font-weight:800}}
    .bonus{{margin-top:4px;color:#00ff9c;font-weight:900}}
    .malus{{margin-top:2px;color:#ff6b6b;font-weight:900}}
    .punti-casa,.punti-osp{{display:block;margin-top:4px;color:#f0f0f0}}
    .good{{color:#1bd11b;font-weight:900}}
    .bad{{color:#ff3b3b;font-weight:900}}
    .goldcell td, .goldcell th{{color:{GOLD} !important; font-weight:800 !important; text-align:center !important;}}
    .center td, .center th{{text-align:center !important}}
    .riga{{margin:6px 0 10px;border-bottom:1px dashed #555;padding-bottom:6px}}
    .riga:last-child{{border-bottom:none}}
    .extra-line{{display:block; margin-top:4px; font-weight:900}}
      /* --- Chips inline per step/malus/bonus --- */
    .steps {{
        display: flex;
        flex-wrap: wrap;
        gap: 6px 8px;
        margin: 6px 0 10px;
    }}
    .chip {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border: 1px solid #444;
        border-radius: 999px;
        background: #141414;
        font-size: 17px;
        line-height: 1.4;
    }}
    .chip small {{opacity: .85}}
    .chip.strong {{font-weight:700}}
    </style>
    """, unsafe_allow_html=True)

inject_css()
init_state()

# 🔹 Stile legenda e testi più leggibili
st.markdown("""
<style>
.legend, .stMarkdown p, .stMarkdown ul li {
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    line-height: 1.5 !important;
}
</style>
""", unsafe_allow_html=True)


                # Modalità  Utente/Amministratore
            
            
with st.sidebar:
    st.subheader("🧭 Modalità")
    idx = 1 if st.session_state.get("admin_pin_ok", False) else 0
    mode = st.radio("Seleziona", ["Utente","Amministratore"], index=idx, key="mode_radio")
    if mode=="Utente":
        if st.session_state.get("admin_pin_ok", False):
            if st.button("Torna a modalità utenti", key="to_user"):
                st.session_state["admin_pin_ok"]=False; st.rerun()
    else:
        if not st.session_state.get("admin_pin_ok", False):
            pin=st.text_input("PIN admin", type="password", placeholder="Inserisci PIN", key="pin_input")
            if st.button("Entra", key="enter_admin"):
                if pin==ADMIN_PIN: st.session_state["admin_pin_ok"]=True; st.rerun()
                else: st.error("PIN errato")

is_admin = bool(st.session_state.get("admin_pin_ok", False))
df = st.session_state.data


            # Amministratore: risultati, cash out, ricariche
if is_admin:

        # --- STAKE / Costo della giocata ---
    st.subheader("💶 Costo della giocata (STAKE)")
    c1, c2 = st.columns([1,1])
    with c1:
        stake_str = st.text_input(
            "Costo per giornata (€)",
            value=str(st.session_state.get("stake_value", STAKE_DEFAULT)),
            help="Puoi usare virgola o punto: es. 10, 12.50, 8,00"
        )
    with c2:
        colb1, colb2 = st.columns([1,1])
        with colb1:
            if st.button("Salva STAKE"):
                val = stake_str.replace(",", ".").strip()
                try:
                    new_stake = round(float(val), 2)
                    if new_stake <= 0:
                        st.warning("Lo stake deve essere > 0.")
                    else:
                        st.session_state["stake_value"] = new_stake
                        st.success(f"Stake aggiornato a {new_stake:.2f} €")
                except Exception:
                    st.error("Valore non valido. Usa numeri tipo 10, 12.50 o 8,00.")
        with colb2:
            if st.button("Ripristina default (10,00 €)"):
                st.session_state["stake_value"] = STAKE_DEFAULT
                st.info("Stake riportato al valore di default: 10,00 €")

                # ====== Giornate Champions (solo Admin) ======
                
    st.subheader("Giornate Champions")
    cc1, cc2 = st.columns(2)
    champs = st.session_state.get("champions_days", [])
    g1 = champs[0] if len(champs)>0 else None
    g2 = champs[1] if len(champs)>1 else None
    with cc1:
        g1_new = st.selectbox("Giornata Champions #1", [None]+list(range(1, NUM_GIORNATE+1)),
                            index=([None]+list(range(1, NUM_GIORNATE+1))).index(g1) if g1 in ([None]+list(range(1, NUM_GIORNATE+1))) else 0)
    with cc2:
        g2_new = st.selectbox("Giornata Champions #2", [None]+list(range(1, NUM_GIORNATE+1)),
                            index=([None]+list(range(1, NUM_GIORNATE+1))).index(g2) if g2 in ([None]+list(range(1, NUM_GIORNATE+1))) else 0)
    if st.button("💾 Salva giornate Champions", key="save_champdays"):
        new_list = [x for x in [g1_new, g2_new] if x is not None]
        st.session_state["champions_days"] = sorted(list(set(new_list)))
        if st.session_state["champions_days"]:
            st.success("Giornate Champions impostate: " + ", ".join(str(x) for x in st.session_state["champions_days"]))
        else:
            st.info("Nessuna giornata Champions impostata.")
        save_all()  # <— AGGIUNTA
        
    colA, colB = st.columns([1, 1])

    with colA:
        # 🔹 Calcola l'ultima giornata compilata come default
        ultima_giornata = 1
        for g in sorted(df["giornata"].unique()):
            if not df[df["giornata"] == g]["esito"].isna().any():
                ultima_giornata = g

        giornata = st.number_input(
            "Giornata da compilare",
            1, NUM_GIORNATE,
            value=ultima_giornata,
            step=1,
            key="giornata_admin"
        )

    # Filtra il dataframe per la giornata selezionata
    dfg = df[df["giornata"] == giornata].set_index("slot").copy()


    # Stake della giornata (eredita dalla precedente se esiste, altrimenti default)
    if "stake" in df.columns and not df.empty and (df["giornata"] < giornata).any():
        last_stake = df.loc[df["giornata"] < giornata, "stake"].dropna().iloc[-1]
    else:
        last_stake = STAKE_DEFAULT

    def edit_row(label, row, g):
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        c1.write(f"**{label}: {row['giocatore']}**")

        # stato iniziale del flag
        f_default = bool(row.get("fantasmino", False))

        # 👻 Fantasmino
        f_flag = c4.checkbox(
            "👻 Fantasmino",
            value=f_default,
            key=f"fant_{g}_{label}_{row['giocatore']}"
        )

        # Esito (disabilitato se fantasmino)
        options = ["", "V", "P"]
        default_index = options.index(row["esito"]) if row.get("esito") in ("V", "P") else 0
        e = c2.selectbox(
            "Esito",
            options,
            index=default_index,
            key=f"esito_{g}_{label}_{row['giocatore']}",
            disabled=f_flag   # <-- adesso usa il flag corrente
        )

        # Quota (disabilitata se fantasmino)
        qtxt = c3.text_input(
            "Quota",
            value="" if row.get("quota") is None else str(row.get("quota")),
            key=f"quota_{g}_{label}_{row['giocatore']}",
            disabled=f_flag   # <-- idem
        )

        # Se è fantasmino: non validare quota/esito
        if f_flag:
            return None, None, True

        # Validazione quota (solo se NON fantasmino)
        q = None
        if qtxt.strip() != "":
            if _re.match(r"^\d+([\.,]\d{1,2})?$", qtxt.strip()):
                q = _try_float(qtxt)
            else:
                c3.error("Quota non valida: usa formato tipo 1,80 oppure 1.8 (max due decimali).")
                q = None

        return (None if e == "" else e), q, False


    # adesso siamo ancora dentro `with colA:`
    st.subheader(f"Compilazione giornata {giornata}")
    st.markdown("**Partita 1**")
    e1,q1,f1 = edit_row("CASA1", dfg.loc["CASA1"], giornata)
    e2,q2,f2 = edit_row("OSP1",  dfg.loc["OSP1"],  giornata)

    st.markdown("**Partita 2**")
    e3,q3,f3 = edit_row("CASA2", dfg.loc["CASA2"], giornata)
    e4,q4,f4 = edit_row("OSP2",  dfg.loc["OSP2"],  giornata)

    st.markdown("**Giocatore a riposo**")
    e5,q5,f5 = edit_row("RIP",   dfg.loc["RIP"],   giornata)

    # ⬇️ Pulsante SALVA GIORNATA subito sotto la compilazione (colonna sinistra)
    st.markdown("---")
    st.markdown(f"### 💾 **Salvataggio Giornata {giornata}**")

    if st.button(f"✅ Salva Giornata {giornata}", key=f"save_{giornata}", use_container_width=True):
        # Assicuro che la colonna 'fantasmino' esista
        if "fantasmino" not in df.columns:
            df["fantasmino"] = False

        # Stake corrente da salvare
        stake_val = float(st.session_state.get("stake_value", STAKE_DEFAULT))
        dfg["stake"] = stake_val  # salva lo stake in tutte le righe della giornata

        def row_vals(e, q, f):
            if f:  # 👻 se Fantasmino: azzera esito/quinta
                return [None, None, True]
            return [e, q, False]

        dfg.loc["CASA1", ["esito", "quota", "fantasmino"]] = row_vals(e1, q1, f1)
        dfg.loc["OSP1",  ["esito", "quota", "fantasmino"]] = row_vals(e2, q2, f2)
        dfg.loc["CASA2", ["esito", "quota", "fantasmino"]] = row_vals(e3, q3, f3)
        dfg.loc["OSP2",  ["esito", "quota", "fantasmino"]] = row_vals(e4, q4, f4)
        dfg.loc["RIP",   ["esito", "quota", "fantasmino"]] = row_vals(e5, q5, f5)

        # Riporta nel DF principale
        df.loc[df["giornata"] == giornata, ["slot", "giocatore", "esito", "quota", "fantasmino", "stake"]] = (
            dfg.reset_index()[["slot", "giocatore", "esito", "quota", "fantasmino", "stake"]].values
        )

        # Aggiorna stato + feedback (📣 SENZA spunta verde)
        st.session_state.data = df
        st.info(f"Giornata {giornata} salvata (Stake: {stake_val:.2f} €)")
        save_all()

    with colB:
        st.subheader("Cash Out 🪙")
        co_enabled = st.checkbox("Cash Out effettuato per questa giornata?", key=f"co_on_{giornata}")
        co_txt = st.text_input("Importo Cash Out (€)", value=eur(st.session_state.get("cashouts", {}).get(giornata, "")).replace(".", "X").replace(",", ".").replace("X", ",") if st.session_state.get("cashouts", {}).get(giornata) is not None else "", key=f"co_val_{giornata}", placeholder="es. 23,78 oppure 345.65")
        if st.button("💾 Salva Cash Out", key="save_cashout"):
            if co_enabled and co_txt.strip():
                try:
                    co_val = float(co_txt.replace(",", "."))
                    st.session_state["cashouts"][giornata] = co_val
                    st.success(f"Cash Out salvato per giornata {giornata}: {eur(co_val)} €")
                    save_all()  # <— AGGIUNTA
                except:
                    st.error("Importo non valido")
            else:
                if giornata in st.session_state["cashouts"]:
                    del st.session_state["cashouts"][giornata]
                st.info("Cash Out non impostato per questa giornata.")
                save_all()  # <— AGGIUNTA

        # --- VINCITA / PERDITA MANUALE (solo Admin) ---
        if is_admin:
            # Vincita manuale
            st.subheader("🪙 Vincita Totale (senza uso del cash out)")
            win_txt = st.text_input(
                "Importo vincita (€)",
                value=str(st.session_state.get("manual_wins", {}).get(giornata, "")),
                key=f"manual_win_{giornata}",
                placeholder="es. 120,50 oppure 120.50"
            )
            if st.button("💾 Salva vincita", key=f"save_win_{giornata}"):
                try:
                    if win_txt.strip() == "":
                        st.session_state["manual_wins"].pop(giornata, None)
                        st.info(f"Nessuna vincita impostata per G{giornata}.")
                        save_all()  # <— AGGIUNTA

                    else:
                        # ✅ Salvataggio vincita
                        wv = float(win_txt.replace(",", "."))
                        st.session_state.setdefault("manual_wins", {})[giornata] = round(wv, 2)
                        st.success(f"Vincita per G{giornata}: {eur(wv)} €")
                        save_all()  # <— AGGIUNTA

                        # 🔹 Imposta automaticamente il flag ALL_WIN se tutti gli esiti sono "V"
                        day_df = df[df["giornata"] == giornata]
                        if not day_df.empty:
                            esiti = day_df["esito"].dropna().tolist()
                            if len(esiti) == 5 and all(e == "V" for e in esiti):
                                st.session_state.setdefault("giornata_flag", {})[giornata] = "ALL_WIN"

                except Exception:
                    st.error("Valore non valido. Usa punto o virgola come separatore decimale.")


            # Perdita Pollo manuale
            st.subheader("🐔 Mancata vincita/Danno economico per Pollo")
            loss_txt = st.text_input(
                "Danno Pollo (€)",
                value=str(st.session_state.get("manual_losses", {}).get(giornata, "")),
                key=f"manual_loss_{giornata}",
                placeholder="es. 95,00 oppure 95.0"
            )
            if st.button("💾 Salva perdita Pollo", key=f"save_loss_{giornata}"):
                try:
                    if loss_txt.strip() == "":
                        st.session_state["manual_losses"].pop(giornata, None)
                        st.info(f"Nessuna perdita Pollo impostata per G{giornata}.")
                        save_all()  # <— AGGIUNTA
                    else:
                        lv = float(loss_txt.replace(",", "."))
                        st.session_state.setdefault("manual_losses", {})[giornata] = round(lv, 2)
                        st.success(f"Perdita Pollo per G{giornata}: {eur(lv)} €")
                        save_all()  # <— AGGIUNTA
                except Exception:
                    st.error("Valore non valido. Usa punto o virgola come separatore decimale.")



        # --- RICARICHE (solo Admin) ---
        
    st.subheader("Ricariche cassa per la giornata corrente")
    st.caption("Inserisci il totale della ricarica complessiva per questa giornata e seleziona i giocatori che hanno partecipato. "
            "La cifra inserita è il totale, non serve indicare quanto ha messo ciascuno.")

    # Campo di testo per l'importo totale (legato alla giornata corrente)
    ric_key = f"ricarica_importo_{giornata}"
    totale_txt = st.text_input("💰 Totale ricarica (€)", value=st.session_state.get(ric_key, ""), key=f"ric_txt_{giornata}")

    # Flag giocatori che partecipano alla ricarica
    players = ["ANGEL", "GARIBALDI", "CHRIS", "MG78IT", "FILLIP"]
    selected_players = []

    # Recupera dati salvati per questa giornata
    ric_data = st.session_state.get("ricariche", {}).get("movimenti", {})
    ric_day = ric_data.get(giornata, {}) if isinstance(ric_data, dict) else {}
    saved_players = ric_day.get("players", []) if isinstance(ric_day, dict) else []

    # Crea checkbox giornalieri
    for p in players:
        flag_key = f"ric_{p}_{giornata}"
        default_val = p in saved_players
        if st.checkbox(f"{p} ha partecipato alla ricarica", key=flag_key, value=default_val):
            selected_players.append(p)

    # Salvataggio
    if st.button("💾 Salva ricarica totale", key=f"save_ric_{giornata}"):
        try:
            totale_txt = str(totale_txt or "").strip()   # ✅ garantisce che sia sempre una stringa
            totale = float(totale_txt.replace(",", ".")) if totale_txt else 0.0
            ric = st.session_state.get("ricariche", {}).get("movimenti", {})

            # Aggiorna o crea la ricarica per la giornata corrente
            ric[giornata] = {
                "importi": [totale],
                "players": selected_players.copy()
            }

            st.session_state["ricariche"] = {"movimenti": ric}
            st.session_state[ric_key] = totale_txt
            save_all()

            st.success(f"💾 Ricarica di {totale:.2f} € salvata per la giornata {giornata}!")
        except Exception as e:
            st.error(f"Errore nel salvataggio ricarica: {e}")

    # --- Tabella di riepilogo ricariche salvate ---
    ric_data = st.session_state.get("ricariche", {})
    ric_mov = ric_data.get("movimenti", {}) if isinstance(ric_data, dict) else {}
    ric_view = []
    for k, vals in sorted(ric_mov.items(), key=lambda kv: str(kv[0])):
        try:
            if isinstance(vals, dict):
                importi = vals.get("importi", [])
                players = vals.get("players", [])
            else:
                importi = vals
                players = []

            totale = sum(float(x) for x in importi)
            ric_view.append({
                "Giornata": k,
                "Totale": eur(totale),
                "Giocatori": ", ".join(players) if players else "-"
            })
        except Exception as e:
            st.warning(f"Errore nella ricarica {k}: {e}")

    if ric_view:
        st.caption("📋 Ricariche salvate:")
        st.dataframe(pd.DataFrame(ric_view), hide_index=True, use_container_width=True)

    
        
        if st.session_state.get("cashouts"):
            tab_co = [{"Giornata": g, "Cash Out €": eur(v)} for g,v in sorted(st.session_state["cashouts"].items())]
            st.caption("Cash Out impostati:")
            st.dataframe(pd.DataFrame(tab_co), hide_index=True, use_container_width=True)
        
    cS,cR=st.columns(2)



# Calcoli

# Normalizza ricariche per i calcoli (compute_all vuole: {punto: [float, ...]})
_ric_raw = st.session_state.get("ricariche", {})
if isinstance(_ric_raw, dict) and "movimenti" in _ric_raw:
    _ric_calc = _ric_raw.get("movimenti", {})
else:
    _ric_calc = _ric_raw

# Normalizziamo ogni ricarica in formato coerente {"importi":[...], "players":[...]}
ricariche_norm = {}
for k, vs in (_ric_calc or {}).items():
    try:
        if isinstance(vs, dict):
            # Nuovo formato con giocatori
            importi = vs.get("importi", [])
            players = vs.get("players", [])
            ricariche_norm[k] = {
                "importi": [float(v) for v in importi],
                "players": players
            }
        elif isinstance(vs, list):
            # Vecchio formato: lista semplice di importi
            ricariche_norm[k] = {
                "importi": [float(v) for v in vs],
                "players": []
            }
        elif isinstance(vs, (int, float)):
            # Singolo importo
            ricariche_norm[k] = {
                "importi": [float(vs)],
                "players": []
            }
    except Exception:
        continue

# Ora passiamo il nuovo formato a compute_all()
(classifica, df_polli, df_volpi, df_tab, df_fili, df_gen,
giornata_flag, df_cassa, df_mov, df_seg,
giorno_player_extra, pollo_name, volpe_name,
last_all_win, giornate_all_win, cashout_days) = compute_all(
    st.session_state.data, fino_a=fino_a,
    ricariche=ricariche_norm,   # ⬅️ ora nel formato corretto per i giocatori
    cashouts=st.session_state.get("cashouts", {})
)


# Etichette con i nomi dei giocatori accanto alle ricariche (💸)
try:
    _ric_data = st.session_state.get("ricariche", {})
    _ric_mov = _ric_data.get("movimenti", {}) if isinstance(_ric_data, dict) else {}

    if not df_mov.empty and "Movimento" in df_mov.columns:
        for g, vals in _ric_mov.items():
            if not isinstance(vals, dict):
                continue
            players = vals.get("players", [])
            if not players:
                continue
            names_str = f" ({', '.join(players)})"

            # Trova nel DataFrame dei movimenti la riga corrispondente alla ricarica di quella giornata
            mask = df_mov["Movimento"].str.contains(f"RG{str(g).replace('.', ',')}.*Ricarica", case=False, na=False)
            df_mov.loc[mask, "Movimento"] = df_mov.loc[mask, "Movimento"] + names_str
except Exception as e:
    st.warning(f"Errore aggiornamento nomi ricariche: {e}")


# Icona 💸 accanto alle ricariche in colonna "Movimento" (dopo l'etichetta RG)
if not df_mov.empty and "Tipo" in df_mov.columns:
    mask_rg = df_mov["Tipo"].str.contains("topup", case=False, na=False)
    for idx in df_mov[mask_rg].index:
        testo = df_mov.at[idx, "Movimento"]
        if "Ricarica" in testo and "💸" not in testo:
            parti = testo.split("—", 1)  # divido in [RG5,0 , Ricarica...]
            if len(parti) == 2:
                df_mov.at[idx, "Movimento"] = f"{parti[0]} 💸—{parti[1]}"



# ===== CELEBRAZIONI =====
from streamlit_extras.let_it_rain import rain


def celebrate_allwin(g, euro):
    # 5/5 senza cash-out — palloncini + oro
    view = st.session_state.get("view", "")
    selected_day = int(st.session_state.get("fino_a", 0))
    flag = (st.session_state.get("giornata_flag") or {}).get(selected_day) or (giornata_flag or {}).get(selected_day)

    # Mostra solo nella giornata giusta e nelle viste abilitate
    if g != selected_day or flag != "ALL_WIN" or view not in ["filippoide", "classifica", "movimenti"]:
        celebration_box.empty()
        return

    celebration_box.empty()
    with celebration_box.container():
        st.balloons()
        st.markdown(
            f"""
            <div style="position:fixed;left:0;right:0;top:70px;text-align:center;z-index:9999;">
            <div style="color:#FFD700;font-weight:900;font-size:40px;text-shadow:0 0 15px #FFD700">
                THE CHAMPIONS
            </div>
            <div style="color:white;font-size:22px;">
                Giornata {g} — Importo:
                <span style="font-size:26px">{eur(euro)} €</span>
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def celebrate_cashout_allwin(g, euro):
    # Cash-out tutti vincenti — tema verde
    view = st.session_state.get("view", "")
    selected_day = int(st.session_state.get("fino_a", 0))
    flag = (st.session_state.get("giornata_flag") or {}).get(selected_day) or (giornata_flag or {}).get(selected_day)

    if g != selected_day or flag != "CASH_ALL_WIN" or view not in ["filippoide", "classifica", "movimenti"]:
        celebration_box.empty()
        return

    celebration_box.empty()
    with celebration_box.container():
        try:
            rain(emoji="🎉", font_size=48, falling_speed=5, animation_length=2)
            rain(emoji="🪙", font_size=46, falling_speed=6, animation_length=2)
        except Exception:
            pass
        st.markdown(
            f"""
            <div style="position:fixed;left:0;right:0;top:70px;text-align:center;z-index:9999;">
            <div style="color:#00FF00;font-weight:900;font-size:32px;text-shadow:0 0 12px #00FF00">
                TUTTI VINCENTI — CASH OUT
            </div>
            <div style="color:white;font-size:20px;">
                Giornata {g} — Importo:
                <span style="font-size:24px">{eur(euro)} €</span>
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def celebrate_cashout_quasi(g, euro):
    # Cash-out quasi tutti vincenti — argento
    view = st.session_state.get("view", "")
    selected_day = int(st.session_state.get("fino_a", 0))
    flag = (st.session_state.get("giornata_flag") or {}).get(selected_day) or (giornata_flag or {}).get(selected_day)

    if g != selected_day or flag not in ("CASH_POLLO", "CASH_POLLO_FANTASMA") or view not in ["filippoide","classifica", "movimenti"]:
        celebration_box.empty()
        return

    celebration_box.empty()
    with celebration_box.container():
        try:
            rain(emoji="✨", font_size=40, falling_speed=7, animation_length=2)
            rain(emoji="🪙", font_size=46, falling_speed=6, animation_length=2)
        except Exception:
            pass
        st.markdown(
            f"""
            <div style="position:fixed;left:0;right:0;top:70px;text-align:center;z-index:9999;">
            <div style="color:#C0C0C0;font-weight:900;font-size:30px;text-shadow:0 0 10px #C0C0C0">
                CASH OUT — QUASI TUTTI VINCENTI
            </div>
            <div style="color:white;font-size:20px;">
                Giornata {g} — Importo:
                <span style="font-size:24px">{eur(euro)} €</span>
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def celebrate_cashout(g, euro):
    # Cash-out generico — pioggia di banconote
    view = st.session_state.get("view", "")
    selected_day = int(st.session_state.get("fino_a", 0))
    flag = (st.session_state.get("giornata_flag") or {}).get(selected_day) or (giornata_flag or {}).get(selected_day)

    if g != selected_day or not (flag and flag.startswith("CASH_")) or view not in ["filippoide", "classifica", "movimenti"]:
        celebration_box.empty()
        return

    celebration_box.empty()
    with celebration_box.container():
        try:
            rain(emoji="💶", font_size=44, falling_speed=5, animation_length=3)
            rain(emoji="💵", font_size=46, falling_speed=6, animation_length=3)
        except Exception:
            pass
        st.markdown(
            f"""
            <div style="position:fixed;left:0;right:0;top:70px;text-align:center;z-index:9999;">
            <div style="color:#C0C0C0;font-weight:900;font-size:28px;text-shadow:0 0 8px #C0C0C0">
                CASH OUT
            </div>
            <div style="color:white;font-size:18px;">
                Giornata {g} — Importo:
                <span style="font-size:22px">{eur(euro)} €</span>
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )


        # ===== HOME PAGE ELEGANTE (pulsanti colorati + back funzionante) =====
        
st.markdown("""
<style>
/* 🔧 Rimuove ogni spazio superiore globale */
section.main {
    padding-top: 0 !important;
    margin-top: -100px !important;  /* 🔹 solleva tutta la pagina */
}

/* 🔹 Streamlit container principale */
[data-testid="stAppViewContainer"] {
    padding-top: 0 !important;
    margin-top: -100px !important;  /* 🔹 rimuove spazio vuoto nero */
}

/* 🔹 Contenitore interno dei contenuti */
main.block-container {
    padding-top: 0 !important;
    margin-top: -100px !important;
}

/* 🔹 Primo blocco di contenuto */
[data-testid="stAppViewBlockContainer"] > div:first-child {
    margin-top: -100px !important;
}

/* 🔹 Disattiva eventuali margini nei blocchi verticali */
[data-testid="stVerticalBlockBorderWrapper"]:first-child {
    margin-top: -60px !important;
}
</style>
""", unsafe_allow_html=True)


        
st.markdown("""
<style>
/* === Pulsanti Home eleganti, testo MOLTO più grande ma bottone invariato === */
div.stButton > button {
    background: linear-gradient(145deg, #c7a739, #d4af37, #b48e1b) !important;
    color: #000000 !important;
    font-weight: 1000 !important;
    font-size: 2.8rem !important;         /* 🔹 testo molto più grande */
    line-height: 1.1 !important;          /* 🔹 compatta verticalmente il testo */
    white-space: nowrap !important;  
    text-shadow: 1px 1px 2px rgba(255,255,255,0.5);
    border: 2px solid #8a6b00 !important;
    border-radius: 18px !important;
    padding: 0.5rem 0.3rem !important;    /* 🔹 meno spazio interno per non aumentare la dimensione complessiva */
    white-space: nowrap !important;  
    max-width: 250px !important;   
    min-height: 80px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    transition: all 0.25s ease-in-out;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}
div.stButton > button:hover {
    background: linear-gradient(145deg, #e1c85a, #d4af37, #b8961f) !important;
    box-shadow: 0 0 20px rgba(255,215,0,0.8) !important;
    transform: translateY(-3px);
}
div.stButton > button:active {
    transform: translateY(1px);
}


/* === Freccia “Torna alla Home” coerente === */
button[kind="primary"][key="back_btn_home"] {
    background: linear-gradient(145deg, #c7a739, #d4af37, #b48e1b) !important;
    color: #000000 !important;
    font-weight: 1000 !important;
    font-size: 1.9rem !important;
    text-shadow: 1px 1px 2px rgba(255,255,255,0.5);
    border: 2px solid #8a6b00 !important;
    border-radius: 16px !important;
    box-shadow: 0 0 14px rgba(0,0,0,0.4);
    padding: 1rem 1.2rem !important;
    width: 220px !important;
}
button[kind="primary"][key="back_btn_home"]:hover {
    background: linear-gradient(145deg, #e1c85a, #d4af37, #b8961f) !important;
    box-shadow: 0 0 26px rgba(255,215,0,0.8);
}

/* === Ingrandisce anche le emoji all’interno dei pulsanti === */
div.stButton > button span, div.stButton > button {
    font-size: 2.8rem !important;         /* emoji e testo più grandi */
}

</style>
""", unsafe_allow_html=True)


# ===== GESTIONE SCROLLBAR (Home senza scroll, sezioni con scroll) =====
st.markdown("""
<style>

/* Blocca totalmente lo scroll e nasconde la barra nella Home */
[data-testid="stAppViewBlockContainer"] > div:first-child {
    overflow: hidden !important;
    height: 100vh !important;
}

/* Riattiva lo scroll SOLO quando sono visibili i pannelli */
[data-testid="stAppViewBlockContainer"] > div:first-child:has(div.panel) {
    overflow-y: auto !important;
    height: auto !important;
}

/* Nasconde qualsiasi scrollbar residua */
body::-webkit-scrollbar, 
[data-testid="stAppViewBlockContainer"]::-webkit-scrollbar {
    display: none !important;
}

/* Disabilita scroll anche sul body principale */
html, body {
    overflow: hidden !important;
}

</style>
""", unsafe_allow_html=True)


# === Protezione anti-reset view ===
if "view" not in st.session_state:
    st.session_state.view = "classifica"


# ===== ROUTER =====

device = st.session_state.get("device", "unified")

if device == "unified":
    if st.session_state.view == "home":
        # Sottotitolo più vicino al titolo, centrato e con spaziatura armoniosa
        st.markdown(
            "<p style='text-align:center; font-size:1.5rem; color:#d4af37; "
            "font-weight:700; margin-top:-90px; margin-bottom:60px;'>"
            "L'app ufficiale del torneo più goliardico dell'anno 🏆</p>",
            unsafe_allow_html=True
        )


        tiles = [
            {"icon": "📊", "label": "Filippoide", "view": "filippoide"},
            {"icon": "🏆", "label": "KillBet Arena", "view": "classifica"},
            {"icon": "📅", "label": "Giornate", "view": "giornate"},
            {"icon": "📘", "label": "Legenda", "view": "legenda"},
            {"icon": "🐔🦊", "label": "Polli & Volpi", "view": "polli_volpi"},
            {"icon": "💰", "label": "Cassa", "view": "movimenti"},
        ]

        # Mostra i pulsanti in 3x2
        rows = [tiles[:3], tiles[3:]]
        for r_i, row in enumerate(rows):
            cols = st.columns(3)
            for c_i, t in enumerate(row):
                with cols[c_i]:
                    label = f"{t['icon']} {t['label']}"
                    if st.button(label, key=f"home_btn_{r_i}_{c_i}", use_container_width=True):
                        st.session_state.view = t["view"]
                        st.rerun()

        st.markdown(
            "<p style='text-align:center; font-size:1.05rem; color:#cccccc; "
            "margin-top:60px;'>💡 Suggerimento: se sei su smartphone, ruota lo schermo in orizzontale per vedere meglio i grafici.</p>",
            unsafe_allow_html=True
        )


    else:
        # 🔹 Pulsante "Torna alla Home" centrato e funzionante (senza reload)
        # 🔹 Contenitore pulsante: più alto e centrato davvero
        col_back = st.columns([1, 1, 1])
        with col_back[1]:
            st.markdown("<div style='margin-top:-120px;'></div>", unsafe_allow_html=True)  # 🔹 spinge tutto verso l’alto
            if st.button("🔙 Torna alla Home", key="back_btn_home", use_container_width=True):
                st.session_state.view = "home"
                st.rerun()


        # 🔹 CSS compatto e senza barra dorata
        st.markdown("""
        <style>
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border: none !important;
            box-shadow: none !important;
        }
        div.stButton > button[key="back_btn_home"] {
            display: block !important;
            margin-left: auto !important;
            margin-right: auto !important;
            margin-top: -160px !important;   /* 🔹 più alto del precedente */
            margin-bottom: 10px !important;  /* 🔹 meno spazio sotto */

            background: linear-gradient(145deg, #c7a739, #d4af37, #b48e1b) !important;
            color: #000 !important;
            font-weight: 1000 !important;
            font-size: 1.6rem !important;
            border: 2px solid #8a6b00 !important;
            border-radius: 14px !important;
            padding: 0.6rem 1.4rem !important;
            width: 260px !important;
            box-shadow: 0 0 12px rgba(0,0,0,0.45);
            cursor: pointer;
            text-shadow: 1px 1px 2px rgba(255,255,255,0.5);
            transition: all 0.25s ease-in-out;
        }


        </style>
        """, unsafe_allow_html=True)


        # Gestione viste (sezioni)
        v = st.session_state.view
        if v == "filippoide":
            mostra_filipp()
        elif v == "classifica":
            mostra_classifica()
        elif v == "giornate":
            mostra_giornate()
        elif v == "legenda":
            mostra_legenda()
        elif v == "polli_volpi":
            mostra_polli_volpi()
        elif v == "movimenti":
            mostra_movimenti()
