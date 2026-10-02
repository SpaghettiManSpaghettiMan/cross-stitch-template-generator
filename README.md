# Cross-Stitch Template Generator

A Python command-line tool that converts an image into a cross-stitch template.

The program reduces an input image to a configurable stitch grid, groups the image colors using K-means clustering, matches the resulting colors against a built-in DMC-style palette, and generates PNG, SVG, and PDF versions of the pattern.

## Features

- Convert JPG, PNG, and other image formats supported by Pillow
- Set the pattern width in stitches
- Optionally set the pattern height
- Automatically calculate height from the source image when omitted
- Automatically determine a color count or specify one manually
- Reduce image colors using K-means clustering
- Match colors using CIE LAB color space
- Generate:
  - PNG chart with colors, grid, symbols, and thread legend
  - SVG chart for scalable viewing
  - PDF pattern for printing
- Print a thread list showing DMC code, thread name, and stitch count

## Requirements

- Python 3.10+
- Pillow
- NumPy
- scikit-learn
- ReportLab

## Installation

Clone or download the repository, then create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
