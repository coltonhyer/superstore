from exporter import export_rows


assert export_rows(["first", "second"]) == "first\nsecond"
