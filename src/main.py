import rasterio
from affine import loadsw

from src import PROJECT_ROOT_FOLDER

if __name__ == '__main__':
    with open(PROJECT_ROOT_FOLDER / "tmp" / "japan_out_main.pgw") as pgw:
        pgw_file = pgw.read()
        a = loadsw(pgw_file)
    with rasterio.open(PROJECT_ROOT_FOLDER / "tmp" / "japan_out_main.png", "r") as src:
        src_transform = src.transform
        print(a, src_transform)
        print(a, src_transform)
        print("a, src_tranform")
