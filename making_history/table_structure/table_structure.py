from dataclasses import dataclass


@dataclass
class Cell:
    """A cell in a table. The cell has a value, optionally a confidence level, and a position in the table."""

    from_row: int
    to_row: int
    from_col: int
    to_col: int
    value: str
    confidence: float = None

    def __post_init__(self):
        self.preprocess_value()

    def preprocess_value(self):
        self.value = self.value.replace(",", "")
        self.value = self.value.replace(".", "")

    def equal_value(self, other_cell):
        return self.value == other_cell.value

    def equal_value_and_position(self, other_cell):
        if self.value != other_cell.value:
            return False
        if self.from_row != other_cell.from_row:
            return False
        if self.from_col != other_cell.from_col:
            return False
        if self.to_row != other_cell.to_row:
            return False
        if self.to_col != other_cell.to_col:
            return False
        return True

    def equal_value_and_row(self, other_cell):
        if self.value != other_cell.value:
            return False
        if self.from_row != other_cell.from_row:
            return False
        if self.to_row != other_cell.to_row:
            return False
        return True

    def equal_value_and_col(self, other_cell):
        if self.value != other_cell.value:
            return False
        if self.to_col != other_cell.to_col:
            return False
        if self.from_col != other_cell.from_col:
            return False
        return True


class TableSection:
    """A section of a table. The section has a list of cells, and a position in the table.
    A section can correspond to the "matrix" section of a table
    The offset is used to keep track of the position of the section in the table, it there is more than one section in the table.
    """

    def __init__(self, row_offset=0, col_offset=0):
        self.cells = []
        self.row_offset = row_offset
        self.col_offset = col_offset
        self.rows = {}
        self.columns = {}
        self.row_numbers = []

    def get_size(self):
        return len(self.rows), len(next(iter(self.rows.values())))

    def pass_cell_check(cell):
        return True

    def check_cells(self, cells):
        return [cell for cell in cells if self.pass_cell_check(cell)]

    def get_row_as_string(self, row):
        return " ".join([cell.value for cell in row])

    def check_rows(self, min_cells=10):
        # warns if a row has < min_cells cells
        # could indicate noise interpreted as a row
        for row_number, cells in self.rows.items():
            if len(cells) < min_cells:
                print(
                    f"**** possible bad row (SHORT) {len(cells)} cells. ROW num: {row_number}",
                    self.get_row_as_string(cells),
                )
                print(row_number)


    def add_cells(self, cell_list):
        for cell in cell_list:
            self.cells.append(cell)
            from_row = cell.from_row
            if from_row in self.rows:
                self.rows[from_row].append(cell)
            else:
                self.rows[from_row] = [cell]
                self.row_numbers.append(from_row)
        self.check_rows()

    def get_all_values(self):
        return [cell.value for cell in self.cells]

    def get_cells_in_row(self, row_number):
        return [cell for cell in self.cells if cell.only_in_row(row_number)]

    def get_cells_in_column(self, column_number):
        return [cell for cell in self.cells if cell.only_in_column(column_number)]

    def create_table_from_annotations():
        pass

    def get_cell_line(self, cell, print_conf, print_pos):
        if not print_pos:
            return f"[{cell.value}]"

        if print_conf:
            return f" [{cell.value} ({cell.from_row}:{cell.to_row},{cell.from_col}:{cell.to_col}) *{cell.confidence}*] "

        else:
            return f"  [{cell.value} ({cell.from_row}:{cell.to_row},{cell.from_col}:{cell.to_col})] "

    def debug_print_table(self, max_rows=None, print_conf=False, print_pos=True):
        # för enkel tabell endast
        print("---------------------------------------------------------------")
        sorted_rows = sorted(self.row_numbers)

        for i, row in enumerate(sorted_rows):
            if max_rows is None or i < max_rows:
                current_row = self.rows[row]
                current_row = sorted(current_row, key=lambda x: x.from_col)
                for cell in current_row:
                    print(self.get_cell_line(cell, print_conf, print_pos), end=" ")
                print("\n")
        print("---------------------------------------------------------------")

    def get_table_as_text_lines(self):
        sorted_rows = sorted(self.row_numbers)
        text_lines = []
        for i, row in enumerate(sorted_rows):
            current_line = []
            current_row = self.rows[row]
            current_row = sorted(current_row, key=lambda x: x.from_col)
            for cell in current_row:
                current_line.append(cell.value)

            text_lines.append(" ".join(current_line))

        return text_lines

    def write_csv(self, filename, sep="\t"):
        with open(filename, mode="w", encoding="utf8") as out_file:
            sorted_rows = sorted(self.row_numbers)

            for i, row in enumerate(sorted_rows):
                current_row = self.rows[row]
                current_row = sorted(current_row, key=lambda x: x.from_col)
                for cell in current_row[:-1]:
                    out_file.write(f"{cell.value}{sep}")

                out_file.write(f"{current_row[-1].value}\n")




class TablePage:
    """A table page can hold one page of a multi-page table. The table page can consist of several table sections"""

    def __init__(self, table_sections, page_nr):
        self.table_parts = table_sections
        self.page_nr = page_nr
        # offsets


class TableDocument:
    """A table document can hold a complete table spanning several pages"""

    def __init__(self, table_pages):
        self.table_pages = table_pages
