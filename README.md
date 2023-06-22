# Table OCR, some work in progress
Source data:
Bidrag till Sveriges officiella statistik, [BiSOS](https://www.scb.se/hitta-statistik/aldre-statistik/innehall/bidrag-till-sveriges-officiella-statistik/)

* Poetry project: [Instructions for installation](https://python-poetry.org/docs/)
* Tesseract
[Instructions for installation](https://tesseract-ocr.github.io/tessdoc/Installation.html),
[User manual](https://tesseract-ocr.github.io)
* Scantailor
[Instructions for installation](https://github.com/4lex4/scantailor-advanced)

TODO: Docker


## Overview
This repo contains an OCR (Optical Character Recognition) model adapted to scanned BiSOS tables. The model is a Tesseract model and can be used as any Tesseract model. 

To get good performance from the model, it is necessary to preprocess the table images, and this is done in two steps. First, **Scantailor** is used (see below), and next the script `preprocess.py` should be applied to the Scantailor data.

Next, `run_OCR.py` will apply the OCR to the preprocessed data. The `run_OCR.py`script provides two types of output, the Tesseract output (first few rows):

```
level,page_num,block_num,par_num,line_num,word_num,left,top,width,height,conf,text
1,1,0,0,0,0,0,0,5113,5064,-1.0,
2,1,1,0,0,0,43,81,5051,4940,-1.0,
3,1,1,1,0,0,67,81,5027,904,-1.0,
4,1,1,1,1,0,67,81,5026,88,-1.0,
5,1,1,1,1,1,67,84,146,67,89.164436,"2,031"
5,1,1,1,1,2,310,81,155,66,85.287979,"2,460"
5,1,1,1,1,3,585,81,101,52,96.385529,424
```

and .tsv files as tab separated rows and columns:

```
2031	2460	424	607	1058	988	1187	1319	4735	548	2465	24	728	1860	4848	8384	7070	9322	7202	23594	90	210	213
19	25	23	44	13	17	12	16	78	16	44	6	29	72	66	154	91	177	194	462	7	7	22
7	12	1	1	3	3	7	9	24	3	13	-	3	9	20	41	32	46	34	112	1	3	4
9	19	-	-	7	5	-	-	-	7	10	-	2	9	23	36	34	46	9	89	1	2	-
```

...xlsx-files with warnings...

![Process overview][pro]

[pro]: FIGS/processes.png "Overview of process"

### Prepare images with Scantailor

Scantailor provides tools for processing scanned images in six steps. To recreate the training/test data starting with scanned images (600 dpi). 

1. **Fix orientation** Rotate image if necessary.
1. **Split pages** If you have a book spread of two pages, split it down the middle, do not remove extra margins. If you have single pages, make sure that the full page is included.
2. **Deskew** Tilt the image if it is not horizontal, strive for straight vertical lines.
3. **Select content** Crop the image so that only the "matrix" part remains (containing the numbers). Do not include columns with row numbers or text columns. Vertical lines at the top or bottom of the image can/should be excluded if possible.
4. **Margins** Set margins to 0 (or some small number). If you have more than one page, select: Apply to all pages. Check the result for all pages.
6. **Output** Select "Black and White" under mode, and keep default settings. If the image is warped in the margin, you can experiment with "Dewarping", there are options for *Auto*, *Marginal* and *Manual*. 

The processed images will be saved in an "out" folder. Copy these to the MATRICES folder.

 

## Fine-tuned tesseract OCR models
Models are available in the models folder...
Training data will be made available...
## Usage
1. Preprocess scanned images using Scantailor
2. Run the preprocess.py script. The script removes vertical lines from the tabels and erodes the text.
The script assumes that image files in .tiff format can be found in a folder *MATRICES*, and that there is a folder *PREPROCESSED* which the output can be written to. 

`python preprocess.py`

If you want to change any of these options:
```
Options:
  --input TEXT      Path to matrix directory
  --output TEXT     Path to directory for OCR results
  --file_type TEXT  File ending (type) of input files. Necessary to provide ff
                    not .tiff (e.g. .png))
  --help            Show this message and exit.
```

3. Run the run_OCR.py script.  This script reads from the *PREPROCESSED* folder and writes to the *OCR_OUTPUT* folder
`python run_OCR.py`

```
Usage: run_OCR.py [OPTIONS]

  Runs OCR on preprocessed images

Options:
  --input TEXT      Path to directory with preprocessed images
  --output TEXT     Path to directory for OCR results
  --model TEXT      Path to directory containing an OCR model named
                    swe.traineddata
  --file_type TEXT  File ending (type) of input files. Necessary to provide ff
                    not .tiff (e.g. .png))
  --help            Show this message and exit.
```



![Scanned book spread][spread]

[spread]: FIGS/1900_original.jpg "Example of scanned book spread"






