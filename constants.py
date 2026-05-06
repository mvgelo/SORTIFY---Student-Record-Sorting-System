import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

BG_MAIN = ("#f0f2f5", "#121212")
BG_SIDEBAR = ("#ffffff", "#181818")
CARD_BG = ("#ffffff", "#282828")
TABLE_HEADER_BG = ("#e5e7eb", "#1f1f1f")
ALGO_INFO_BG = ("#e8f5e9", "#1e3024")
TEXT_PRIMARY = ("#191414", "#ffffff")
TEXT_SECONDARY = ("#535353", "#b3b3b3")
PRIMARY_BTN = ("#1db954", "#1ed760")
PRIMARY_HOVER = ("#17a149", "#1db954")
NEUTRAL_BTN = ("#e5e7eb", "#3e3e3e")
NEUTRAL_HOVER = ("#d1d5db", "#535353")
DANGER_BTN = ("#fecaca", "#7f1d1d")
DANGER_HOVER = ("#f87171", "#991b1b")
DANGER_TEXT = ("#7f1d1d", "#fecaca")

FONT_H1 = ("Segoe UI Variable", 24, "bold")
FONT_H2 = ("Segoe UI Variable", 18, "bold")
FONT_BODY = ("Segoe UI Variable", 13, "normal")
FONT_SMALL = ("Segoe UI Variable", 12, "normal")

P = 12
ROW_HEIGHT = 34
VISIBLE_ROWS = 10
TABLE_HEIGHT = ROW_HEIGHT * VISIBLE_ROWS + 18
BTN_H = 36
EMPTY_SORTED_ROWS = 2
COL_WEIGHTS_NO_ACTION = [2, 4, 2, 2, 4, 2]
COL_WEIGHTS_WITH_ACTION = [2, 4, 2, 2, 4, 2, 2]
COL_WEIGHTS_ARCHIVED = [2, 4, 2, 2, 4, 2, 3]

SORT_KEY_BY_COLUMN = {
    "Name": 1,
    "ID": 0,
    "Age": 2,
    "GWA": 3,
    "Year": 5,
}

ALGO_INFO = {
    "Quick Sort": {
        "desc": "Divide-and-conquer algorithm that partitions data around a pivot and recursively sorts both sides.",
        "time": "Best: O(n log n) | Average: O(n log n) | Worst: O(n^2)",
        "space": "Best: O(log n) | Average: O(log n) | Worst: O(n)",
    },
    "Bubble Sort": {
        "desc": "Simple comparison algorithm that repeatedly swaps adjacent out-of-order elements until sorted.",
        "time": "Best: O(n) | Average: O(n^2) | Worst: O(n^2)",
        "space": "Best: O(1) | Average: O(1) | Worst: O(1)",
    },
    "Insertion Sort": {
        "desc": "Builds the sorted portion one element at a time by inserting each item into its correct position.",
        "time": "Best: O(n) | Average: O(n^2) | Worst: O(n^2)",
        "space": "Best: O(1) | Average: O(1) | Worst: O(1)",
    },
    "Merge Sort": {
        "desc": "Stable divide-and-conquer algorithm that splits input, recursively sorts parts, then merges them.",
        "time": "Best: O(n log n) | Average: O(n log n) | Worst: O(n log n)",
        "space": "Best: O(n) | Average: O(n) | Worst: O(n)",
    },
}