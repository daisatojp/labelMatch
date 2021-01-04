# PointMatcher

 PointMatcher is a graphical corresponding point annotation tool. In computer vision, normally we decide correspondences of points automatically by a feature point extraction algorithm (e.g. SIFT) and a feature matching algorithm (e.g. Brute Force). But when you want to do it manually, you can use this tool!

<p align="center"><img src="demo/main_window.jpg" alt="demo image" width="460"></img></p>

## Requirements

* Python 3
* PyQT5

## How to Use

download or clone repository

```bash
clone https://github.com/daisatojp/PointMatcher.git --recursive
```

Install dependencies

```bash
pip install pyqt5
```

Run

```bash
python PointMatcher.py
```

## Quick Start (Examle)

If you don't have annotation file (matching file)

1. File > New File
2. choose directory that stores images
3. choose annotation file to be saved
4. click ok
5. let's annotation

If you have annotation file

1. click "Open Dir" from toolbox
2. choose directory that stores images
3. click "Open File" from toolbox
4. choose annotation file
5. let's annotation

## Annotation format

```text
{
  "views": [
    {
      "id_view": 0,
      "filename": ["dirname", "dirname", ..., "filename"],
      "keypoints": [
        [x1, y1],
        [x2, y2],
        ...
      ]
    }
    ...
  ],
  "pairs": [
    {
      "id_view_i": 0,
      "id_view_j": 1,
      "matches": [
        [0, 0],
        [2, 3],
        ...
      ]
    }
    ...
  ]
}
```

## License

[MIT license] (https://github.com/daisatojp/PointMatcher/blob/master/LICENSE)

## Acknowledgment

* [labelimg](https://github.com/tzutalin/labelImg) as a reference
* [Chateau de Sceaux Image Dataset](https://github.com/openMVG/ImageDataset_SceauxCastle) to test software
