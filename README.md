# PointMatcher

 PointMatcher is a graphical corresponding point annotation tool. In computer vision, normally we decide correspondences of points automatically by a feature point extraction algorithm (e.g. SIFT) and a feature matching algorithm (e.g. Brute Force). But when you want to do it manually, you can use this tool!

<p align="center"><img src="demo/main_window.jpg" alt="demo image" width="460"></img></p>

## Requirements

* Python3
* PyQT5

## How to Start

### with Binary (Windows only)

You can use binary file. Please download from the [Release](https://github.com/daisatojp/PointMatcher/releases).

### with pip (Any OS)

I haven't made binary for other than Windows yet. Please download through pip.

```bash
conda create --name=PointMatcher python=3.7
conda activate PointMatcher
pip install PointMatcher
PointMatcher
```

### with git-clone (Any OS)

```bash
git clone https://github.com/daisatojp/PointMatcher.git --recursive
cd PointMatcher
python PointMatcher/__main__.py
```

## Annotation format

You can export annotated data to one json file in the following format.

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

[MIT license](https://github.com/daisatojp/PointMatcher/blob/master/LICENSE)

## Acknowledgment

* [labelimg](https://github.com/tzutalin/labelImg) as a reference
* [Chateau de Sceaux Image Dataset](https://github.com/openMVG/ImageDataset_SceauxCastle) to test software
