"""
California Housing — Data-Quality Clean + Exploratory Analysis
Reproduces the Excel project in Python.
Usage:  python3 housing_analysis.py housing.csv
"""
import sys, os
import numpy as np
import pandas as pd

CSV_PATH = sys.argv[1] if len(sys.argv) > 1 else "housing.csv"
OUT_XLSX = "housing_project.xlsx"
CHART_DIR = "charts"

def load_data(path):
    if not os.path.exists(path):
        sys.exit(f"ERROR: could not find '{path}'. Pass it as: python3 housing_analysis.py <file>")
    df = pd.read_csv(path)
    print(f"Loaded {len(df):,} rows x {df.shape[1]} columns from {path}")
    return df

def clean_data(df):
    df = df.copy()
    bed_median = df["total_bedrooms"].median()
    df["bed_missing_flag"] = df["total_bedrooms"].isna().astype(int)
    df["total_bedrooms_filled"] = df["total_bedrooms"].fillna(bed_median)
    df["value_capped_flag"] = (df["median_house_value"] == 500001).astype(int)
    df["income_capped_flag"] = (df["median_income"] >= 15).astype(int)
    df["age_capped_flag"] = (df["housing_median_age"] == 52).astype(int)
    print(f"  Imputed {df['bed_missing_flag'].sum()} missing bedrooms with median {bed_median:g}")
    print(f"  Flagged {df['value_capped_flag'].sum()} value-capped, "
          f"{df['income_capped_flag'].sum()} income-capped, "
          f"{df['age_capped_flag'].sum()} age-capped rows")
    return df

def summary_stats(df):
    cols = ["housing_median_age","total_rooms","total_bedrooms_filled","population",
            "households","median_income","median_house_value"]
    stats = df[cols].agg(["count","mean","median","std","min","max"]).T
    stats["p25"] = df[cols].quantile(0.25).values
    stats["p75"] = df[cols].quantile(0.75).values
    return stats.round(2)

def segment_by_ocean(df):
    g = df.groupby("ocean_proximity").agg(
        districts=("median_house_value","size"),
        avg_house_value=("median_house_value","mean"),
        avg_median_income=("median_income","mean"))
    g["pct_of_total"] = g["districts"]/g["districts"].sum()
    return g.sort_values("districts", ascending=False).round(2)

def segment_by_income(df):
    bins=[0,2,4,6,8,np.inf]; labels=["< 2","2 - 4","4 - 6","6 - 8","8 +"]
    df = df.assign(income_bracket=pd.cut(df["median_income"],bins=bins,labels=labels,right=False))
    g = df.groupby("income_bracket",observed=True).agg(
        districts=("median_house_value","size"),
        avg_house_value=("median_house_value","mean"))
    g["pct_of_total"]=g["districts"]/g["districts"].sum()
    return g.round(2)

def segment_by_latitude(df):
    bins=[0,34,36,38,40,np.inf]
    labels=["< 34 (far south)","34-36 (LA/coast)","36-38 (central/Bay S)","38-40 (Bay N/Sac)","40+ (far north)"]
    df = df.assign(lat_band=pd.cut(df["latitude"],bins=bins,labels=labels,right=False))
    g = df.groupby("lat_band",observed=True).agg(
        districts=("median_house_value","size"),
        avg_house_value=("median_house_value","mean"),
        avg_median_income=("median_income","mean"))
    return g.round(2)

def correlations(df):
    feats=["median_income","total_rooms","housing_median_age","households","population"]
    corr={f: df[f].corr(df["median_house_value"]) for f in feats}
    return pd.Series(corr,name="corr_with_house_value").sort_values(ascending=False).round(3).to_frame()

def make_charts(ocean, income, lat):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(CHART_DIR, exist_ok=True)
    def bar(series,title,fname,color):
        fig,ax=plt.subplots(figsize=(7,4))
        series.plot(kind="bar",ax=ax,color=color)
        ax.set_title(title); ax.set_ylabel("Avg house value ($)")
        ax.tick_params(axis="x",rotation=30); fig.tight_layout()
        fig.savefig(os.path.join(CHART_DIR,fname),dpi=120); plt.close(fig)
    bar(ocean["avg_house_value"],"Avg House Value by Ocean Proximity","value_by_ocean.png","#2E75B6")
    bar(income["avg_house_value"],"Avg House Value by Income Bracket","value_by_income.png","#548235")
    bar(lat["avg_house_value"],"Avg House Value by Latitude Band","value_by_latitude.png","#C55A11")
    print(f"  Saved 3 charts to ./{CHART_DIR}/")

def export_excel(clean, stats, ocean, income, lat, corr):
    with pd.ExcelWriter(OUT_XLSX, engine="openpyxl") as xl:
        stats.to_excel(xl, sheet_name="Summary Stats")
        ocean.to_excel(xl, sheet_name="By Ocean Proximity")
        income.to_excel(xl, sheet_name="By Income Bracket")
        lat.to_excel(xl, sheet_name="By Latitude Band")
        corr.to_excel(xl, sheet_name="Correlations")
        clean.head(1000).to_excel(xl, sheet_name="Clean Data (sample)", index=False)
    print(f"  Wrote {OUT_XLSX}")

def main():
    print("="*60)
    df = load_data(CSV_PATH)
    clean = clean_data(df)
    stats = summary_stats(clean)
    ocean = segment_by_ocean(clean)
    income = segment_by_income(clean)
    lat = segment_by_latitude(clean)
    corr = correlations(clean)
    print("\nKEY FINDINGS\n"+"-"*60)
    print(f"Strongest driver of house value: median_income (r = {corr.iloc[0,0]:.2f})")
    print(f"Cheapest region: {ocean['avg_house_value'].idxmin()} (${ocean['avg_house_value'].min():,.0f})")
    print(f"Value range across income brackets: ${income['avg_house_value'].min():,.0f} -> ${income['avg_house_value'].max():,.0f}")
    make_charts(ocean, income, lat)
    export_excel(clean, stats, ocean, income, lat, corr)
    print("="*60+"\nDone.")

if __name__ == "__main__":
    main()
