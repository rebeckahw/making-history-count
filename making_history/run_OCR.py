import pytesseract
import click
import cv2 as cv
import os
from pathlib import Path
import glob
from making_history.convert_tesseract_data_to_table import TesseractToTable


def create_output_dirs(data_dir):
    out_dir_data = os.path.join(data_dir, "AS_DATA")
    out_dir_tsv = os.path.join(data_dir, "AS_TSV")
    Path(out_dir_data).mkdir(parents=True, exist_ok=True)
    Path(out_dir_tsv).mkdir(parents=True, exist_ok=True)
    return out_dir_data, out_dir_tsv

def write_as_tsv(tesseract_file, tsv_file):
    ttt = TesseractToTable(tesseract_file)
    ts = ttt.get_table_section(do_print=False, remove_pipe=False, merge_dash=True)
    ts.write_csv(tsv_file)


def write_as_data(image_file_paths, tiff_dir, data_dir, conf, image_suffix):
    for input_tiff in image_file_paths:
        img_cv = cv.imread(input_tiff)
        img = cv.cvtColor(img_cv, cv.COLOR_BGR2GRAY)

        out_dir, tsv_dir = create_output_dirs(data_dir)
        print(f"*** Processing {input_tiff} ***")
        data_path = input_tiff.replace(tiff_dir, out_dir).replace(image_suffix, ".csv")
        tsv_path = input_tiff.replace(tiff_dir, tsv_dir).replace(image_suffix, ".tsv")

        as_data = pytesseract.image_to_data(img, config=conf, output_type="data.frame")
        as_data.to_csv(data_path, index=False)
        write_as_tsv(data_path, tsv_path)


def check_dirs_exists(input_dir, output_dir):
    if not os.path.isdir(input_dir):
        print(f"Input directory {input_dir} does not exist")
        exit(1)
    if not os.path.isdir(output_dir):
        print(f"Output directory {output_dir} does not exist")
        exit(1)
    print("Directories exist")


def check_model_file_exists(model_file):
    if not os.path.isfile(model_file):
        print(f"Model file {model_file} does not exist")
        exit(1)
    print("Model file exists")



def check_that_input_dir_contains_image_files(input_dir, file_suffix=".tiff"):
    no_image_files = True
    for file in os.listdir(input_dir):
        if file.endswith(file_suffix):
            no_image_files = False
            break
    if no_image_files:
        print(f"Input directory {input_dir} contains non-image files of type: {file_suffix}")
        exit(1)
    print(f"Input directory contains {file_suffix} files")


@click.command()
@click.option(
    "--input", default="PREPROCESSED", help="Path to directory with preprocessed images"
)
@click.option(
    "--output", default="OCR_OUTPUT", help="Path to directory for OCR results"
)
@click.option(
    "--model",
    default="models/AUGMENTED_26_5000/",
    help="Path to directory containing an OCR model named swe.traineddata",
)
@click.option(
    "--file_type",
    default=".tiff",
    help="File ending (type) of input files. Necessary to provide ff not .tiff (e.g. .png))",
)
def main(input, output, model, file_type):
    """
    Runs OCR on preprocessed images
    """
    print(f"Will read input files from {input}")
    print(f"Will write output files to {output}")
    print(f"Will use model swe.trainddata in directory {model}")
    print(f"Assumes input data (table images) is of type:{file_type}")
    config = f"--psm 6 -l swe --tessdata-dir {model}"
    print("\n...doing some checks...")
    check_dirs_exists(input, output)
    check_model_file_exists(f'{model}/swe.traineddata')
    check_that_input_dir_contains_image_files(input, file_type)
    print("\n...done with checks...")
    image_file_paths = glob.glob(f'{input}/*{file_type}')
    print("\n...running OCR...")
    write_as_data(image_file_paths, input, output, config, file_type)


if __name__ == "__main__":
    main()
