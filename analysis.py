import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import UnivariateSpline
from tabulate import tabulate


COLUMNS_TO_KEEP = [
    "file_name",
    "comment",
    "project",
    "category",
    "scientific_category",
    "introduced",
    "removed",
]

PROJECTS_TO_KEEP = [
    "Astropy",
    "Athena",
    "Biopython",
    "Elmer",
    "Firedrake",
    "GROMACS",
    "Root",
    "MOOSE",
    "CESM",
]

CATEGORY_COLOR_MAP = {
    "algorithm debt": "#0072B2",
    "architectural debt": "#E69F00",
    "build debt": "#009E73",
    "code debt": "#CC79A7",
    "defect debt": "#D55E00",
    "design debt": "#56B4E9",
    "documentation debt": "#F0E442",
    "on hold debt": "#999999",
    "requirements debt": "#332288",
    "scientific debt": "#117733",
    "test debt": "#88CCEE",
}

SCIENTIFIC_COLOR_MAP = {
    "assumptions": "#0072B2",
    "missing edge case": "#E69F00",
    "computational accuracy": "#009E73",
    "translation challenges": "#CC79A7",
    "new scientific findings": "#D55E00",
}


def load_satd_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df = df[COLUMNS_TO_KEEP].copy()
    df["scientific_category"] = (
        df["scientific_category"]
        .str.replace('"', "", regex=False)
        .replace("scientific findings", "new scientific findings")
    )
    return df


def _smooth_values(values: pd.Series) -> list[float]:
    if len(values) < 4:
        return values.tolist()
    x = range(len(values))
    return UnivariateSpline(x, values, s=1)(x)


def plot_scientific_debt(
    projects_to_keep: list[str],
    introduced_counts: pd.DataFrame,
    removed_counts: pd.DataFrame,
    export_pdf_path: str | None = None,
) -> None:
    fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(18, 12))
    fig.suptitle(
        "Introduction and Removal Trends of Scientific SATD Comments", fontsize=16
    )

    handles = labels = None
    for idx, project in enumerate(projects_to_keep):
        ax = axes[idx // 3, idx % 3]
        introduced_data = introduced_counts.xs(project, level="project")
        removed_data = removed_counts.xs(project, level="project")

        if (
            "scientific debt" in introduced_data.columns
            and "scientific debt" in removed_data.columns
        ):
            introduced_data = introduced_data[["scientific debt"]]
            removed_data = removed_data[["scientific debt"]]
        else:
            introduced_data = pd.DataFrame(columns=["scientific debt"])
            removed_data = pd.DataFrame(columns=["scientific debt"])

        introduced_data_smooth = introduced_data.apply(_smooth_values, axis=0)
        removed_data_smooth = removed_data.apply(_smooth_values, axis=0)

        introduced_data_smooth.plot(
            kind="line",
            marker="o",
            color="#FF0000",
            ax=ax,
            label="Introduction",
            legend=False,
        )
        removed_data_smooth.plot(
            kind="line",
            marker="x",
            color="#0000FF",
            ax=ax,
            label="Removal",
            legend=False,
        )

        if handles is None and labels is None:
            handles, labels = ax.get_legend_handles_labels()

        ax.set_title(project)
        ax.set_xlabel("Year")
        if idx % 3 == 0:
            ax.set_ylabel("Normalized Count")
        ax.grid(True)

    fig.legend(handles, ["Introduction", "Removal"], loc="upper right", title="Type")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    if export_pdf_path:
        fig.savefig(export_pdf_path, format="pdf", bbox_inches="tight")
    plt.show()


def _set_segment_accessibility(
    ax: plt.Axes,
    sorted_columns: list[str],
    highlight_category: str | None = None,
    muted_alpha: float = 0.35,
) -> None:
    for category, container in zip(sorted_columns, ax.containers):
        for patch in container.patches:
            patch.set_edgecolor("white")
            patch.set_linewidth(0.6)
            if highlight_category is not None and category != highlight_category:
                patch.set_alpha(muted_alpha)
            else:
                patch.set_alpha(1.0)


def _bar_label_with_contrast(
    ax: plt.Axes, sorted_columns: list[str], highlight_category: str | None = None
) -> None:
    for category, container in zip(sorted_columns, ax.containers):
        labels = [f"{value:.1f}%" if value > 0 else "" for value in container.datavalues]
        text_color = "black"
        if container.patches:
            r, g, b, a = container.patches[0].get_facecolor()
            luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
            if a >= 0.9 and luminance < 0.45:
                text_color = "white"
        weight = (
            "bold"
            if (highlight_category is not None and category == highlight_category)
            else "normal"
        )
        ax.bar_label(
            container,
            labels=labels,
            label_type="center",
            fontsize=9,
            color=text_color,
            fontweight=weight,
        )


def plot_scientific_debt_percentages(
    df: pd.DataFrame,
    color_map: dict[str, str],
    highlight_category: str | None = None,
    highlight_color: str = "#2ca02c",
    export_pdf_path: str | None = None,
) -> None:
    category_counts = (
        df.groupby(["project", "scientific_category"]).size().unstack(fill_value=0)
    )
    category_percentages = category_counts.div(category_counts.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(12, 8))
    sorted_columns = category_counts.sum(axis=0).sort_values(ascending=False).index.tolist()
    sorted_columns = [cat for cat in sorted_columns if cat in color_map]
    category_percentages = category_percentages[sorted_columns]

    print(tabulate(category_percentages, headers="keys", tablefmt="psql", showindex=True))

    if highlight_category is None:
        bar_colors = [color_map[cat] for cat in sorted_columns]
    else:
        bar_colors = [
            highlight_color if cat == highlight_category else color_map[cat]
            for cat in sorted_columns
        ]

    category_percentages.plot(kind="bar", stacked=True, color=bar_colors, ax=ax)
    _set_segment_accessibility(ax, sorted_columns, highlight_category=highlight_category)
    _bar_label_with_contrast(ax, sorted_columns, highlight_category=highlight_category)

    ax.set_xlabel("project")
    ax.set_ylabel("Percentage")
    handles, labels = ax.get_legend_handles_labels()
    legend_labels = [
        f"{label.title()} (Highlighted)"
        if (highlight_category is not None and label == highlight_category)
        else label.title()
        for label in labels
    ]
    ax.legend(
        handles,
        legend_labels,
        title="Indicator",
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
    )
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    if export_pdf_path:
        fig.savefig(export_pdf_path, format="pdf", bbox_inches="tight")
    plt.show()


def plot_all_debt_category_percentages(
    df: pd.DataFrame,
    category_color_map: dict[str, str],
    highlight_category: str | None = None,
    highlight_color: str = "#2ca02c",
    muted_alpha: float = 0.25,
    export_pdf_path: str | None = None,
) -> None:
    df_local = df.copy()
    df_local["category"] = df_local["category"].str.lower().str.strip()
    exploded_df = df_local.assign(category=df_local["category"].str.split(", ")).explode(
        "category"
    )
    exploded_df["category"] = exploded_df["category"].str.strip()

    category_counts = exploded_df.groupby(["project", "category"]).size().unstack(fill_value=0)
    category_percentages = category_counts.div(category_counts.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(15, 10))
    sorted_columns = category_counts.sum(axis=0).sort_values(ascending=False).index.tolist()
    sorted_columns = [cat for cat in sorted_columns if cat in category_color_map]
    category_percentages = category_percentages[sorted_columns]

    if highlight_category is None:
        category_colors = [category_color_map[cat] for cat in sorted_columns]
    else:
        category_colors = [
            highlight_color if cat == highlight_category else category_color_map[cat]
            for cat in sorted_columns
        ]

    category_percentages.plot(kind="bar", stacked=True, color=category_colors, ax=ax)
    _set_segment_accessibility(
        ax,
        sorted_columns,
        highlight_category=highlight_category,
        muted_alpha=muted_alpha,
    )
    _bar_label_with_contrast(ax, sorted_columns, highlight_category=highlight_category)

    print(tabulate(category_percentages, headers="keys", tablefmt="psql", showindex=True))

    ax.set_xlabel("project")
    ax.set_ylabel("Percentage")
    handles, labels = ax.get_legend_handles_labels()
    legend_labels = [
        f"{label.title()} (Highlighted)"
        if (highlight_category is not None and label == highlight_category)
        else label.title()
        for label in labels
    ]
    ax.legend(
        handles,
        legend_labels,
        title="Debt Category",
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
    )
    plt.tight_layout()
    if export_pdf_path:
        fig.savefig(export_pdf_path, format="pdf", bbox_inches="tight")
    plt.show()


def build_introduction_removal_inputs(
    df: pd.DataFrame,
) -> tuple[list[str], pd.DataFrame, pd.DataFrame]:
    working_df = df.copy()
    working_df = working_df.dropna(subset=["category"])
    working_df.loc[~working_df["project"].isin(PROJECTS_TO_KEEP), "project"] = "CESM"

    working_df["introduced"] = pd.to_datetime(working_df["introduced"], utc=True, errors="coerce")
    working_df["Introduced_Year"] = working_df["introduced"].dt.year
    working_df = working_df.dropna(subset=["Introduced_Year"])
    working_df["Introduced_Year"] = working_df["Introduced_Year"].astype(int)

    working_df["category"] = working_df["category"].astype(str).str.replace(" ", "", regex=False).str.split(",")
    df_exploded = working_df.explode("category")
    df_exploded["category"] = (
        df_exploded["category"].str.replace("debt", " debt", regex=False).str.replace("hold", " hold", regex=False)
    )

    total_counts = df_exploded.groupby(["project", "category"]).size().unstack(fill_value=0)
    introduced_counts = (
        df_exploded.groupby(["Introduced_Year", "project", "category"]).size().unstack(fill_value=0)
    )
    introduced_counts = introduced_counts.reindex(columns=total_counts.columns, fill_value=0)
    introduced_norm = introduced_counts.div(total_counts, axis=1, level=1)

    working_df["removed"] = pd.to_datetime(working_df["removed"], utc=True, errors="coerce")
    working_df["Removed_Year"] = working_df["removed"].dt.year
    removed_df = working_df.dropna(subset=["Removed_Year"]).copy()
    removed_df["Removed_Year"] = removed_df["Removed_Year"].astype(int)
    removed_exploded = removed_df.explode("category")
    removed_exploded["category"] = (
        removed_exploded["category"]
        .str.replace("debt", " debt", regex=False)
        .str.replace("hold", " hold", regex=False)
    )

    removed_counts = (
        removed_exploded.groupby(["Removed_Year", "project", "category"])
        .size()
        .unstack(fill_value=0)
    )
    removed_counts = removed_counts.reindex(columns=total_counts.columns, fill_value=0)
    removed_norm = removed_counts.div(total_counts, axis=1, level=1)

    return PROJECTS_TO_KEEP, introduced_norm, removed_norm


def calculate_scientific_addressed_percentages(
    df: pd.DataFrame,
) -> tuple[pd.Series, pd.Series]:
    total_counts = df["scientific_category"].value_counts()
    addressed_counts = df[df["removed"].notna()]["scientific_category"].value_counts()
    unaddressed_counts = df[df["removed"].isna()]["scientific_category"].value_counts()

    addressed_percentages = (addressed_counts / total_counts * 100).sort_values(ascending=False)
    unaddressed_percentages = (unaddressed_counts / total_counts * 100).sort_values(
        ascending=False
    )
    return addressed_percentages, unaddressed_percentages


def main() -> None:
    parser = argparse.ArgumentParser(description="SATD analysis script converted from notebook.")
    parser.add_argument("--csv", default="ssw_satd.csv", help="Path to input CSV file.")
    parser.add_argument(
        "--export-dir",
        default=None,
        help="Directory to export PDF charts. If omitted, charts are not exported.",
    )
    parser.add_argument(
        "--scientific-highlight",
        default=None,
        help="Scientific category to highlight in the scientific categories chart.",
    )
    parser.add_argument(
        "--all-highlight",
        default="scientific debt",
        help="Debt category to highlight in the all categories chart.",
    )
    args = parser.parse_args()

    df = load_satd_data(args.csv)
    print(df.columns)

    export_dir = Path(args.export_dir) if args.export_dir else None
    if export_dir:
        export_dir.mkdir(parents=True, exist_ok=True)

    plot_all_debt_category_percentages(
        df,
        CATEGORY_COLOR_MAP,
        highlight_category=args.all_highlight,
        export_pdf_path=str(export_dir / "all_debt_category_percentages.pdf")
        if export_dir
        else None,
    )

    plot_scientific_debt_percentages(
        df,
        SCIENTIFIC_COLOR_MAP,
        highlight_category=args.scientific_highlight,
        export_pdf_path=str(export_dir / "scientific_debt_percentages.pdf")
        if export_dir
        else None,
    )

    projects, introduced_norm, removed_norm = build_introduction_removal_inputs(df)
    plot_scientific_debt(
        projects,
        introduced_norm,
        removed_norm,
        export_pdf_path=str(export_dir / "scientific_intro_removal_trends.pdf")
        if export_dir
        else None,
    )

    addressed, unaddressed = calculate_scientific_addressed_percentages(
        df.dropna(subset=["category"])
    )
    print("Percentage of 'scientific_category' mostly addressed (sorted):")
    print(addressed)
    print("\nPercentage of 'scientific_category' mostly unaddressed (sorted):")
    print(unaddressed)


if __name__ == "__main__":
    main()
