#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
COMMODITIES & FOREX SEASONALITY & MACRO DRIVERS REPORT GENERATOR
=============================================================================
Générateur automatisé de rapports d'analyse de saisonnalité sur devises et commodités
Reprend fidèlement la structure du rapport de référence (AUDJPY 2020-2025)
en y intégrant tous les compléments indispensables pour le trading :
- Saisonnalité par jour de semaine et amplitude moyenne (pips/points)
- Profil composite annuel cumulé (365 jours)
- Moteurs macro et matrice de corrélation intermarchés :
  * DXY (Dollar Index)
  * EUR (Euro - EUR/USD)
  * JPY (Yen - USD/JPY)
  * NZD (Dollar Néozélandais - Sentiment risque / Chine)
  * OR (Gold - XAU/USD / Refuge & Inflation)
  * PÉTROLE (Crude Oil WTI - Énergie & Matières premières)

Auteur: Antigravity / Forex & Commodities Quantitative Engine
=============================================================================
"""

import os
import sys

# Support UTF-8 sur Windows PowerShell/CMD
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import argparse
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
import yfinance as yf

# Configuration graphique soignée et professionnelle
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#B0BEC5'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#ECEFF1'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7

# Charte graphique institutionnelle
COLOR_NAVY = '#1A365D'
COLOR_SLATE = '#2D3748'
COLOR_GREEN = '#2E7D32'
COLOR_RED = '#C62828'
COLOR_ORANGE = '#E65100'
COLOR_BLUE = '#1565C0'
COLOR_PURPLE = '#6A1B9A'
COLOR_BG_BOX = '#F8FAFC'
COLOR_BORDER = '#CFD8DC'

MONTH_NAMES_FR = [
    'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
    'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
]
MONTH_ABBR_FR = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
DAY_NAMES_FR = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi']

# Piliers macro-économiques d'influence mondiale
MACRO_DRIVERS_MAP = {
    'DXY': {'ticker': 'DX-Y.NYB', 'label': 'DXY (Dollar Index)', 'desc': 'Liquidité mondiale & Dollar US'},
    'EUR': {'ticker': 'EURUSD=X', 'label': 'EUR (EUR/USD)', 'desc': 'Poids lourd FX (57.6% DXY)'},
    'JPY': {'ticker': 'USDJPY=X', 'label': 'JPY (USD/JPY)', 'desc': 'Refuge & Carry trade mondial'},
    'NZD': {'ticker': 'NZDUSD=X', 'label': 'NZD (NZD/USD)', 'desc': 'Appétit risque & Océanie/Chine'},
    'OR':  {'ticker': 'GC=F',     'label': 'OR (XAU/USD)', 'desc': 'Refuge & Taux réels/Inflation'},
    'PETROLE': {'ticker': 'CL=F', 'label': 'PÉTROLE (WTI)', 'desc': 'Énergie & Croissance globale'}
}

# Liste par défaut des devises et commodités à analyser
DEFAULT_ASSETS = [
    'AUDJPY', 'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF', 'NZDUSD',
    'EURJPY', 'GBPJPY', 'GOLD', 'SILVER'
]
DEFAULT_BENCHMARK = 'DXY'


def get_asset_info(symbol: str) -> tuple[str, str, float, str]:
    """
    Retourne (ticker_yfinance, display_name, unit_size, unit_label) :
    - Or / Gold : GC=F, OR (XAU/USD), 1.0, 'Points ($)'
    - Argent / Silver : SI=F, ARGENT (XAG/USD), 0.01, 'Cents ($0.01)'
    - Pétrole / Oil : CL=F, PÉTROLE (WTI), 1.0, 'Points ($)'
    - Forex JPY : 0.01, 'Pips'
    - Forex standard : 0.0001, 'Pips'
    """
    s = symbol.upper().replace('/', '').strip()

    if s in ['GOLD', 'OR', 'XAUUSD', 'XAU', 'GC=F']:
        return 'GC=F', "l'OR (XAU/USD)", 1.0, 'Points ($)'
    if s in ['SILVER', 'ARGENT', 'XAGUSD', 'XAG', 'SI=F']:
        return 'SI=F', "l'ARGENT (XAG/USD)", 0.01, 'Cents ($0.01)'
    if s in ['OIL', 'PETROLE', 'WTI', 'CRUDE', 'CL=F']:
        return 'CL=F', 'PÉTROLE WTI', 1.0, 'Points ($)'
    if s in ['COPPER', 'CUIVRE', 'HG=F']:
        return 'HG=F', 'CUIVRE', 0.01, 'Cents'

    special_fx = {
        'USDCAD': 'CAD=X',
        'USDCHF': 'CHF=X',
        'DXY': 'DX-Y.NYB',
        'USDX': 'DX-Y.NYB'
    }
    if s in special_fx:
        ticker = special_fx[s]
    elif s.endswith('=X'):
        ticker = s
    else:
        ticker = f"{s}=X"

    if 'JPY' in s:
        return ticker, f"la paire {s}", 0.01, 'Pips'
    return ticker, f"la paire {s}", 0.0001, 'Pips'


def fetch_macro_drivers(start_date: str, end_date: str) -> pd.DataFrame:
    """Télécharge en une seule fois tous les cours de clôture des 6 piliers macro."""
    print("-> Téléchargement de la matrice des 6 moteurs macro (DXY, EUR, JPY, NZD, OR, PÉTROLE)...")
    driver_closes = {}
    for key, info in MACRO_DRIVERS_MAP.items():
        df = yf.download(info['ticker'], start=start_date, end=end_date, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        c = df['Close'].dropna()
        driver_closes[key] = c

    df_drivers = pd.DataFrame(driver_closes).dropna()
    return df_drivers


def fetch_data(asset: str, benchmark: str, start_date: str, end_date: str):
    """Télécharge les cours journaliers pour l'actif cible et le benchmark."""
    asset_ticker, display_name, unit_size, unit_label = get_asset_info(asset)
    b = benchmark.upper().replace('/', '').strip()
    bm_ticker = 'DX-Y.NYB' if b in ['DXY', 'USDX'] else get_asset_info(b)[0]

    print(f"-> Téléchargement pour {display_name} ({asset_ticker}) et benchmark {benchmark} ({bm_ticker})...")
    df_asset = yf.download(asset_ticker, start=start_date, end=end_date, progress=False)
    df_bm = yf.download(bm_ticker, start=start_date, end=end_date, progress=False)

    if isinstance(df_asset.columns, pd.MultiIndex):
        df_asset.columns = df_asset.columns.get_level_values(0)
    if isinstance(df_bm.columns, pd.MultiIndex):
        df_bm.columns = df_bm.columns.get_level_values(0)

    df_asset = df_asset.dropna(subset=['Close'])
    df_bm = df_bm.dropna(subset=['Close'])

    if df_asset.empty:
        raise ValueError(f"Aucune donnée récupérée pour {asset} ({asset_ticker}).")

    return df_asset, df_bm, display_name, unit_size, unit_label


def analyze_seasonality(df: pd.DataFrame, df_bm: pd.DataFrame, df_drivers: pd.DataFrame,
                        asset: str, benchmark: str, display_name: str, unit_size: float, unit_label: str):
    """Calcule l'ensemble des métriques de saisonnalité et d'analyse intermarchés."""
    data = df.copy()

    # Rendements journaliers et amplitude
    data['Return'] = data['Close'].pct_change()
    data['Range_Units'] = (data['High'] - data['Low']) / unit_size
    data['Year'] = data.index.year
    data['Month'] = data.index.month
    data['DayOfWeek'] = data.index.dayofweek
    data['DayOfYear'] = data.index.dayofyear

    years = sorted(data['Year'].unique())
    nb_years = len(years)

    # 1. Analyse Mensuelle : variation Open -> Close de chaque mois
    monthly_records = []
    for (yr, m), grp in data.groupby(['Year', 'Month']):
        first_open = grp['Open'].iloc[0]
        last_close = grp['Close'].iloc[-1]
        m_ret = (last_close / first_open - 1) * 100
        m_units = (last_close - first_open) / unit_size
        monthly_records.append({
            'Year': yr,
            'Month': m,
            'Return': m_ret,
            'Units': m_units,
            'FirstOpen': first_open,
            'LastClose': last_close
        })
    df_monthly = pd.DataFrame(monthly_records)

    # Tableau résumé mensuel (1 à 12)
    stats_list = []
    for m in range(1, 13):
        m_data = df_monthly[df_monthly['Month'] == m]
        nb_m = len(m_data)
        if nb_m > 0:
            dir_pct = (m_data['Return'] > 0).sum() / nb_m * 100
            mean_ret = m_data['Return'].mean()
            mean_units = m_data['Units'].mean()
            std_ret = m_data['Return'].std(ddof=1) if nb_m > 1 else 0.0
            min_ret = m_data['Return'].min()
            max_ret = m_data['Return'].max()
        else:
            dir_pct = mean_ret = mean_units = std_ret = min_ret = max_ret = 0.0

        stats_list.append({
            'Month_Num': m,
            'Mois': MONTH_NAMES_FR[m - 1],
            'Nb_mois': nb_m,
            'Directional': dir_pct,
            'Mean_Return': mean_ret,
            'Mean_Units': mean_units,
            'Std_Return': std_ret,
            'Min_Return': min_ret,
            'Max_Return': max_ret
        })
    df_stats = pd.DataFrame(stats_list)

    # 2. Analyse par jour de la semaine (Lundi=0 à Vendredi=4)
    weekday_data = data[data['DayOfWeek'] < 5]
    dow_records = []
    for dow in range(5):
        sub_d = weekday_data[weekday_data['DayOfWeek'] == dow]
        d_ret = sub_d['Return'].mean() * 100
        d_units = ((sub_d['Close'] - sub_d['Open']) / unit_size).mean()
        d_wr = (sub_d['Return'] > 0).mean() * 100
        d_range = sub_d['Range_Units'].mean()
        dow_records.append({
            'DayOfWeek': dow,
            'Jour': DAY_NAMES_FR[dow],
            'Mean_Return': d_ret,
            'Mean_Units': d_units,
            'Win_Rate': d_wr,
            'Avg_Range_Units': d_range
        })
    df_dow = pd.DataFrame(dow_records)

    # 3. Profil composite annuel propre (Moyenne cumulative sur 365 jours)
    day_returns = data.groupby([data.index.year, data.index.dayofyear])['Return'].mean().unstack(level=0)
    mean_daily_ret = day_returns.mean(axis=1).reindex(range(1, 366)).fillna(0)
    composite_curve = ((1 + mean_daily_ret).cumprod() - 1) * 100

    # 4. Métriques globales
    total_days = len(data)
    total_ret = (data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100
    ann_ret = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) ** (252 / total_days) - 1) * 100 if total_days > 0 else 0
    ann_vol = data['Return'].std() * np.sqrt(252) * 100
    sharpe = (ann_ret / ann_vol) if ann_vol > 0 else 0.0

    # Max Drawdown
    cum_wealth = (1 + data['Return'].fillna(0)).cumprod()
    running_max = cum_wealth.cummax()
    dd = (cum_wealth - running_max) / running_max
    max_dd = dd.min() * 100

    # 5. Corrélation avec le Benchmark spécifique (ex: DXY)
    merged_bm = pd.concat([data['Return'].rename('Asset'), df_bm['Close'].pct_change().rename('BM')], axis=1).dropna()
    global_corr = merged_bm['Asset'].corr(merged_bm['BM'])
    rolling_corr_60 = merged_bm['Asset'].rolling(60).corr(merged_bm['BM'])

    # Sensibilité en fonction du Benchmark (jours haussiers vs baissiers)
    dxy_up = merged_bm[merged_bm['BM'] > 0]['Asset'].mean() * 100
    dxy_down = merged_bm[merged_bm['BM'] < 0]['Asset'].mean() * 100

    # 6. MOTEURS MACRO : Matrice de corrélation et sensibilité avec les 6 Piliers
    driver_pct = df_drivers.pct_change()
    merged_drivers = pd.concat([data['Return'].rename('Asset'), driver_pct], axis=1).dropna()

    driver_metrics = []
    for d_key, info in MACRO_DRIVERS_MAP.items():
        if d_key in merged_drivers.columns:
            corr_val = merged_drivers['Asset'].corr(merged_drivers[d_key])
            up_mean = merged_drivers[merged_drivers[d_key] > 0]['Asset'].mean() * 100
            down_mean = merged_drivers[merged_drivers[d_key] < 0]['Asset'].mean() * 100
            roll_s = merged_drivers['Asset'].rolling(60).corr(merged_drivers[d_key])

            driver_metrics.append({
                'Key': d_key,
                'Label': info['label'],
                'Desc': info['desc'],
                'Corr': corr_val,
                'UpMean': up_mean,
                'DownMean': down_mean,
                'Rolling60': roll_s
            })

    df_macro_stats = pd.DataFrame(driver_metrics)

    # 7. Classification automatique des mois
    bullish_months = []
    bearish_months = []
    neutral_months = []

    for _, row in df_stats.iterrows():
        m_num = int(row['Month_Num'])
        m_name = row['Mois']
        d_pct = row['Directional']
        m_ret = row['Mean_Return']
        m_unit = row['Mean_Units']
        s_ret = row['Std_Return']
        pts = df_monthly[df_monthly['Month'] == m_num]['Return'].values

        if (d_pct >= 66.0 and m_ret > 0.4) or (d_pct >= 80.0 and m_ret > 0):
            stability_score = m_ret / (s_ret + 0.001) * (d_pct / 100.0)
            bullish_months.append({
                'Mois': m_name,
                'Directional': d_pct,
                'Mean_Return': m_ret,
                'Mean_Units': m_unit,
                'Std_Return': s_ret,
                'Score': stability_score,
                'Points': pts
            })
        elif d_pct <= 40.0 or (d_pct <= 50.0 and m_ret < -0.4):
            bearish_months.append({
                'Mois': m_name,
                'Directional': d_pct,
                'Mean_Return': m_ret,
                'Mean_Units': m_unit,
                'Std_Return': s_ret,
                'Points': pts
            })
        else:
            neutral_months.append({
                'Mois': m_name,
                'Directional': d_pct,
                'Mean_Return': m_ret,
                'Mean_Units': m_unit,
                'Std_Return': s_ret,
                'Points': pts
            })

    bullish_months.sort(key=lambda x: x['Score'], reverse=True)
    bearish_months.sort(key=lambda x: x['Mean_Return'])

    return {
        'data': data,
        'df_monthly': df_monthly,
        'df_stats': df_stats,
        'df_dow': df_dow,
        'composite_curve': composite_curve,
        'total_ret': total_ret,
        'ann_ret': ann_ret,
        'ann_vol': ann_vol,
        'sharpe': sharpe,
        'max_dd': max_dd,
        'global_corr': global_corr,
        'rolling_corr_60': rolling_corr_60,
        'dxy_up': dxy_up,
        'dxy_down': dxy_down,
        'unit_size': unit_size,
        'unit_label': unit_label,
        'display_name': display_name,
        'years': years,
        'nb_years': nb_years,
        'bullish_months': bullish_months,
        'bearish_months': bearish_months,
        'neutral_months': neutral_months,
        'df_macro_stats': df_macro_stats,
        'merged_drivers': merged_drivers
    }


# =============================================================================
# RENDU DES PAGES DU RAPPORT PDF (5 PAGES HAUTE DÉFINITION)
# =============================================================================

def render_page_1(pdf: PdfPages, asset: str, benchmark: str, analysis: dict, start_yr: int, end_yr: int):
    """Page 1 : Contexte brut, Gain/Perte moyen par mois & Nuage de points des retours."""
    fig = plt.figure(figsize=(8.27, 11.69), dpi=200)
    gs = gridspec.GridSpec(3, 1, height_ratios=[0.6, 1.2, 1.2], hspace=0.35, top=0.95, bottom=0.06, left=0.10, right=0.90)

    disp_name = analysis['display_name']
    u_label = analysis['unit_label']

    ax_hdr = fig.add_subplot(gs[0])
    ax_hdr.axis('off')
    ax_hdr.text(0.5, 0.90, f"Rapport d'analyse sur la Saisonnalité de\n{disp_name} ({start_yr} – {end_yr})",
                fontsize=16, weight='bold', color=COLOR_NAVY, ha='center', va='top', linespacing=1.3)
    ax_hdr.text(0.5, 0.45, f"Période {start_yr}-{end_yr}  |  Indice de référence : {benchmark.upper()}",
                fontsize=11, color='#4A5568', ha='center')
    ax_hdr.text(0.5, 0.25, f"Période analysée : {analysis['nb_years']*12} mois ({MONTH_NAMES_FR[0].lower()} {start_yr} à {MONTH_NAMES_FR[-1].lower()} {end_yr}) soit {analysis['nb_years']} ans",
                fontsize=9.5, color='#718096', ha='center')

    ax_hdr.text(0.0, -0.05, "1. Contexte des données (avant toute analyse)", fontsize=11, weight='bold', color=COLOR_SLATE)
    ax_hdr.text(0.0, -0.22, "Les graphiques et le tableau ci-dessous constituent le contexte brut.", fontsize=9.5, color='#4A5568')

    # Graphique 1 : Gain/Perte moyen par mois
    ax_g1 = fig.add_subplot(gs[1])
    units = analysis['df_stats']['Mean_Units'].values
    colors = [COLOR_GREEN if u >= 0 else COLOR_RED for u in units]
    bars = ax_g1.bar(range(1, 13), units, color=colors, width=0.6, edgecolor='#374151', linewidth=0.5)
    ax_g1.axhline(0, color='black', linewidth=0.8, linestyle='--')
    ax_g1.set_title(f"Graphique 1 : {u_label} moyen par mois ({asset.upper()})", fontsize=11, weight='bold', color=COLOR_SLATE, pad=10)
    ax_g1.set_ylabel(f"Moyenne ({u_label})", fontsize=9.5)
    ax_g1.set_xticks(range(1, 13))
    ax_g1.set_xticklabels(MONTH_NAMES_FR, fontsize=8, rotation=35, ha='right')

    for b in bars:
        h = b.get_height()
        va_align = 'bottom' if h >= 0 else 'top'
        y_offset = (3 if h >= 0 else -10)
        ax_g1.annotate(f"{h:+.1f}", xy=(b.get_x() + b.get_width() / 2, h),
                       xytext=(0, y_offset), textcoords="offset points",
                       ha='center', va=va_align, fontsize=8, weight='bold',
                       color=COLOR_GREEN if h >= 0 else COLOR_RED)

    # Graphique 2 : Nuage de points des retours mensuels (%)
    ax_g2 = fig.add_subplot(gs[2])
    ax_g2.set_title(f"Graphique 2 : Nuage de points des retours mensuels (%) pour {asset.upper()} ({start_yr}-{end_yr})",
                    fontsize=10.5, weight='bold', color=COLOR_SLATE, pad=10)
    ax_g2.set_ylabel("Retour mensuel (%)", fontsize=9.5)
    ax_g2.set_xticks(range(1, 13))
    ax_g2.set_xticklabels(MONTH_NAMES_FR, fontsize=8, rotation=35, ha='right')
    ax_g2.axhline(0, color='black', linewidth=0.8, linestyle='--')

    df_m = analysis['df_monthly']
    for _, row in df_m.iterrows():
        m = int(row['Month'])
        yr = int(row['Year'])
        ret = row['Return']
        ax_g2.scatter(m, ret, color=COLOR_BLUE, alpha=0.75, s=28, edgecolors='#0D47A1', zorder=4)
        ax_g2.annotate(f"'{str(yr)[-2:]}", xy=(m, ret), xytext=(4, -2), textcoords="offset points",
                       fontsize=6.5, color='#374151', weight='bold')

    pdf.savefig(fig)
    plt.close(fig)


def render_page_2(pdf: PdfPages, asset: str, analysis: dict, start_yr: int, end_yr: int):
    """Page 2 : Distribution mensuelle (Boxplots) et Tableau statistique de saisonnalité."""
    fig = plt.figure(figsize=(8.27, 11.69), dpi=200)
    gs = gridspec.GridSpec(2, 1, height_ratios=[1.1, 1.3], hspace=0.35, top=0.94, bottom=0.06, left=0.08, right=0.92)

    u_label = analysis['unit_label']

    # Graphique 3 : Boxplot des distributions
    ax_box = fig.add_subplot(gs[0])
    monthly_data = [analysis['df_monthly'][analysis['df_monthly']['Month'] == m]['Return'].values for m in range(1, 13)]
    
    bp = ax_box.boxplot(monthly_data, patch_artist=True, tick_labels=MONTH_NAMES_FR, widths=0.55,
                        medianprops=dict(color='#D32F2F', linewidth=1.5),
                        boxprops=dict(facecolor='#E3F2FD', edgecolor=COLOR_BLUE, linewidth=1.0),
                        whiskerprops=dict(color='#546E7A', linewidth=1.0),
                        capprops=dict(color='#546E7A', linewidth=1.0),
                        flierprops=dict(marker='o', markerfacecolor='#D32F2F', markeredgecolor='black', markersize=4.5))

    ax_box.axhline(0, color='black', linewidth=0.8, linestyle='--')
    ax_box.set_title(f"Graphique 3 : Distribution mensuelle des retours (%) pour {asset.upper()} ({start_yr}-{end_yr})",
                     fontsize=10.5, weight='bold', color=COLOR_SLATE, pad=10)
    ax_box.set_ylabel("Retour mensuel (%)", fontsize=9.5)
    ax_box.set_xticklabels(MONTH_NAMES_FR, fontsize=8, rotation=35, ha='right')

    # Tableau de saisonnalité complet
    ax_tbl = fig.add_subplot(gs[1])
    ax_tbl.axis('off')
    ax_tbl.set_title(f"Tableau de saisonnalité {asset.upper()} ({start_yr} -> {end_yr})",
                     fontsize=11, weight='bold', color=COLOR_NAVY, pad=12, loc='left')

    df_s = analysis['df_stats']
    table_data = []
    header_unit = 'Mean_Pips' if 'Pips' in u_label else 'Mean_Points'
    headers = ['Mois', 'Nb_mois', 'Directional', 'Mean_Return', header_unit, 'Std_Return']
    for idx, row in df_s.iterrows():
        table_data.append([
            row['Mois'],
            str(int(row['Nb_mois'])),
            f"{row['Directional']:.1f} %",
            f"{row['Mean_Return']:+.3f} %",
            f"{row['Mean_Units']:+.1f}",
            f"{row['Std_Return']:.3f} %"
        ])

    tbl = ax_tbl.table(cellText=table_data, colLabels=headers, loc='center', cellLoc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8.5)
    tbl.scale(1.0, 1.55)

    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor(COLOR_BORDER)
        if r == 0:
            cell.set_facecolor(COLOR_NAVY)
            cell.set_text_props(color='white', weight='bold')
        else:
            cell.set_facecolor('#F8FAFC' if r % 2 == 0 else 'white')
            if c == 2:
                val = df_s.iloc[r - 1]['Directional']
                if val >= 66.0: cell.set_text_props(color=COLOR_GREEN, weight='bold')
                elif val <= 34.0: cell.set_text_props(color=COLOR_RED, weight='bold')
            elif c == 3:
                val = df_s.iloc[r - 1]['Mean_Return']
                cell.set_text_props(color=COLOR_GREEN if val >= 0 else COLOR_RED, weight='bold')
            elif c == 4:
                val = df_s.iloc[r - 1]['Mean_Units']
                cell.set_text_props(color=COLOR_GREEN if val >= 0 else COLOR_RED, weight='bold')

    pdf.savefig(fig)
    plt.close(fig)


def render_page_3(pdf: PdfPages, asset: str, analysis: dict, start_yr: int, end_yr: int):
    """Page 3 : Définition des termes, Analyse et Interprétation automatisée des mois."""
    fig = plt.figure(figsize=(8.27, 11.69), dpi=200)
    ax = fig.add_axes([0.08, 0.05, 0.84, 0.90])
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    disp_name = analysis['display_name']
    u_label = analysis['unit_label']

    y = 0.98
    ax.text(0.0, y, "2. Définition des termes importants (utilisés dans l'analyse)",
            fontsize=11, weight='bold', color=COLOR_NAVY, va='top')
    y -= 0.035

    definitions = [
        ("Directionnel (Directional)", f"Pourcentage de mois positifs sur les {analysis['nb_years']} années observées (ex. : 100 % = tous les mois de ce type ont été haussiers)."),
        ("Dispersion (Std_Return)", "Écart-type des retours mensuels en %. Plus la valeur est faible, plus la performance est stable et prévisible (faible risque saisonnier)."),
        ("Retour moyen (Mean_Return)", "Moyenne des performances mensuelles en pourcentage."),
        (f"Variation moyenne ({u_label})", f"Gain ou perte moyen en {u_label.lower()} (unité de mouvement de {disp_name})."),
        ("Distribution (boxplot & nuage de points)", "Visualisation de la répartition réelle des retours (médiane, dispersion, outliers) pour croiser avec les moyennes du tableau.")
    ]

    for term, desc in definitions:
        ax.text(0.0, y, f"• {term} :", fontsize=8.5, weight='bold', color=COLOR_SLATE, va='top')
        ax.text(0.02, y - 0.016, desc, fontsize=8.2, color='#4A5568', va='top')
        y -= 0.040

    y -= 0.010
    ax.plot([0.0, 1.0], [y, y], color=COLOR_BORDER, lw=0.8)
    y -= 0.025

    ax.text(0.0, y, "3. Analyse et Interprétation des mois intéressants à traiter",
            fontsize=11, weight='bold', color=COLOR_NAVY, va='top')
    y -= 0.025
    intro_txt = ("Nous croisons maintenant les 3 graphiques + le tableau pour identifier les mois qui présentent un signal\n"
                 "saisonnier clair (forte directionnalité + retour élevé + dispersion contrôlée ou, au contraire, forte tendance baissière).")
    ax.text(0.0, y, intro_txt, fontsize=8.5, color='#4A5568', linespacing=1.3, va='top')
    y -= 0.048

    # Mois Haussiers
    ax.text(0.0, y, "A. Mois Haussiers Remarquables (Opportunités d'achat)", fontsize=10, weight='bold', color=COLOR_GREEN, va='top')
    y -= 0.025

    bulls = analysis['bullish_months']
    if bulls:
        for idx, m in enumerate(bulls[:3]):
            pts = m['Points']
            outliers_neg = [p for p in pts if p < 0]
            outlier_txt = "aucun outlier négatif" if not outliers_neg else f"{len(outliers_neg)} seul(s) mois baissier(s)"
            box_bg = '#F1F8E9' if idx == 0 else '#F8FAFC'
            border_col = COLOR_GREEN if idx == 0 else COLOR_BORDER

            text_content = (
                f"Rang {idx+1} : {m['Mois']}  —  {m['Directional']:.1f}% directionnel\n"
                f"• Gain moyen : {m['Mean_Return']:+.2f}% ({m['Mean_Units']:+.1f} {u_label.lower()})  |  Dispersion : {m['Std_Return']:.2f}%\n"
                f"• Nuage de points : {outlier_txt} (min {pts.min():+.1f}%, max {pts.max():+.1f}%)\n"
                f"• Signal croisé : Forte régularité historique favorable aux positions acheteuses."
            )
            ax.text(0.01, y, text_content, fontsize=7.8, color='#1A202C', linespacing=1.3, va='top',
                    bbox=dict(boxstyle='square,pad=0.5', facecolor=box_bg, edgecolor=border_col, linewidth=0.8))
            y -= 0.082
    else:
        ax.text(0.02, y, "Aucun mois ne dépasse le seuil strict de directionnalité haussière (>= 66%).",
                fontsize=8.5, color='#718096', va='top')
        y -= 0.035

    y -= 0.010
    # Mois Baissiers
    ax.text(0.0, y, "B. Mois Baissiers ou Défavorables (Risque de baisse ou opportunité vendeuse)",
            fontsize=10, weight='bold', color=COLOR_RED, va='top')
    y -= 0.025

    bears = analysis['bearish_months']
    if bears:
        for idx, m in enumerate(bears[:2]):
            pts = m['Points']
            text_content = (
                f"{m['Mois']}  —  {m['Directional']:.1f}% directionnel seulement\n"
                f"• Perte moyenne : {m['Mean_Return']:+.2f}% ({m['Mean_Units']:+.1f} {u_label.lower()})  |  Dispersion : {m['Std_Return']:.2f}%\n"
                f"• Nuage de points : Pire mois observé {pts.min():+.2f}% (max {pts.max():+.2f}%)\n"
                f"• Signal croisé : Biais nettement vendeur / Prudence accrue sur les achats."
            )
            ax.text(0.01, y, text_content, fontsize=7.8, color='#1A202C', linespacing=1.3, va='top',
                    bbox=dict(boxstyle='square,pad=0.5', facecolor='#FFEBEE', edgecolor='#FFCDD2', linewidth=0.8))
            y -= 0.082
    else:
        ax.text(0.02, y, "Aucun mois ne présente de tendance baissière marquée récurrente.",
                fontsize=8.5, color='#718096', va='top')
        y -= 0.035

    y -= 0.010
    # Mois Neutres
    ax.text(0.0, y, "C. Mois Neutres ou Peu Exploitables", fontsize=10, weight='bold', color='#455A64', va='top')
    y -= 0.025
    neutrals = analysis['neutral_months']
    n_names = ", ".join([m['Mois'] for m in neutrals])
    neutral_txt = (
        f"• Mois concernés : {n_names if n_names else 'Aucun'}.\n"
        f"• Caractéristique : Directionnalité proche de 50 % ou retours moyens proches de 0.\n"
        f"• Recommandation : Pas d'avantage statistique évident ; privilégier l'analyse technique court terme."
    )
    ax.text(0.01, y, neutral_txt, fontsize=8.0, color='#2D3748', linespacing=1.35, va='top',
            bbox=dict(boxstyle='square,pad=0.5', facecolor='#F5F5F5', edgecolor=COLOR_BORDER, linewidth=0.8))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    pdf.savefig(fig)
    plt.close(fig)


def render_page_4(pdf: PdfPages, asset: str, benchmark: str, analysis: dict, start_yr: int, end_yr: int):
    """Page 4 : Saisonnalité Hebdomadaire, Amplitude en Pips/Points & Profil Composite Annuel."""
    fig = plt.figure(figsize=(8.27, 11.69), dpi=200)
    gs = gridspec.GridSpec(4, 2, height_ratios=[0.45, 1.1, 1.1, 1.1], hspace=0.38, wspace=0.25,
                           top=0.95, bottom=0.06, left=0.09, right=0.91)

    disp_name = analysis['display_name']
    u_label = analysis['unit_label']

    ax_hdr = fig.add_subplot(gs[0, :])
    ax_hdr.axis('off')
    ax_hdr.text(0.0, 0.85, f"4. Analyse Hebdomadaire & Profil Annuel de {disp_name}",
                fontsize=13, weight='bold', color=COLOR_NAVY)
    ax_hdr.text(0.0, 0.30, "Dynamique des séances du Lundi au Vendredi et trajectoire cumulée annuelle.",
                fontsize=9.5, color='#4A5568')

    # Graphique : Rendement moyen par jour de semaine
    ax_dow_ret = fig.add_subplot(gs[1, 0])
    df_dow = analysis['df_dow']
    d_rets = df_dow['Mean_Return'].values
    d_cols = [COLOR_GREEN if r >= 0 else COLOR_RED for r in d_rets]
    bars_d = ax_dow_ret.bar(DAY_NAMES_FR, d_rets, color=d_cols, width=0.55, edgecolor='#374151', linewidth=0.5)
    ax_dow_ret.axhline(0, color='black', linewidth=0.8, linestyle='--')
    ax_dow_ret.set_title("Rendement moyen par jour (%)", fontsize=9.5, weight='bold', color=COLOR_SLATE)
    for b in bars_d:
        h = b.get_height()
        ax_dow_ret.annotate(f"{h:+.2f}%", xy=(b.get_x() + b.get_width() / 2, h),
                            xytext=(0, 2 if h >= 0 else -9), textcoords="offset points",
                            ha='center', fontsize=7.5, weight='bold')

    # Graphique : Amplitude moyenne journalière (Pips/Points)
    ax_dow_rng = fig.add_subplot(gs[1, 1])
    ranges = df_dow['Avg_Range_Units'].values
    bars_rng = ax_dow_rng.bar(DAY_NAMES_FR, ranges, color=COLOR_BLUE, width=0.55, edgecolor='#0D47A1', linewidth=0.5)
    ax_dow_rng.set_title(f"Amplitude moyenne par jour ({u_label})", fontsize=9.5, weight='bold', color=COLOR_SLATE)
    for b in bars_rng:
        h = b.get_height()
        ax_dow_rng.annotate(f"{h:.1f}", xy=(b.get_x() + b.get_width() / 2, h),
                            xytext=(0, 2), textcoords="offset points",
                            ha='center', fontsize=7.5, weight='bold')

    # Graphique : Profil Composite Annuel Cumulé (1 Jan -> 31 Déc)
    ax_comp = fig.add_subplot(gs[2, :])
    curve = analysis['composite_curve']
    ax_comp.plot(curve.index, curve.values, color=COLOR_NAVY, linewidth=2.0, label=f"Trajectoire moyenne {asset.upper()} (1 Jan - 31 Déc)")
    ax_comp.fill_between(curve.index, 0, curve.values, color=COLOR_BLUE, alpha=0.12)
    ax_comp.axhline(0, color='black', linewidth=0.8, linestyle='--')
    ax_comp.set_title("Profil Saisonnier Composite Annuel (Moyenne cumulative sur 365 jours)", fontsize=10, weight='bold', color=COLOR_SLATE)
    ax_comp.set_ylabel("Progression moyenne (%)", fontsize=9)
    ax_comp.set_xlim(1, 365)
    month_days = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    ax_comp.set_xticks(month_days)
    ax_comp.set_xticklabels(MONTH_ABBR_FR, fontsize=8)
    ax_comp.legend(loc='upper left', fontsize=8.5, frameon=True)

    # Graphique : Corrélation mobile 60j avec Benchmark (DXY)
    ax_corr = fig.add_subplot(gs[3, 0])
    rc = analysis['rolling_corr_60'].dropna()
    ax_corr.plot(rc.index, rc.values, color=COLOR_ORANGE, linewidth=1.2, label="Corrélation 60j")
    ax_corr.axhline(0, color='black', linewidth=0.7, linestyle='--')
    ax_corr.axhline(analysis['global_corr'], color='#2D3748', linewidth=1.0, linestyle=':',
                    label=f"Moyenne globale ({analysis['global_corr']:+.2f})")
    ax_corr.set_ylim(-1.05, 1.05)
    ax_corr.set_title(f"Corrélation mobile 60j avec {benchmark.upper()}", fontsize=9.5, weight='bold', color=COLOR_SLATE)
    ax_corr.legend(loc='lower left', fontsize=7.5, frameon=True)
    ax_corr.tick_params(axis='x', labelsize=8)

    # Synthèse de la page 4
    ax_syn = fig.add_subplot(gs[3, 1])
    ax_syn.axis('off')
    ax_syn.set_title(f"Règles Intra-Semaine & Dollar", fontsize=9.5, weight='bold', color=COLOR_NAVY, pad=8)

    corr_text = "Négative forte" if analysis['global_corr'] < -0.4 else "Positive forte" if analysis['global_corr'] > 0.4 else "Modérée / Neutre"
    best_dow = df_dow.loc[df_dow['Mean_Return'].idxmax(), 'Jour']
    most_volatile_dow = df_dow.loc[df_dow['Avg_Range_Units'].idxmax(), 'Jour']

    rules = [
        f"• Corrélation {benchmark.upper()} : {analysis['global_corr']:+.2f} ({corr_text})",
        f"• Quand {benchmark.upper()} monte : {asset.upper()} fait {analysis['dxy_up']:+.2f}% /jour",
        f"• Quand {benchmark.upper()} baisse : {asset.upper()} fait {analysis['dxy_down']:+.2f}% /jour",
        f"• Jour le plus haussier : {best_dow} ({df_dow['Mean_Return'].max():+.2f}%)",
        f"• Jour d'amplitude max : {most_volatile_dow} ({df_dow['Avg_Range_Units'].max():.1f} {u_label.lower()})",
        f"• Règle : Privilégier les trades dans le sens du profil composite."
    ]

    y_t = 0.90
    for r in rules:
        ax_syn.text(0.0, y_t, r, fontsize=8.2, color='#2D3748')
        y_t -= 0.16

    pdf.savefig(fig)
    plt.close(fig)


def render_page_5(pdf: PdfPages, asset: str, analysis: dict, start_yr: int, end_yr: int):
    """
    Page 5 : Matrice des 6 Moteurs Macro-Économiques d'Influence Intermarchés
    Analyse systématique face aux 6 baromètres : DXY, EUR, JPY, NZD, OR, PÉTROLE.
    """
    fig = plt.figure(figsize=(8.27, 11.69), dpi=200)
    gs = gridspec.GridSpec(3, 1, height_ratios=[0.45, 1.25, 1.45], hspace=0.38, top=0.95, bottom=0.06, left=0.20, right=0.92)

    disp_name = analysis['display_name']
    df_m = analysis['df_macro_stats']

    # 1. En-tête Page 5
    ax_hdr = fig.add_subplot(gs[0])
    ax_hdr.axis('off')
    ax_hdr.text(-0.14, 0.85, f"5. Baromètres Macro & Corrélations Intermarchés",
                fontsize=13, weight='bold', color=COLOR_NAVY)
    ax_hdr.text(-0.14, 0.35, f"Croisement de {disp_name} avec les 6 grands moteurs mondiaux : DXY, EUR, JPY, NZD, OR, PÉTROLE.",
                fontsize=9.2, color='#4A5568')

    # 2. Graphique 5 : Bar Chart Horizontal des Corrélations avec les 6 Piliers Macro
    ax_bar = fig.add_subplot(gs[1])
    labels = df_m['Label'].values
    corrs = df_m['Corr'].values
    bar_colors = [COLOR_GREEN if c >= 0 else COLOR_RED for c in corrs]

    y_positions = np.arange(len(labels))
    bars = ax_bar.barh(y_positions, corrs, color=bar_colors, height=0.52, edgecolor='#374151', linewidth=0.5)
    ax_bar.axvline(0, color='black', linewidth=0.8, linestyle='--')
    ax_bar.set_yticks(y_positions)
    ax_bar.set_yticklabels(labels, fontsize=8.5, weight='bold', color=COLOR_SLATE)
    ax_bar.set_xlim(-1.15, 1.15)
    ax_bar.set_xlabel("Coefficient de corrélation de Pearson (2020-2025)", fontsize=8.5)
    ax_bar.set_title(f"Graphique 5 : Degré de corrélation de {asset.upper()} avec les 6 piliers macro",
                     fontsize=10, weight='bold', color=COLOR_SLATE, pad=10)

    for b, c_val in zip(bars, corrs):
        width = b.get_width()
        x_pos = width + (0.04 if width >= 0 else -0.13)
        ax_bar.annotate(f"{c_val:+.2f}", xy=(x_pos, b.get_y() + b.get_height() / 2),
                        va='center', fontsize=8.0, weight='bold',
                        color=COLOR_GREEN if c_val >= 0 else COLOR_RED)

    # 3. Tableau de Sensibilité & Rôle Stratégique des 6 Piliers
    ax_tbl_area = fig.add_subplot(gs[2])
    ax_tbl_area.axis('off')

    table_data = []
    headers = ['Pilier Macro', 'Rôle Économique', 'Corrélation', 'Si Pilier Monte', 'Si Pilier Baisse']
    for idx, row in df_m.iterrows():
        table_data.append([
            row['Label'],
            row['Desc'],
            f"{row['Corr']:+.2f}",
            f"{row['UpMean']:+.2f}% /jour",
            f"{row['DownMean']:+.2f}% /jour"
        ])

    col_widths = [0.22, 0.32, 0.14, 0.16, 0.16]
    tbl = ax_tbl_area.table(cellText=table_data, colLabels=headers, colWidths=col_widths, loc='upper center', cellLoc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(7.8)
    tbl.scale(1.0, 1.45)

    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor(COLOR_BORDER)
        if r == 0:
            cell.set_facecolor(COLOR_NAVY)
            cell.set_text_props(color='white', weight='bold')
        else:
            cell.set_facecolor('#F8FAFC' if r % 2 == 0 else 'white')
            if c == 2:
                v = df_m.iloc[r - 1]['Corr']
                cell.set_text_props(color=COLOR_GREEN if v >= 0 else COLOR_RED, weight='bold')

    # Cartouche de Synthèse Macro en bas de page
    best_driver = df_m.loc[df_m['Corr'].idxmax()]
    worst_driver = df_m.loc[df_m['Corr'].idxmin()]

    macro_insights = (
        f"SYNTHÈSE OPÉRATIONNELLE DES MOTEURS INTERMARCHÉS :\n"
        f"• Premier Moteur Positif : {best_driver['Label']} ({best_driver['Corr']:+.2f}) -> {disp_name} fait {best_driver['UpMean']:+.2f}% /jour quand il monte.\n"
        f"• Premier Moteur Inverse : {worst_driver['Label']} ({worst_driver['Corr']:+.2f}) -> {disp_name} fait {worst_driver['UpMean']:+.2f}% /jour quand il monte.\n"
        f"• Filtre de confirmation : Ne jamais entrer sur un signal saisonnier si les deux moteurs dominants divergent fortement.\n"
        f"• Rôle Clé : Le DXY pilote le dollar, l'Or pilote l'inflation/refuge, le Pétrole pilote l'énergie/matières premières."
    )

    ax_tbl_area.text(-0.12, 0.22, macro_insights, fontsize=7.8, color='#1A202C', linespacing=1.35, va='top',
                     bbox=dict(boxstyle='square,pad=0.6', facecolor='#F1F8E9', edgecolor=COLOR_GREEN, linewidth=0.8))

    pdf.savefig(fig)
    plt.close(fig)


def generate_single_report(asset: str, benchmark: str, df_drivers: pd.DataFrame,
                           start_date: str, end_date: str, output_dir: str):
    """Génère le rapport PDF complet de 5 pages pour un actif donné."""
    os.makedirs(output_dir, exist_ok=True)
    start_yr = int(start_date[:4])
    end_yr = int(end_date[:4])

    asset_clean = asset.upper().replace('/', '').replace('=F', '').replace('=X', '')
    pdf_filename = f"Rapport_Saisonnalite_{asset_clean}_{start_yr}_{end_yr}.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)

    df_asset, df_bm, display_name, unit_size, unit_label = fetch_data(asset, benchmark, start_date, end_date)
    analysis = analyze_seasonality(df_asset, df_bm, df_drivers, asset_clean, benchmark, display_name, unit_size, unit_label)

    print(f"[+] Création du rapport PDF (5 pages) pour {display_name}...")
    with PdfPages(pdf_path) as pdf:
        # Page 1 : Contexte brut, Pips/Points moyen par mois, Nuage de points
        render_page_1(pdf, asset_clean, benchmark, analysis, start_yr, end_yr)
        # Page 2 : Boxplots & Tableau complet de saisonnalité
        render_page_2(pdf, asset_clean, analysis, start_yr, end_yr)
        # Page 3 : Définitions & Interprétation croisée (Mois haussiers/baissiers/neutres)
        render_page_3(pdf, asset_clean, analysis, start_yr, end_yr)
        # Page 4 : Saisonnalité Hebdomadaire, Amplitude & Profil Composite Annuel
        render_page_4(pdf, asset_clean, benchmark, analysis, start_yr, end_yr)
        # Page 5 : Matrice des 6 Moteurs Macro (DXY, EUR, JPY, NZD, OR, PÉTROLE)
        render_page_5(pdf, asset_clean, analysis, start_yr, end_yr)

    print(f"[OK] Rapport enregistré avec succès : {pdf_path}")
    return pdf_path


def main():
    parser = argparse.ArgumentParser(description="Générateur de rapports de saisonnalité Forex & Commodités PDF")
    parser.add_argument('--pairs', '--assets', dest='assets', nargs='+', default=DEFAULT_ASSETS,
                        help=f"Actifs à analyser (Devises Forex ou Commodités comme GOLD, SILVER, WTI).")
    parser.add_argument('--benchmark', type=str, default=DEFAULT_BENCHMARK,
                        help=f"Indice de référence dollar / benchmark (défaut: {DEFAULT_BENCHMARK})")
    parser.add_argument('--start', type=str, default='2020-01-01',
                        help="Date de début (AAAA-MM-JJ)")
    parser.add_argument('--end', type=str, default='2025-12-31',
                        help="Date de fin (AAAA-MM-JJ)")
    parser.add_argument('--output_dir', type=str, default='./rapports_pdf',
                        help="Dossier de sortie des rapports PDF")

    args = parser.parse_args()

    print("=" * 70)
    print("GÉNÉRATEUR DE RAPPORTS SAISONNALITÉ FOREX & COMMODITÉS")
    print(f"Actifs : {args.assets}")
    print(f"Benchmark : {args.benchmark}")
    print(f"Période : {args.start} -> {args.end}")
    print(f"Dossier de sortie : {os.path.abspath(args.output_dir)}")
    print("=" * 70)

    # Téléchargement préalable unique des 6 moteurs macro
    df_drivers = fetch_macro_drivers(args.start, args.end)

    success_count = 0
    for asset in args.assets:
        try:
            generate_single_report(asset, args.benchmark, df_drivers, args.start, args.end, args.output_dir)
            success_count += 1
        except Exception as e:
            print(f"[!] Erreur lors de la génération pour {asset} : {e}")

    print("=" * 70)
    print(f"Terminé : {success_count}/{len(args.assets)} rapports générés avec succès.")
    print("=" * 70)


if __name__ == '__main__':
    main()
