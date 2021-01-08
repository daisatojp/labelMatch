# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['PointMatcher/__main__.py'],
             pathex=['PointMatcher'],
             binaries=[],
             datas=[
			     ('PointMatcher/package_data/icons/*', 'PointMatcher/package_data/icons'),
			     ('PointMatcher/package_data/strings/*', 'PointMatcher/package_data/strings')
			 ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='PointMatcher',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )