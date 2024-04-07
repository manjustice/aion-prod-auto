from app.production_window import ProductionWindow
from app.utils import switch_to_window


def main():
    switch_to_window("Image Viewer")
    ProductionWindow()
    switch_to_window("pycharm ")


if __name__ == "__main__":
    main()
