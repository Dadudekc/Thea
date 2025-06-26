import traceback\ntry:\n    import gui.main_window as mw\nexcept Exception as e:\n    print(\ Error:\, e)\n    traceback.print_exc()
