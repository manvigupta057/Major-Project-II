import pandas as pd
import os
import re

from config import Config

CSV_PATH = Config.CSV_PATH

class DataEngine:
    def __init__(self):
        if os.path.exists(CSV_PATH):
            self.df = pd.read_csv(CSV_PATH)
            # Ensure column names are clean
            self.df.columns = [c.strip() for c in self.df.columns]
        else:
            self.df = pd.DataFrame()
            print(f"Warning: CSV not found at {CSV_PATH}")

    def get_total_patients(self) -> int:
        return len(self.df)

    def count_condition(self, condition: str) -> int:
        """Returns the number of patients with a specific disease."""
        if 'disease' in self.df.columns:
            match = self.df[self.df['disease'].str.contains(condition, case=False, na=False)]
            return int(len(match))
        return 0

    def most_common_condition(self) -> str:
        """Returns the disease that appears most frequently."""
        if 'disease' in self.df.columns:
            return str(self.df['disease'].mode()[0])
        return "Unknown"

    def filter_patients(self, condition: str = None, gender: str = None) -> int:
        """Filters patients by disease or gender."""
        temp_df = self.df.copy()
        if condition and 'disease' in temp_df.columns:
            temp_df = temp_df[temp_df['disease'].str.contains(condition, case=False, na=False)]
        if gender and 'gender' in temp_df.columns:
            temp_df = temp_df[temp_df['gender'].str.lower() == gender.lower()]
        return int(len(temp_df))

# Singleton instance
data_engine = DataEngine()
