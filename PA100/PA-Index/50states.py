import os
import pickle
import pandas as pd
import warnings
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")


stock_split = {
    'NYCB': ['2024-07-12', 1/3],
    'WRB': ['2024-07-11', 1.5/1],
    'FRES': ['2024-07-10', 1/10],
    'WSM': ['2024-07-09', 2/1],
    'IONM': ['2024-07-09', 1/18],
    'EFSH': ['2024-07-08', 1/13],
    'CJET': ['2024-07-08', 1/30],
    'SNFCA': ['2024-07-05', 1.05/1],
    'PHIO': ['2024-07-05', 1/9],
    'CYN': ['2024-07-05', 1/100],
    'NUTX': ['2024-07-03', 1/10],
    'MDRR': ['2024-07-03', 1/2],
    'JZXN': ['2024-07-03', 1/13],
    'ASLN': ['2024-07-03', 1/8],
    'ASST': ['2024-07-02', 1/5],
    'YGMZ': ['2024-07-01', 1/5],
    'RELI': ['2024-07-01', 1/17],
    'KORE': ['2024-07-01', 1/5],
    'DARE': ['2024-07-01', 1/12],
    'AZTR': ['2024-07-01', 1/30],
    'NUWE': ['2024-06-28', 1/35],
    'YYAI': ['2024-06-27', 1/20],
    'RIGL': ['2024-06-27', 1/10],
    'STAF': ['2024-06-26', 1/10],
    'OMIC': ['2024-06-26', 1/30],
    'CMG': ['2024-06-26', 50/1],
    'WBTN': ['2024-06-25', 30/1],
    'NKLA': ['2024-06-25', 1/30],
    'CRKN': ['2024-06-25', 1/149.93],
    'BBSI': ['2024-06-24', 4/1],
    'TECX': ['2024-06-21', 1/12],
    'QLI': ['2024-06-21', 1/5],
    'BJD': ['2024-06-20', 1/8],
    'ATRA': ['2024-06-20', 1/25],
    'ALMS': ['2024-06-20', 1/4.68],
    'VSMA': ['2024-06-18', 1/7],
    'GRI': ['2024-06-18', 1/13],
    'FORD': ['2024-06-18', 1/10],
    'WKHS': ['2024-06-17', 1/20],
    'STRR': ['2024-06-17', 1/5],
    'SPCE': ['2024-06-17', 1/20],
    'SLRX': ['2024-06-17', 1/8],
    'CATX': ['2024-06-17', 1/10],
    'TWOU': ['2024-06-14', 1/30],
    'TRNR': ['2024-06-14', 1/40],
    'CZFS': ['2024-06-14', 1.01/1],
    'VLD': ['2024-06-13', 1/35],
    'RBOT': ['2024-06-13', 1/30],
    'NAAS': ['2024-06-13', 1/20],
    'PEGY': ['2024-06-12', 1/15],
    'BNED': ['2024-06-12', 1/100],
    'APH': ['2024-06-12', 2/1],
    'KPRX': ['2024-06-11', 1/9],
    'DM': ['2024-06-11', 1/10],
    'CNQ': ['2024-06-11', 2/1],
    'TNXP': ['2024-06-10', 1/32],
    'RTC': ['2024-06-10', 1/5],
    'NVDA': ['2024-06-10', 10/1],
    'ICU': ['2024-06-10', 1/25],
    'VLCN': ['2024-06-07', 1/100],
    'SSKN': ['2024-06-07', 1/10],
    'DBVT': ['2024-06-07', 1/2],
    'CEAD': ['2024-06-07', 1/12],
    'SNGX': ['2024-06-06', 1/16],
    'QXO': ['2024-06-06', 1/8],
    'CNSP': ['2024-06-05', 1/50],
    'LICY': ['2024-06-04', 1/8],
    'PLAG': ['2024-06-03', 1/10],
    'GWAV': ['2024-06-03', 1/149.93],
    'NBY': ['2024-05-31', 1/35],
    'BCDA': ['2024-05-30', 1/15],
    'GV': ['2024-05-29', 1/15],
    'THAR': ['2024-05-28', 1/15],
    'SINT': ['2024-05-28', 1/200],
    'CIG.C': ['2024-05-24', 1.3/1],
    'CIG': ['2024-05-24', 1.3/1],
    'JAGX': ['2024-05-23', 1/59.99],
    'AKAN': ['2024-05-23', 1/40],
    'CIM': ['2024-05-22', 1/5],
    'SCNI': ['2024-05-21', 1/10],
    'OPGN': ['2024-05-20', 1/10],
    'GCTK': ['2024-05-20', 1/5],
    'BSFC': ['2024-05-20', 1/50],
    'HSCS': ['2024-05-17', 1/100],
    'CTHR': ['2024-05-17', 1/10],
    'SEEL': ['2024-05-16', 1/8],
    'ELWS': ['2024-05-16', 1/5],
    'DRMA': ['2024-05-16', 1/15],
    'WAY': ['2024-05-15', 1/1.65],
    'BNR': ['2024-05-15', 1/10],
    'TIRX': ['2024-05-14', 1/5],
    'ADN': ['2024-05-14', 1/30],
    'ZH': ['2024-05-10', 1/6],
    'TBIO': ['2024-05-09', 1/18],
    'IVP': ['2024-05-08', 1/100],
    'SCCO': ['2024-05-07', 1.01/1],
    'OLB': ['2024-05-06', 1/10],
    'BZFD': ['2024-05-06', 1/4],
    'YTEN': ['2024-05-03', 1/24],
    'AEZS': ['2024-05-03', 1/4],
    'SGBX': ['2024-05-03', 1/20],
    'VINO': ['2024-05-01', 1/10],
    'SOPA': ['2024-05-01', 1/15],
    'RCON': ['2024-05-01', 1/18],
    'BKKT': ['2024-04-29', 1/25],
    'ZVSA': ['2024-04-26', 1/10],
    'ATXI': ['2024-04-26', 1/75.02],
    'XTKG': ['2024-04-25', 1.06/1],
    'APDN': ['2024-04-25', 1/20],
    'CDTX': ['2024-04-24', 1/20],
    'ZAPP': ['2024-04-24', 1/20],
    'PIRS': ['2024-04-23', 1/80],
    'MYSZ': ['2024-04-23', 1/8],
    'BPTY': ['2024-04-23', 1/40],
    'WINT': ['2024-04-22', 1/18],
    'SMFL': ['2024-04-22', 1/7],
    'GSUN': ['2024-04-19', 1/10],
    'GGB': ['2024-04-18', 1.2/1],
    'BENF': ['2024-04-18', 1/80],
    'SBFM': ['2024-04-17', 1/100],
    'NCNA': ['2024-04-16', 1/25],
    'LOAR': ['2024-04-16', 377450.98/1],
    'WISA': ['2024-04-15', 1/149.93],
    'MRIN': ['2024-04-15', 1/6],
    'GRRR': ['2024-04-15', 1/10],
    'FRPH': ['2024-04-15', 2/1],
    'MI': ['2024-04-15', 1/50],
    'FLNT': ['2024-04-15', 1/6],
    'EZGO': ['2024-04-12', 1/40],
    'CISS': ['2024-04-12', 1/100],
    'AGEN': ['2024-04-12', 1/20],
    'SMSI': ['2024-04-11', 1/8],
    'BON': ['2024-04-11', 1/10],
    'TCON': ['2024-04-10', 1/20],
    'NUTX': ['2024-04-10', 1/15],
    'CTRI': ['2024-04-09', 742575.21/1],
    'ALLR': ['2024-04-09', 1/20],
    'PALI': ['2024-04-08', 1/15],
    'SNPX': ['2024-04-05', 1/25],
    'RNAC': ['2024-04-05', 1/30],
    'GLAD': ['2024-04-05', 2/1],
    'EDBL': ['2024-04-05', 1/20],
    'STKH': ['2024-04-04', 1/10],
    'UCAR': ['2024-04-04', 1/100],
    'RENT': ['2024-04-03', 1/20],
    'XXII': ['2024-04-02', 1/16],
    'NRXP': ['2024-04-02', 1/10],
    'FLYE': ['2024-04-02', 110000/1],
    'EMKR': ['2024-04-02', 1/10],
    'DCFCQ': ['2024-04-02', 1/200],
    'AWIN': ['2024-04-02', 1/100],
    'PLUR': ['2024-04-01', 1/8],
    'CTNM': ['2024-04-01', 1/5.6],
    'ODFL': ['2024-03-28', 2/1],
    'DOYU': ['2024-03-28', 1/10],
    'TPL': ['2024-03-27', 3/1],
    'LGVN': ['2024-03-27', 1/10],
    'GHI': ['2024-03-27', 1/1],
    'CTRM': ['2024-03-27', 1/10],
    'QTTB': ['2024-03-26', 1/18],
    'LINK': ['2024-03-25', 1.5/1],
    'INTZ': ['2024-03-25', 1/20],
    'MLGO': ['2024-03-22', 1/10],
    'MBRX': ['2024-03-22', 1/15],
    'LENZ': ['2024-03-22', 1/7],
    'BCAN': ['2024-03-22', 1/190.11],
    'ATER': ['2024-03-22', 1/12],
    'CSPI': ['2024-03-21', 2/1],
    'BTTR': ['2024-03-21', 1/43.99],
    'ADVM': ['2024-03-21', 1/10],
    'BOLD': ['2024-03-19', 1/19.5],
    'AEVA': ['2024-03-19', 1/5],
    'YSG': ['2024-03-19', 1/5],
    'SER': ['2024-03-15', 1/35.17],
    'LFWD': ['2024-03-15', 1/7],
    'OTLK': ['2024-03-14', 1/20],
    'XTIA': ['2024-03-14', 1/100],
    'HPCO': ['2024-03-13', 1/10],
    'AFMD': ['2024-03-11', 1/10],
    'PGY': ['2024-03-08', 1/12],
    'GXAI': ['2024-03-08', 1/12],
    'GOEV': ['2024-03-08', 1/23],
    'CISO': ['2024-03-07', 1/15],
    'PIK': ['2024-03-07', 1/5],
    'CPHI': ['2024-03-06', 1/5],
    'APVO': ['2024-03-06', 1/43.99],
    'TR': ['2024-03-06', 1.03/1],
    'LQR': ['2024-03-04', 1.5/1],
    'IFBD': ['2024-03-04', 1/8],
    'AUNA': ['2024-03-04', 1/5.5],
    'VRPX': ['2024-03-01', 1/10],
    'RETO': ['2024-03-01', 1/10],
    'FFIE': ['2024-03-01', 1/3],
    'EGIO': ['2024-03-01', 1/40],
    'CJJD': ['2024-03-01', 1/20],
    'ZCMD': ['2024-02-29', 1/10],
    'CELU': ['2024-02-29', 1/10],
    'ATNF': ['2024-02-28', 1/19],
    'TGL': ['2024-02-27', 1/69.98],
    'PHUN': ['2024-02-27', 1/50],
    'AUUD': ['2024-02-27', 1/25],
    'WMT': ['2024-02-26', 3/1],
    'TRIB': ['2024-02-23', 1/5],
    'LYT': ['2024-02-23', 1/59.99],
    'BPTH': ['2024-02-23', 1/20],
    'VCNX': ['2024-02-20', 1/14],
    'JZ': ['2024-02-20', 1/3],
    'COO': ['2024-02-20', 4/1],
    'AMBO': ['2024-02-20', 1/10],
    'ACB': ['2024-02-20', 1/10],
    'SISI': ['2024-02-16', 1/10],
    'MYMD': ['2024-02-15', 1/30],
    'VRM': ['2024-02-14', 1/80],
    'EJH': ['2024-02-14', 1/5],
    'DTIL': ['2024-02-14', 1/30],
    'CHRO': ['2024-02-14', 1/9],
    'SGLY': ['2024-02-12', 1/10],
    'ASMB': ['2024-02-12', 1/12],
    'UAVS': ['2024-02-09', 1/20],
    'GRYP': ['2024-02-09', 1/20],
    'CENTA': ['2024-02-09', 1.25/1],
    'CENT': ['2024-02-09', 1.25/1],
    'ZJYL': ['2024-02-08', 20/1],
    'VLCN': ['2024-02-05', 1/45],
    'GTBP': ['2024-02-05', 1/30],
    'FRGT': ['2024-02-05', 1/10],
    'ZBAO': ['2024-02-04', 3/1],
    'HOLO': ['2024-02-04', 1/40],
    'GNPX': ['2024-02-02', 1/10],
    'CAMPQ': ['2024-02-02', 1/23],
    'BSGM': ['2024-02-02', 1/10],
    'TCRT': ['2024-02-01', 1/15],
    'NA': ['2024-02-01', 1/20],
    'CMAX': ['2024-02-01', 1/30],
    'GOVX': ['2024-01-31', 1/15],
    'QGEN': ['2024-01-31', 1.03/1],
    'GRI': ['2024-01-30', 1/7],
    'MMAT': ['2024-01-29', 1/100],
    'INBS': ['2024-01-29', 1/12],
    'HUBG': ['2024-01-29', 2/1],
    'TC': ['2024-01-26', 1/15],
    'REVB': ['2024-01-25', 1/30],
    'KAVL': ['2024-01-25', 1/21],
    'INO': ['2024-01-25', 1/12],
    'BTSG': ['2024-01-25', 15.7/1],
    'INSG': ['2024-01-24', 1/10],
    'DTSS': ['2024-01-23', 1/15],
    'REBN': ['2024-01-22', 1/8],
    'PCSA': ['2024-01-22', 1/20],
    'NVVE': ['2024-01-22', 1/40],
    'EVAX': ['2024-01-22', 1/10],
    'CNEY': ['2024-01-19', 1/30],
    'CLEU': ['2024-01-19', 1/15],
    'PBLA': ['2024-01-18', 1/20],
    'AULT': ['2024-01-17', 1/25],
    'UXIN': ['2024-01-16', 1/10],
    'RNAZ': ['2024-01-16', 1/40],
    'AXIL': ['2024-01-16', 1/20],
    'EFTR': ['2024-01-12', 1/25],
    'MESO': ['2024-01-10', 1/2],
    'TTNP': ['2024-01-09', 1/20],
    'ONCT': ['2024-01-08', 1/20],
    'EIGRQ': ['2024-01-08', 1/30],
    'SABS': ['2024-01-05', 1/10],
    'DSS': ['2024-01-05', 1/20],
    'JSPR': ['2024-01-04', 1/10],
    'ACON': ['2024-01-04', 1/16],
    'TENX': ['2024-01-03', 1/80],
    'PRSO': ['2024-01-03', 1/2],
    'LXEH': ['2024-01-03', 1/16],
    'TBLT': ['2024-01-02', 1/65.02],
    'KTTA': ['2024-01-02', 1/20],
    'VS': ['2023-12-29', 1/16],
    'AVTX': ['2023-12-29', 1/149.93],
    'NXU': ['2023-12-27', 1/30],
    'LIDR': ['2023-12-27', 1/10],
    'GMBL': ['2023-12-22', 1/400],
    'NRBO': ['2023-12-21', 1/8],
    'MULN': ['2023-12-21', 1/100],
    'BKYI': ['2023-12-21', 1/18],
    'WNW': ['2023-12-20', 1/35],
    'SIDU': ['2023-12-20', 1/100],
    'SCOR': ['2023-12-20', 1/20],
    'CGC': ['2023-12-20', 1/10],
    'BBLG': ['2023-12-20', 1/8],
    'TFFP': ['2023-12-19', 1/25],
    'NGNE': ['2023-12-19', 1/4],
    'YQ': ['2023-12-18', 1/5],
    'VRAX': ['2023-12-18', 1/10],
    'ENTO': ['2023-12-18', 1/20],
    'CYCC': ['2023-12-18', 1/15],
    'TCBP': ['2023-12-15', 1/20],
    'SING': ['2023-12-15', 1/26],
    'LU': ['2023-12-15', 1/4],
    'HUBC': ['2023-12-15', 1/10],
    'SRZN': ['2023-12-14', 1/15],
    'GENE': ['2023-12-14', 1/100],
    'AIMD': ['2023-12-14', 1/5],
    'CYTO': ['2023-12-13', 1/20],
    'AUVIP': ['2023-12-12', 1/25],
    'SNCR': ['2023-12-11', 1/9],
    'JG': ['2023-12-11', 1/20],
    'TIL': ['2023-12-08', 1/20],
    'SNCE': ['2023-12-08', 1/20],
    'CENN': ['2023-12-08', 1/10],
    'XOS': ['2023-12-07', 1/30],
    'XHG': ['2023-12-07', 1/40],
    'PAVM': ['2023-12-07', 1/15],
    'ZVSA': ['2023-12-05', 1/35],
    'DEC': ['2023-12-05', 1/20],
    'SYTA': ['2023-12-04', 1/7],
    'MCOM': ['2023-12-04', 1/149.93],
    'BNRG': ['2023-12-04', 1/10],
    'ENG': ['2023-12-01', 1/8],
    'UK': ['2023-11-30', 1/12],
    'LQR': ['2023-11-30', 1/59.99],
    'LARK': ['2023-11-30', 1.05/1],
    'IXHL': ['2023-11-30', 1/4],
    'CING': ['2023-11-30', 1/20],
    'RGS': ['2023-11-29', 1/5],
    'PRAX': ['2023-11-29', 1/15],
    'IBIO': ['2023-11-29', 1/20],
    'YOSH': ['2023-11-28', 1/10],
    'SEEL': ['2023-11-28', 1/30],
    'CMND': ['2023-11-28', 1/30],
    'SNEX': ['2023-11-28', 1.5/1],
    'CHR': ['2023-11-27', 1/10],
    'NURO': ['2023-11-22', 1/8],
    'BODI': ['2023-11-22', 1/50],
    'VTVT': ['2023-11-21', 1/40],
    'THAR': ['2023-11-21', 1/25],
    'IFBD': ['2023-11-20', 1/20],
    'TRVG': ['2023-11-17', 1/5],
    'SNES': ['2023-11-17', 1/12],
    'AMTD': ['2023-11-17', 1/3],
    'MDXH': ['2023-11-16', 1/16],
    'DDC': ['2023-11-16', 1/16],
    'AEYGQ': ['2023-11-15', 1/10],
    'RVSN': ['2023-11-15', 1/8],
    'HYMC': ['2023-11-15', 1/10],
    'CELH': ['2023-11-15', 3/1],
    'XRTX': ['2023-11-14', 1/9],
    'PRE': ['2023-11-14', 1/15],
    'QNRX': ['2023-11-08', 1/10],
    'NVOS': ['2023-11-08', 1/10],
    'FOXO': ['2023-11-07', 1/20],
    'DOGZ': ['2023-11-07', 1/50],
    'KRRO': ['2023-11-06', 1/7],
    'JFBR': ['2023-11-03', 1/7],
    'CANOQ': ['2023-11-02', 1/100],
    'XHG': ['2023-11-02', 1/10],
    'TNON': ['2023-11-02', 1/10],
    'MOTS': ['2023-11-02', 1/15],
    'MYND': ['2023-11-01', 2/1],
    'BYFC': ['2023-11-01', 1/8],
    'AAMC': ['2023-11-01', 1.7/1],
    'PXMD': ['2023-10-31', 1/17],
    'GYRE': ['2023-10-31', 1/15],
    'ALZN': ['2023-10-31', 1/15],
    'GVP': ['2023-10-30', 1/50],
    'BYU': ['2023-10-30', 1/16],
    'ZIVO': ['2023-10-27', 1/6],
    'VVOS': ['2023-10-27', 1/25],
    'SMFL': ['2023-10-27', 1/20]
}


input_file_path = os.path.join(os.getcwd(), "input/date_dataframes.pkl")

with open(input_file_path, 'rb') as input_file:
    date_dataframes = pickle.load(input_file)

rebalancing = {'2023': ['2023-11-10','2024-06-28'],
               '2024': ['2024-06-28','2025-06-28']
              }

unique_dates = list(date_dataframes.keys())

eod_market_cap_pivot = {}

all_states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 
              'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 
              'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 
              'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 
              'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']

all_gics_sectors = ['Communication Services', 'Consumer Discretionary', 'Consumer Staples', 
                    'Energy', 'Financials', 'Health Care', 'Industrials',
                    'Information Technology', 'Materials', 'Real Estate', 'Utilities']



# Sidebar multiselect for states
states = st.sidebar.multiselect("Select States", all_states, default=['PA'])

select_all = st.sidebar.checkbox("Select All GICS Sectors", value=True)

# Multiselect with all options selected by default if select_all is True
if select_all:
    gics_sectors = all_gics_sectors
else:
    gics_sectors = st.sidebar.multiselect("Select GICS Sector", all_gics_sectors, all_gics_sectors)

companies = st.sidebar.number_input("Number of Companies", min_value=1, max_value=3000, value=100)

for year in rebalancing.keys():
    dataframe_file = f'input/RAY_{rebalancing[year][0]}.xlsx'
    first_df = pd.read_excel(dataframe_file)
    first_df.columns = first_df.columns.str.rstrip('\n')
    first_df['Ticker'] = first_df['Ticker'].str.split(' ',n=1,expand=True)[0].replace(' ','')
    first_df['Ticker'] = first_df['Ticker'].str.replace('/', '.')
    df = first_df[first_df['State of Domicile'].isin(states)]
    df = df[df['GICS Sector'].isin(gics_sectors)]
    df = df.sort_values('Market Cap', ascending=False)
    df = df[['Ticker','Equity Float','GICS Sector']].head(companies)

    eod_market_cap_pivot[year] = pd.DataFrame()

    for date in unique_dates:
        if date >= rebalancing[year][0] and date <= rebalancing[year][1]:
            eod_df = date_dataframes[date]
            merged_df = pd.merge(df,eod_df,left_on='Ticker',right_on='underlying_symbol')
            for i,ticker in enumerate(merged_df['Ticker']):
                for company in stock_split.keys():
                    if ticker == company and date >= stock_split[ticker][0]:
                        merged_df.at[i,'Equity Float'] = merged_df.at[i,'Equity Float'] * stock_split[ticker][1]
            merged_df['Market Cap'] = merged_df['Equity Float'] * merged_df['close']
            eod_market_cap_daily = merged_df.pivot_table(values='Market Cap',index='quote_date',columns='Ticker',aggfunc='sum')
            eod_market_cap_pivot[year] = pd.concat([eod_market_cap_pivot[year],eod_market_cap_daily])

    eod_market_cap_pivot[year] = eod_market_cap_pivot[year].rename_axis(index='Date')
    eod_market_cap_pivot[year].index = pd.to_datetime(eod_market_cap_pivot[year].index,errors='coerce')

    eod_market_cap_pivot[year]['mkt_cap_deleted_stock'] = 0
    
    for ticker in eod_market_cap_pivot[year].keys():
        last_valid_market_cap = None
        first_deletion = False
    
        for date_index, date in enumerate(eod_market_cap_pivot[year].index):
    
            if date != eod_market_cap_pivot[year].index[-1]:
            
                next_date = eod_market_cap_pivot[year].index[date_index + 1]
            
                market_cap = eod_market_cap_pivot[year].at[date,ticker]
    
                market_cap_next_date = eod_market_cap_pivot[year].at[next_date,ticker]
    
                if (pd.isna(market_cap) or market_cap == 0) and (pd.isna(market_cap_next_date) or market_cap_next_date == 0):
                    if not first_deletion and last_valid_market_cap is not None:
                        eod_market_cap_pivot[year].at[date, 'mkt_cap_deleted_stock'] = last_valid_market_cap
                        first_deletion = True
    
                if (pd.isna(market_cap) or market_cap == 0) and market_cap_next_date != 0:
                    if not first_deletion and last_valid_market_cap is not None:
                        eod_market_cap_pivot[year].at[date,ticker] = last_valid_market_cap
                        first_deletion = True
                
                else:
                    last_valid_market_cap = market_cap
                    first_deletion = False
    
            else:
                market_cap = eod_market_cap_pivot[year].at[date,ticker]
                if pd.isna(market_cap) or market_cap == 0:
                    if not first_deletion and last_valid_market_cap is not None:
                        eod_market_cap_pivot[year].at[date,ticker] = last_valid_market_cap
                        first_deletion = True
                else:
                    last_valid_market_cap = market_cap
                    first_deletion = False
    
    eod_market_cap_pivot[year]["close_mkt_cap"] = eod_market_cap_pivot[year].drop(columns='mkt_cap_deleted_stock').sum(axis=1)
    
    
    eod_market_cap_pivot[year]["adj_mkt_cap"] = 0
    eod_market_cap_pivot[year]["divisor"] = 0
    eod_market_cap_pivot[year]["gross_index_level"] = 0
    eod_market_cap_pivot[year]["Index Value"] = 0
    
for j,year in enumerate(eod_market_cap_pivot.keys()):
    if j == 0:
        for i in range(0, len(eod_market_cap_pivot[year])):
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=FutureWarning)
                if i == 0:
                    eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "adj_mkt_cap"] = float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "close_mkt_cap"]) + float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "mkt_cap_deleted_stock"])
                    eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "divisor"] = 1
                    eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "gross_index_level"] = float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "close_mkt_cap"]) / float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "divisor"])
                    eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "Index Value"] = float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "gross_index_level"]) / (float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[0], "close_mkt_cap"]) / 100)
                else:
                    eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "adj_mkt_cap"] = float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i-1], "close_mkt_cap"]) - float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "mkt_cap_deleted_stock"])
                    eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "divisor"] = (float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "adj_mkt_cap"]) / float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i-1], "close_mkt_cap"])) * float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i-1], "divisor"])
                    eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "gross_index_level"] = float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "close_mkt_cap"]) / float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "divisor"])
                    eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "Index Value"] = float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "gross_index_level"]) / (float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[0], "close_mkt_cap"]) / 100)
        last_value = eod_market_cap_pivot[year].iloc[-1]['Index Value']
    else:
        for i in range(0, len(eod_market_cap_pivot[year])):
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=FutureWarning)
                if i == 0:
                    eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "adj_mkt_cap"] = float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "close_mkt_cap"]) + float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "mkt_cap_deleted_stock"])
                    eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "divisor"] = 1
                    eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "gross_index_level"] = float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "close_mkt_cap"]) / float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "divisor"])
                    eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "Index Value"] = float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "gross_index_level"]) / (float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[0], "close_mkt_cap"]) / last_value)
                else:
                    eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "adj_mkt_cap"] = float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i-1], "close_mkt_cap"]) - float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "mkt_cap_deleted_stock"])
                    eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "divisor"] = (float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "adj_mkt_cap"]) / float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i-1], "close_mkt_cap"])) * float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i-1], "divisor"])
                    eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "gross_index_level"] = float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "close_mkt_cap"]) / float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "divisor"])
                    eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "Index Value"] = float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[i], "gross_index_level"]) / (float(eod_market_cap_pivot[year].at[eod_market_cap_pivot[year].index[0], "close_mkt_cap"]) / last_value)
        last_value = eod_market_cap_pivot[year].iloc[-1]['Index Value']        


list_of_dataframes = []

for i,year in enumerate(eod_market_cap_pivot.keys()):
    if i == 0:
        list_of_dataframes.append(eod_market_cap_pivot[year])
    else:
        list_of_dataframes.append(eod_market_cap_pivot[year].iloc[1:])

final_df = pd.concat(list_of_dataframes)
index_df = final_df[['Index Value']].copy()

y_axis_min = index_df.min() - 5
y_axis_max = index_df.max() + 5


fig = px.line(index_df, y="Index Value", title="Index Value Over Time")



fig.update_layout(title='Index Value Over Time',
                  xaxis_title='Date',
                  yaxis_title='Index Value',
                  yaxis=dict(range=[y_axis_min, y_axis_max]),
 )
col1, col2 = st.columns([1, 4])  # Adjust the ratio as needed

# Display the DataFrame in the first column
with col1:
    st.write(index_df)

# Display the plotly figure in the second column
with col2:
    st.plotly_chart(fig)





what_state = []
what_ticker = []

for ticker in eod_market_cap_pivot[year].keys():
    for i, company in enumerate(first_df['Ticker']):
        if ticker == company:
            what_ticker.append(ticker)
            what_state.append(first_df.at[i, "State of Domicile"])

state_info = pd.DataFrame([what_ticker,what_state]).T
state_info.columns = ['Ticker','State']
state_info = state_info.set_index('Ticker')
state_counts = state_info.value_counts().reset_index()
state_counts.columns = ['State', 'Count']

st.write("State Value Counts")
st.dataframe(state_counts)









# Assuming `unique_dates` is already defined and populated
latest_date = max(unique_dates)

# Convert `latest_date` from string to datetime object
latest_date = pd.to_datetime(latest_date)

# Get the data for the latest date
latest_date_df = date_dataframes[latest_date.strftime("%Y-%m-%d")]

# Merge with the original dataframe to get the sector information
latest_date_merged_df = pd.merge(df[['Ticker', 'Equity Float', 'GICS Sector']], latest_date_df, left_on='Ticker', right_on='underlying_symbol')

# Calculate the market cap for the latest date
latest_date_merged_df['Market Cap'] = latest_date_merged_df['Equity Float'] * latest_date_merged_df['close']

# Aggregate market cap by sector
sector_distribution = latest_date_merged_df.groupby('GICS Sector')['Market Cap'].sum().reset_index()

# Generate pie chart
fig_pie = px.pie(sector_distribution, names='GICS Sector', values='Market Cap', title=f'Sector Distribution on {latest_date.strftime("%Y-%m-%d")}')

# Streamlit code to display the pie chart
st.plotly_chart(fig_pie)

# Generate the treemap for sector distribution
fig_treemap = px.treemap(sector_distribution, path=['GICS Sector'], values='Market Cap',
                        title=f'Sector Distribution on {latest_date.strftime("%Y-%m-%d")}',
                        color='Market Cap',
                        color_continuous_scale='Viridis')

# Display the treemap in Streamlit
st.plotly_chart(fig_treemap)