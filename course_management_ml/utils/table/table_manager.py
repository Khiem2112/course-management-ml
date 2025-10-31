from PyQt6.QtWidgets import (
    QTableWidgetItem,
    QTableWidget,
    QHeaderView
)
from PyQt6.QtCore import Qt
from utils.logger import get_class_logger

class TableWidgetManager:
    """
    Manager class to handle operations for a specific QTableWidget instance.
    """

    # Class attribute for shared settings across instances
    _table_settings_defaults = {
        'no_id': {'hidden_columns': ['id']}
    }

    def __init__(self, table_widget: QTableWidget):
        """
        Initialize the manager for a specific QTableWidget.

        Args:
            table_widget: The QTableWidget instance this manager will control.
        """
        if not isinstance(table_widget, QTableWidget):
            raise TypeError("Expected a QTableWidget instance.")
        self.table_widget = table_widget
        self.header_labels: list[str] | None = None # Store headers after loading
        self._configure_table() # Apply initial configuration
        self.logger = get_class_logger(__name__,self.__class__.__name__)

    def _configure_table(self):
        """Apply default table configuration to the managed table."""
        self.table_widget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_widget.verticalHeader().setVisible(False)
        # Optional: Add stretching for the last column
        # self.table_widget.horizontalHeader().setStretchLastSection(True)

    def load_data(self, data: list[dict],
                  header_labels: list[str] | None = None, table_type: str |None = None,
                  hidden_column_names: list[str] | None = None):
        """Load data (list of dictionaries) into the managed table widget.

        Args:
            data: List of dictionaries (each dict is a row).
            header_labels: Optional list of column headers to display. If None,
                           keys from the first data dictionary are used.
            table_type: Optional type of table for predefined settings (e.g., hiding columns).
            hidden_column_names: Optional explicit list of header names to hide.
                                 Overrides table_type settings if provided.
        """
        try:
        # Determine headers
          if data:
              # Use provided header_labels if they exist, otherwise use dict keys
              self.header_labels = header_labels if header_labels is not None else list(data[0].keys())
          elif header_labels is not None:
              # Data is empty, but headers were provided
              self.header_labels = header_labels
          else: # data is empty and no headers provided
              self.header_labels = []

          self._populate_data(data) # Uses self.header_labels
        

          # Determine columns to hide
          columns_to_hide = []
          if hidden_column_names is not None:
              columns_to_hide = hidden_column_names # Explicit list takes precedence
          elif table_type and table_type in self._table_settings_defaults:
              settings = self._table_settings_defaults[table_type]
              if 'hidden_columns' in settings:
                  columns_to_hide = settings['hidden_columns']

          if columns_to_hide and self.header_labels:
              self._hide_columns_by_name(columns_to_hide) # Uses self.header_labels
        except Exception as e:
          self.logger.warning(f"Loading data error: {e}")

    def _populate_data(self, data: list[dict]):
        """Populate managed table with data using stored headers."""
        self.table_widget.setRowCount(0)  # Clears table rows
        self.table_widget.setColumnCount(0) # Clears columns

        if not self.header_labels: # Cannot proceed without headers
             return

        self.table_widget.setColumnCount(len(self.header_labels))
        self.table_widget.setHorizontalHeaderLabels(self.header_labels)

        if not data: # If data is empty, headers are set, just return
            return

        self.table_widget.setRowCount(len(data))

        # Initialize column widths with header widths
        fm = self.table_widget.fontMetrics()
        column_widths = [0] * len(self.header_labels)

        for col, header in enumerate(self.header_labels):
            header_width = fm.horizontalAdvance(str(header))
            column_widths[col] = max(column_widths[col], header_width)

        # Populate rows and calculate content widths
        for row_index, row_dict in enumerate(data):
            for col_index, header in enumerate(self.header_labels):
                # Get data using header as key, default to "" if key missing
                cell_data = row_dict.get(header, "")
                item = QTableWidgetItem(str(cell_data))
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.table_widget.setItem(row_index, col_index, item)

                # Calculate content width using font metrics
                content_width = fm.horizontalAdvance(str(cell_data))
                column_widths[col_index] = max(column_widths[col_index], content_width)

        # Apply calculated widths with padding
        for col, width in enumerate(column_widths):
            padding = 40  # Adjust padding as needed
            final_width = min(width + padding, 400)  # Maximum width of 400px

            # Special handling for date columns by header name
            if any(date_keyword in self.header_labels[col].lower() for date_keyword in ['date', 'time']):
                final_width = max(final_width, 120)  # Minimum width for date columns

            self.table_widget.setColumnWidth(col, final_width)


    def _hide_columns_by_name(self, headers_to_hide: list[str]):
        """Hide specified columns by their header name in the managed table.

        Args:
            headers_to_hide: List of header names (strings) to hide.
        """
        if not self.header_labels:
             return # No headers to compare against

        header_indices = {header: i for i, header in enumerate(self.header_labels)}
        for header_name in headers_to_hide:
            col_index = header_indices.get(header_name)
            if col_index is not None:
                self.table_widget.setColumnHidden(col_index, True)

    def rearrange_columns_visual(self, first_header: str, second_header: str):
        """Visually moves the column with 'first_header' to be before 'second_header'.

           Note: Uses the currently stored self.header_labels.
                 Best used after data is populated.
        Args:
            first_header: The header name of the column to move earlier.
            second_header: The header name of the column it should be moved before.
        """
        if not self.header_labels or first_header not in self.header_labels or second_header not in self.header_labels:
            print(f"Warning: Headers missing or specified headers ('{first_header}', '{second_header}') not found.")
            return  # Skip if headers are missing

        header_view = self.table_widget.horizontalHeader()

        # --- Added Check ---
        if header_view is None:
            print("Error: Table widget's horizontal header is None. Cannot rearrange columns.")
            return
        # --- End Added Check ---

        # Get current VISUAL indices
        first_visual_idx = -1
        second_visual_idx = -1
        # Iterate through visual indices
        for visual_index in range(header_view.count()):
             logical_index = header_view.logicalIndex(visual_index)
             # Ensure logical_index is valid before accessing self.header_labels
             if 0 <= logical_index < len(self.header_labels):
                 current_header = self.header_labels[logical_index]
                 if current_header == first_header:
                     first_visual_idx = visual_index
                 elif current_header == second_header:
                     second_visual_idx = visual_index

        if first_visual_idx != -1 and second_visual_idx != -1 and first_visual_idx > second_visual_idx:
            # Move the section specified by its *current* visual index (first_visual_idx)
            # to the *target* visual index (second_visual_idx)
            header_view.moveSection(first_visual_idx, second_visual_idx)
        elif first_visual_idx == -1 or second_visual_idx == -1:
            print(f"Warning: Could not find visual index for '{first_header}' or '{second_header}'.")

    # --- Static utility method (doesn't depend on instance state) ---

    @staticmethod
    def swap_column_data(headers: list[str], data: list[dict], header1: str, header2: str):
        """
        Creates a *new* list of headers and a *new* list of data dictionaries
        with the values corresponding to header1 and header2 swapped.

        Args:
            headers: The original list of header names.
            data: The original list of data dictionaries.
            header1: The first header name to swap.
            header2: The second header name to swap.

        Returns:
             A tuple containing:
               - new_headers (list[str]): Headers with positions swapped.
               - new_data (list[dict]): Deep copy of data with values swapped in each dict.
             Returns original headers and data if headers are missing.
        """
        if not headers or header1 not in headers or header2 not in headers:
            return headers, data  # Return unchanged if columns are missing

        idx1 = headers.index(header1)
        idx2 = headers.index(header2)

        # Swap headers in a new list
        new_headers = headers[:] # Create a copy
        new_headers[idx1], new_headers[idx2] = new_headers[idx2], new_headers[idx1]

        # Create a deep copy of the data and swap values within each dictionary
        new_data = []
        for row_dict in data:
            new_row = row_dict.copy() # Shallow copy is enough if values are immutable
            # Swap values if both keys exist
            if header1 in new_row and header2 in new_row:
                 new_row[header1], new_row[header2] = new_row[header2], new_row[header1]
            elif header1 in new_row: # Handle case where only one key might exist
                 # Move value from header1 to header2, remove header1 (or set to None)
                 new_row[header2] = new_row.pop(header1)
            elif header2 in new_row:
                 # Move value from header2 to header1, remove header2 (or set to None)
                 new_row[header1] = new_row.pop(header2)
            new_data.append(new_row)

        return new_headers, new_data