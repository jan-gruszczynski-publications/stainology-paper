import pandas as pd

from post_processing.loaders import get_papers

# PAPERS = get_papers(NEW_PAPERS_PATH)
PAPERS = get_papers("../concats/new_papers.csv")
PMID_TO_DATE = PAPERS.set_index("PMID")["EDAT"].to_dict()

WHO_mapping = pd.read_excel("../concats/Ovary Tumours from WHO Bluebook.xlsx",
                            index_col=0, skiprows=2).reset_index(drop=True)



def enrich_df_with_tumour_llm_classification(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriches the DataFrame with detailed WHO classification levels based on the 'matched_tumour' column.

    This function does not modify the 'matched_tumour' column. Instead, it adds four new columns:
    - 'tumour_class': The specific WHO Tumour Class.
    - 'category_2': The WHO Category 2 classification.
    - 'category_1': The WHO Category 1 classification.
    - 'mt_level': An integer specifying the hierarchical level of the 'matched_tumour'
      (0 for Class, 1 for Category 2, 2 for Category 1).

    Args:
        df: A pandas DataFrame containing the column 'matched_tumour'.

    Returns:
        A pandas DataFrame with the four new classification columns added.
    """
    assert 'matched_tumour' in df.columns, "DataFrame must contain 'matched_tumour' column."
    df = df.copy(deep=True)
    print(f"Initial shape: {df.shape}")

    # Load the WHO classification mapping from the Excel file.
    # Ensure the path is correct for your environment.
    # WHO_mapping = pd.read_excel("../../stains_data_cleaner/backup/Ovary Tumours from WHO Bluebook.xlsx",
    #                             index_col=0, skiprows=2).reset_index(drop=True)

    # --- 1. Prepare Mappers & Clean Data ---

    # Defensive cleaning: remove leading/trailing whitespace from mapping data.
    for col in ['Tumour Class', 'Category 2', 'Category 1']:
        if WHO_mapping[col].dtype == 'object':
            WHO_mapping[col] = WHO_mapping[col].str.strip()

    # Also clean the input column to ensure reliable matching.
    matched_tumour_clean = df['matched_tumour'].str.strip()

    # Level 0 mappers (from Tumour Class up to Cat1 and Cat2)
    class_to_cat2 = WHO_mapping.set_index('Tumour Class')['Category 2'].to_dict()
    class_to_cat1 = WHO_mapping.set_index('Tumour Class')['Category 1'].to_dict()

    # Level 1 mapper (from Category 2 up to Cat1)
    # Drop duplicates to ensure a one-to-one mapping from Cat 2 to Cat 1.
    cat2_map_df = WHO_mapping.drop_duplicates(subset=['Category 2'])
    cat2_to_cat1 = cat2_map_df.set_index('Category 2')['Category 1'].to_dict()

    # Level 2 lookup set (for identifying Category 1 terms)
    all_cat1_values = set(WHO_mapping['Category 1'].unique())

    # --- 2. Initialize New Columns ---

    # Using pd.Series with a specified dtype to avoid future warnings.
    df['tumour_class'] = pd.Series(dtype='object')
    df['category_2'] = pd.Series(dtype='object')
    df['category_1'] = pd.Series(dtype='object')
    df['mt_level'] = pd.Series(dtype=float)  # Use float to allow for NaN initially

    # --- 3. Map Data Based on Hierarchy ---

    # Priority 1: Check if matched_tumour is a Tumour Class (Level 0)
    is_class_mask = matched_tumour_clean.isin(class_to_cat1.keys())

    df.loc[is_class_mask, 'mt_level'] = 0
    df.loc[is_class_mask, 'tumour_class'] = matched_tumour_clean[is_class_mask]
    df.loc[is_class_mask, 'category_2'] = matched_tumour_clean[is_class_mask].map(class_to_cat2)
    df.loc[is_class_mask, 'category_1'] = matched_tumour_clean[is_class_mask].map(class_to_cat1)

    # Priority 2: Check remaining rows to see if matched_tumour is a Category 2 (Level 1)
    remaining_mask = df['mt_level'].isna()
    is_cat2_mask = remaining_mask & matched_tumour_clean.isin(cat2_to_cat1.keys())

    df.loc[is_cat2_mask, 'mt_level'] = 1
    # 'tumour_class' is left as NaN because it's ambiguous (one Cat 2 can have many classes).
    df.loc[is_cat2_mask, 'category_2'] = matched_tumour_clean[is_cat2_mask]
    df.loc[is_cat2_mask, 'category_1'] = matched_tumour_clean[is_cat2_mask].map(cat2_to_cat1)

    # Priority 3: Check remaining rows to see if matched_tumour is a Category 1 (Level 2)
    remaining_mask = df['mt_level'].isna()
    is_cat1_mask = remaining_mask & matched_tumour_clean.isin(all_cat1_values)

    df.loc[is_cat1_mask, 'mt_level'] = 2
    # 'tumour_class' and 'tumour_cat_2' are left as NaN because they are ambiguous.
    df.loc[is_cat1_mask, 'category_1'] = matched_tumour_clean[is_cat1_mask]

    print(f"Final shape after enrichment: {df.shape}")
    return df

