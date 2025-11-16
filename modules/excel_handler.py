"""
Excel Handler Module
Handles reading Instagram URLs from Excel and writing transcriptions back.
"""

import pandas as pd
from typing import List, Dict, Optional
import os


class ExcelHandler:
    """Handles all Excel file operations for reading URLs and writing transcriptions."""

    def __init__(self, file_path: str):
        """
        Initialize the Excel handler.

        Args:
            file_path: Path to the Excel file
        """
        self.file_path = file_path
        self.df = None

    def read_links_from_excel(self, column_name: str = "Instagram URL") -> List[str]:
        """
        Read Instagram URLs from Excel file.

        Args:
            column_name: Name of the column containing Instagram URLs

        Returns:
            List of Instagram URLs

        Raises:
            FileNotFoundError: If Excel file doesn't exist
            ValueError: If specified column doesn't exist
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Excel file not found: {self.file_path}")

        try:
            # Read Excel file
            self.df = pd.read_excel(self.file_path)
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {str(e)}")

        # Check if column exists
        if column_name not in self.df.columns:
            raise ValueError(
                f"Column '{column_name}' not found in Excel file. "
                f"Available columns: {', '.join(self.df.columns)}"
            )

        # Get URLs and filter out empty values
        urls = self.df[column_name].dropna().tolist()

        # Convert to strings and strip whitespace
        urls = [str(url).strip() for url in urls]

        return urls

    def write_transcriptions_to_excel(
        self,
        transcriptions: Dict[str, str],
        column_name: str = "Transcription",
        output_path: Optional[str] = None
    ) -> str:
        """
        Write transcriptions back to Excel file.

        Args:
            transcriptions: Dictionary mapping URLs to transcriptions
            column_name: Name of the column to write transcriptions to
            output_path: Optional custom output path. If None, overwrites original file

        Returns:
            Path to the saved Excel file

        Raises:
            ValueError: If DataFrame hasn't been loaded yet
        """
        if self.df is None:
            raise ValueError("Excel file hasn't been loaded yet. Call read_links_from_excel first.")

        # Create transcription column if it doesn't exist
        if column_name not in self.df.columns:
            self.df[column_name] = ""

        # Map transcriptions to the DataFrame
        # Assuming we have a URL column to match against
        url_column = None
        for col in ["Instagram URL", "URL", "Link", "instagram_url", "url", "link"]:
            if col in self.df.columns:
                url_column = col
                break

        if url_column is None:
            raise ValueError("Could not find URL column in Excel file")

        # Update transcriptions for matching URLs
        for idx, row in self.df.iterrows():
            url = str(row[url_column]).strip()
            if url in transcriptions:
                self.df.at[idx, column_name] = transcriptions[url]

        # Determine output path
        save_path = output_path if output_path else self.file_path

        # Save to Excel
        try:
            self.df.to_excel(save_path, index=False, engine='openpyxl')
        except Exception as e:
            raise ValueError(f"Error writing to Excel file: {str(e)}")

        return save_path

    def get_dataframe(self) -> pd.DataFrame:
        """
        Get the loaded DataFrame.

        Returns:
            The loaded pandas DataFrame

        Raises:
            ValueError: If DataFrame hasn't been loaded yet
        """
        if self.df is None:
            raise ValueError("Excel file hasn't been loaded yet. Call read_links_from_excel first.")
        return self.df

    def add_status_column(self, status_data: Dict[str, str], column_name: str = "Status"):
        """
        Add a status column to track download/transcription status.

        Args:
            status_data: Dictionary mapping URLs to status messages
            column_name: Name of the status column
        """
        if self.df is None:
            raise ValueError("Excel file hasn't been loaded yet. Call read_links_from_excel first.")

        # Create status column if it doesn't exist
        if column_name not in self.df.columns:
            self.df[column_name] = ""

        # Find URL column
        url_column = None
        for col in ["Instagram URL", "URL", "Link", "instagram_url", "url", "link"]:
            if col in self.df.columns:
                url_column = col
                break

        if url_column is None:
            raise ValueError("Could not find URL column in Excel file")

        # Update status for matching URLs
        for idx, row in self.df.iterrows():
            url = str(row[url_column]).strip()
            if url in status_data:
                self.df.at[idx, column_name] = status_data[url]


# Standalone functions for simple use cases
def read_urls_from_excel(file_path: str, column_name: str = "Instagram URL") -> List[str]:
    """
    Simple function to read URLs from Excel without using the class.

    Args:
        file_path: Path to Excel file
        column_name: Column containing URLs

    Returns:
        List of URLs
    """
    handler = ExcelHandler(file_path)
    return handler.read_links_from_excel(column_name)


def write_transcriptions(
    file_path: str,
    transcriptions: Dict[str, str],
    output_path: Optional[str] = None
) -> str:
    """
    Simple function to write transcriptions without using the class directly.

    Args:
        file_path: Path to input Excel file
        transcriptions: Dictionary of URL -> transcription mappings
        output_path: Optional output path

    Returns:
        Path to saved file
    """
    handler = ExcelHandler(file_path)
    handler.read_links_from_excel()  # Load the file first
    return handler.write_transcriptions_to_excel(transcriptions, output_path=output_path)
