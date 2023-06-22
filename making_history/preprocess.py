import click
import cv2 as cv
import glob
import math

# somewhat tuned options
LINE_THICKNESS = 20 
WHITE = (255, 255, 255)
MIN_LINE_LEN = 200
MAX_LINE_GAP = 1000 # line segments are merged if they are closer than this
HOUGH_THRESHOLD = 10
KERNEL_W = 1
KERNEL_H_NOISE = 5
ITERS = 3
# kernel should be larger than letter height to avoid interpreting letters as lines
KERNEL_H_LINES = 100


def read_image_files(table_path):
    img_color = cv.imread(table_path, cv.IMREAD_COLOR)
    img = cv.cvtColor(img_color, cv.COLOR_BGR2GRAY)
    img = cv.bitwise_not(img)
    thresh = cv.threshold(img, 30, 255, cv.THRESH_BINARY)[1]
    return thresh, img_color


def vertical_lines_one_tab(table_path):

    thresh, img_color = read_image_files(table_path)

    # Close small gaps in lines  
    kernel_line_noise = cv.getStructuringElement(cv.MORPH_RECT, (KERNEL_W, KERNEL_H_NOISE))
    morphology_img = cv.morphologyEx(thresh, cv.MORPH_CLOSE, kernel_line_noise, iterations=ITERS)
   
    # Defining a vertical kernel to detect all vertical lines of image
    ver_kernel = cv.getStructuringElement(cv.MORPH_RECT, (KERNEL_W, KERNEL_H_LINES))   
    vertical_lines = cv.morphologyEx(morphology_img, cv.MORPH_OPEN,  ver_kernel, iterations=1)
    
    lines = cv.HoughLinesP(image=vertical_lines, rho=1, theta=math.pi / 180, threshold=HOUGH_THRESHOLD, lines=None, minLineLength=MIN_LINE_LEN, maxLineGap=MAX_LINE_GAP)

    white_out(img_color, lines)

    return img_color

def white_out(img_color, lines):
    if lines is not None:
        for  i,line in enumerate(lines):
            l = line[0]
            cv.line(img_color, (l[0], l[1]), (l[2], l[3]), WHITE, LINE_THICKNESS)

def erode_image(img, erosion_kernel=(3,3), n_erosions=1):
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    inverted = cv.bitwise_not(img_gray)
    img_inverted = cv.erode(inverted, kernel=erosion_kernel, iterations=n_erosions)
    img_gray_eroded_only = cv.bitwise_not(img_inverted)
    return img_gray_eroded_only


def prepare_images(input_dir, output_dir, suffix='.tiff'): 
    tiff_files = glob.glob(f'{input_dir}/*{suffix}')
    for tiff_file in tiff_files:
        fixed_img = vertical_lines_one_tab(tiff_file)
        #cv.imwrite(tiff_file.replace(input_dir, output_dir).replace('.tiff', '_not_eroded.tiff'), fixed_img)
        eroded_img = erode_image(fixed_img)
        cv.imwrite(tiff_file.replace(input_dir, output_dir), eroded_img)



@click.command()
@click.option(
    "--input", default="MATRICES", help="Path to matrix directory"
)
@click.option(
    "--output", default="PREPROCESSED", help="Path to directory for OCR results"
)
@click.option(
    "--file_type",
    default=".tiff",
    help="File ending (type) of input files. Necessary to provide ff not .tiff (e.g. .png))",
)

def main(input, output, file_type):
    """
    Runs preprocessing on images
    """
    print(f"Will read input files from {input}")
    print(f"Will write output files to {output}")
    print(f"Assumes input data (table images) is of type:{file_type}")
    prepare_images(input, output, suffix=file_type)

 

if __name__ == "__main__":
    main()
