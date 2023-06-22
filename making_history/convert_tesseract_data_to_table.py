import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from making_history.table_structure.table_structure import Cell, TableSection
import operator

pd.set_option("display.max_columns", 500)


class TesseractToTable:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.read_csv(file_path, dtype={"text": str}, keep_default_na=False)
        # for detecting columns(/rows) should be evaluated
        PROMINENCE_ROW = 5
        PROMINENCE_COL = 20
        DISTANCE_ROW = 40
        DISTANCE_COL = 50

        self.COL_DETECT_HEIGHTS = [2, 5, 7, 8, 9, 10]
        self.window_size = len(self.COL_DETECT_HEIGHTS)

        self.df = self.df[self.df["text"] != " "]
        self.df = self.df[self.df["conf"] != -1]
        self.df["mid_row"] = self.df["top"] + self.df["height"] // 2
        self.df["mid_col"] = self.df["left"] + self.df["width"] // 2
        self.df["right"] = self.df["left"] + self.df["width"]
        self.df["bottom"] = self.df["top"] + self.df["height"]
        density_row, density_col = self.get_density()
        self.peaks_col, _ = find_peaks(
            density_col, prominence=PROMINENCE_COL, distance=DISTANCE_COL
        )
        self.peaks_row, _ = find_peaks(
            density_row, prominence=PROMINENCE_ROW, distance=DISTANCE_ROW
        )

        self.add_line_order()



    def add_line_order(self):
        self.line_order = sorted(
            list(set(zip(self.df["par_num"], self.df["line_num"]))),
            key=operator.itemgetter(0, 1),
        )
        self.df["row_number"] = self.df.apply(
            lambda x: self.get_row_number_df(x.par_num, x.line_num), axis=1
        )



    def preprocess_text(self, remove_pipes, merge_dash, text):
        # eg. borde cellerna hanteras som rader 
        if remove_pipes:
            text = text.replace("|", " ")
        if merge_dash:
            text = text.replace("---", "-")
            text = text.replace("--", "-")
        return text

    def get_table_section(self, do_print=False, remove_pipe=False, merge_dash=False):
        cells = []
        for _, row in self.df.iterrows():
            current_text = row["text"]
            current_text = self.preprocess_text(remove_pipe, merge_dash, current_text)

            if row["text"] != "|" and current_text != "":
                row_index = self.get_row(row)
                col_index = self.get_closest_column(row)
                cells.append(
                    Cell(
                        row_index,
                        row_index + 1,
                        col_index,
                        col_index + 1,
                        current_text,
                        row["conf"],
                    )
                )

        ts = TableSection()
        ts.add_cells(cells)
        if do_print:
            ts.debug_print_table(print_conf=True)
        return ts

    def get_closest_column(self, df_row):
        current_col_val = df_row["mid_col"]
        min_diff = 999999
        min_index = -1
        for i, peak in enumerate(self.peaks_col):
            diff = abs(peak - current_col_val)
            if diff < min_diff:
                min_diff = diff
                min_index = i
        return min_index

    def get_row_number_df(self, par_num, line_num):
        return self.line_order.index((par_num, line_num))

    def get_row(self, df_row):
        return self.line_order.index((df_row["par_num"], df_row["line_num"]))

    def get_density(self):
        max_right = self.df["right"].max()
        max_bottom = self.df["bottom"].max()

        density_col = [0] * max_right
        density_row = [0] * max_bottom
        for _, row in self.df.iterrows():
            start_val_column = row["right"] - self.window_size
            if row["text"] != "|":
                for w in range(self.window_size):
                    density_col[start_val_column + w] += self.COL_DETECT_HEIGHTS[w]

            start_val_row = row["top"]
            for h in range(row["height"]):
                density_row[start_val_row + h] += 1
        plt.plot(range(len(density_col)), density_col, c="r")

        return density_row, density_col


