# -*- mode: python -*-

block_cipher = None

a = Analysis(['pyportify/server.py'],
             pathex=['/Users/atin/src/pyportify'],
             binaries=None,
             datas=[
                ('pyportify/static', 'pyportify'), 
             ],
             hiddenimports=['aiohttp'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='pyportify',
          debug=False,
          strip=False,
          upx=True,
          console=True)

a1 = Analysis(['pyportify/copy_user_playlist.py'],
             pathex=['/Users/atin/src/pyportify'],
             binaries=None,
             datas=None,
             hiddenimports=['pyportify', 'pyportify.server'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz1 = PYZ(a1.pure, a1.zipped_data, cipher=block_cipher)
exe1 = EXE(pyz,
          a1.scripts,
          a1.binaries,
          a1.zipfiles,
          a1.datas,
          name='pyportify-copy-user-playlist',
          debug=False,
          strip=False,
          upx=True,
          console=True)
