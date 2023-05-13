"""Some data types that are used as building blocks in the main ReferenceData classes."""

from enum import Enum, StrEnum


class IndexTermUnit(Enum):
    DAYS = "days"
    WEEK = "week"
    MNTH = "month"
    YEAR = "year"


class IndexName(StrEnum):
    EONA = "EONIA"
    EONS = "EONIA SWAP"
    EURO = "EURIBOR"
    EUCH = "EuroSwiss"
    GCFR = "GCF REPO"
    ISDA = "ISDAFIX"
    LIBI = "LIBID"
    LIBO = "LIBOR"
    MAAA = "Muni AAA"
    PFAN = "Pfandbriefe"
    TIBO = "TIBOR"
    STBO = "STIBOR"
    BBSW = "BBSW"
    JIBA = "JIBAR"
    BUBO = "BUBOR"
    CDOR = "CDOR"
    CIBO = "CIBOR"
    MOSP = "MOSPRIM"
    NIBO = "NIBOR"
    PRBO = "PRIBOR"
    TLBO = "TELBOR"
    WIBO = "WIBOR"
    TREA = "Treasury"
    SWAP = "SWAP"
    FUSW = "Future SWAP"


class DebtSeniority(Enum):
    SNDB = "senior"
    MZZD = "mezzanine"
    SBOD = "subordinated"
    JUND = "junior"


class OptionType(Enum):
    PUTO = "put"
    CALL = "call"
    OTHR = "other"


class OptionExerciseStyle(Enum):
    EURO = "European"
    AMER = "American"
    ASIA = "Asian"
    BERM = "Bermudan"
    OTHR = "Other"


class DeliveryType(Enum):
    PHYS = "physical"
    CASH = "cash"
    OPTL = "optional"  # "optional" is kind of a guess as to what word is being abbreviated


# Classification of commodity and emission allowances derivatives
# https://ec.europa.eu/finance/securities/docs/isd/mifid/rts/160714-rts-23-annex_en.pdf
class BaseProduct(Enum):
    AGRI = "Agricultural"
    NRGY = "Energy"
    ENVR = "Environmental"
    FRGT = "Freight"
    FRTL = "Fertilizer"
    INDP = "Industrial products"
    METL = "Metals"
    MCEX = "Multi Commodity Exotic"
    PAPR = "Paper"
    POLY = "Polypropylene"
    INFL = "Inflation"
    OEST = "Official economic statistics"
    OTHC = "Other C10 (as defined in Table 10.1 of Section 10 of Annex III to Commission Delegated Regulation " \
           "supplementing Regulation (EU) No 600/2014 of the European Parliament and of the Council with regard to " \
           "regulatory technical standards on transparency requirements for trading venues and investment firms in " \
           "respect of bonds, structured finance products, emission allowances and derivatives)"
    OTHR = "Other"


class SubProduct(Enum):
    # AGRI
    GROS = "Grains and Oil Seeds"
    SOFT = "Softs"
    POTA = "Potato"
    OOLI = "Olive oil"
    DIRY = "Dairy"
    FRST = "Forestry"
    SEAF = "Seafood"
    LSTK = "Livestock"
    GRIN = "Grain"

    # NRGY
    ELEC = "Electricity"
    NGAS = "Natural Gas"
    OILP = "Oil"
    COAL = "Coal"
    INRG = "Inter Energy"
    RNNG = "Renewable energy"
    LGHT = "Light ends"
    DIST = "Distillates"

    # ENVR
    EMIS = "Emissions"
    WTHR = "Weather"
    CRBR = "Carbon related"

    # FRGT
    WETF = "Wet"
    DRYF = "Dry"
    CSHP = "Container ships"

    # FRTL
    AMMO = "Ammonia"
    DAPH = "DAP (Diammonium Phosphate)"
    PTSH = "Potash"
    SLPH = "Sulphur"
    UREA = "Urea"
    UAAN = "UAN (urea and ammonium nitrate)"

    # INDP
    CSTR = "Construction"
    MFTG = "Manufacturing"

    # METL
    NPRM = "Non Precious"
    PRME = "Precious"

    # PAPR
    CBRD = "Containerboard"
    NSPT = "Newsprint"
    PULP = "Pulp"
    PLST = "Plastic"


class FurtherSubProduct(Enum):
    # GROS
    FWHT = "Feed Wheat"
    SOYB = "Soybeans"
    CORN = "Maize"
    RPSD = "Rapeseed"
    RICE = "Rice"

    # SOFT
    CCOA = "Cocoa"
    ROBU = "Robusta Coffee"
    WHSG = "White Sugar"
    BRWN = "Raw Sugar"

    # OOLI
    LAMP = "Lampante"

    # GRIN
    MWHT = "Milling Wheat"

    # ELEC
    BSLD = "Base load"
    FITR = "Financial Transmission Rights"
    PKLD = "Peak load"
    OFFP = "Off-peak"

    # NGAS
    GASP = "GASPOOL"
    LNGG = "LNG"
    NCGG = "NCG"
    TTFG = "TTF"

    # OILP
    BAKK = "Bakken"
    BDSL = "Biodiesel"
    BRNT = "Brent"
    BRNX = "Brent NX"
    CNDA = "Canadian"
    COND = "Condensate"
    DSEL = "Diesel"
    DUBA = "Dubai"
    ESPO = "ESPO"
    ETHA = "Ethanol"
    FUEL = "Fuel"
    FOIL = "Fuel Oil"
    GOIL = "Gasoil"
    GSLN = "Gasoline"
    HEAT = "Heating Oil"
    JTFL = "Jet Fuel"
    KERO = "Kerosene"
    LLSO = "Light Louisiana Sweet (LLS)"
    MARS = "MARS"
    NAPH = "Naptha"
    NGLO = "NGL"
    TAPI = "Tapis"
    URAL = "Urals"
    WTIO = "WTI"

    # EMIS
    CERE = "CER"
    ERUE = "ERU"
    EUAE = "EUA"
    EUAA = "EUAA"

    # WETF
    TNKR = "Tankers"

    # DRYF
    DBCR = "Dry bulk carriers"

    # NPRM
    ALUM = "Aluminium"
    ALUA = "Aluminium Alloy"
    CBLT = "Cobalt"
    COPR = "Copper"
    IRON = "Iron ore"
    LEAD = "Lead"
    MOLY = "Molybdenum"
    NASC = "NASAAC"
    NICK = "Nickel"
    STEL = "Steel"
    TINN = "Tin"
    ZINC = "Zinc"

    # PRME
    GOLD = "Gold"
    SLVR = "Silver"
    PTNM = "Platinum"
    PLDM = "Palladium"

    # Various
    OTHR = "Other"


class TransactionType(Enum):
    FUTR = "Futures"
    OPTN = "Options"
    TAPO = "TAPOS"
    SWAP = "Swaps"
    MINI = "Minis"
    OTCT = "OTC"
    ORIT = "Outright"
    CRCK = "Crack"
    DIFF = "Differential"
    OTHR = "Other"


class FinalPriceType(Enum):
    ARGM = "Argus/McCloskey"
    BLTC = "Baltic"
    EXOF = "Exchange"
    GBCL = "GlobalCOAL"
    IHSM = "HIS McCloskey"
    PLAT = "Platts"
    OTHR = "Other"


class FxType(Enum):
    FXCR = "FX Cross Rates"
    FXEM = "FX Emerging Markets"
    FXMJ = "FX Majors"
