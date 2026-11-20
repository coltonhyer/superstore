from label import normalize_label


assert normalize_label("  North Star  ") == "north star"
