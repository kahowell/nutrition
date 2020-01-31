from pyodideapp.build import *
from extract import FoodsSource

import shutil


app = App(id='net.kahowell.nutrition', name='Nutrition', sources=[
    SourceDirectory('src'),
    Archive(Url('https://github.com/hfg-gmuend/openmoji/releases/download/12.1.0/openmoji-svg-color.zip', sha256sum='205638da29deb41cdad7bf3244cb3ffabe4c0e9a41ae5a4f63b40f9a02ea13e4'), files=[
        '1F957.svg',  # green salad
        '1F34A.svg',  # tangerine
        '1F336.svg',  # hot pepper
        '1F373.svg',  # cooking
    ]),
    Url('https://cdn.jsdelivr.net/npm/vue@2.6.11/dist/vue.min.js', sha256sum='9e0156dd49c03744e79bbea60eebbbb94b5811c1b71b91f5fb38a8270dedfbaf'),
    Url('https://unpkg.com/vue-onsenui@2.6.2/dist/vue-onsenui.min.js', sha256sum='ca09a70c38496b73bc237ccd30d05dc0d7732cc96326eac0708c4e64101f29f7'),
    Url('https://unpkg.com/onsenui@2.10.10/js/onsenui.min.js', sha256sum='515743ef8887d2b5af8ca40f870805cf32969e339c7feb89f2ffff10c0203869'),
    Url('https://unpkg.com/onsenui@2.10.10/css/onsen-css-components.min.css', sha256sum='c13b94ebc4fdbc5343470485052c0143cea46345b790a3045d5eaa436484f5a9'),
    Url('https://unpkg.com/onsenui@2.10.10/css/onsenui.min.css', sha256sum='90af85cc638f7f5d565930c0c63fb913a8e9f5dee94dc37cbd800484f19fd17d'),
    Url('https://unpkg.com/onsenui@2.10.10/css/ionicons/css/ionicons.min.css', sha256sum='abb25b72286b5daaebd9758183f196cfc7ded15748acb610bd4ba266e95fd1e1', filename='ionicons/css/ionicons.min.css'),
    Url('https://unpkg.com/onsenui@2.10.10/css/material-design-iconic-font/css/material-design-iconic-font.min.css', sha256sum='dec3e9f0190a504ed0c8f4a5e957c107206ba106cac4a1bbb6cbac6369a16d56', filename='material-design-iconic-font/css/material-design-iconic-font.min.css'),
    Url('https://unpkg.com/onsenui@2.10.10/css/material-design-iconic-font/fonts/Material-Design-Iconic-Font.woff', sha256sum='7c74c136895350e927bf69fe9fcb9f33fe9fae6340709d6ec4f8cb838a9470a3', filename='material-design-iconic-font/fonts/Material-Design-Iconic-Font.woff'),
    Url('https://unpkg.com/onsenui@2.10.10/css/material-design-iconic-font/fonts/Material-Design-Iconic-Font.woff2', sha256sum='e8eea96e29a7c0a72612ab85ca3229979666467a28349642c2176e7189a1a39c', filename='material-design-iconic-font/fonts/Material-Design-Iconic-Font.woff2'),
    Url('https://unpkg.com/onsenui@2.10.10/css/material-design-iconic-font/fonts/Material-Design-Iconic-Font.ttf', sha256sum='18a45be2ecb66ce217c3bbccf219f8bdc05dc76d61a6e63673186efd1c7cda1a', filename='material-design-iconic-font/fonts/Material-Design-Iconic-Font.ttf'),
    Url('https://unpkg.com/onsenui@2.10.10/css/font_awesome/css/all.min.css', sha256sum='eeb17a45a48aca1d7adbcf04de155dcd0b47cb36ad036310446bb471fea9aaa3', filename='font_awesome/css/all.min.css'),
    Url('https://unpkg.com/onsenui@2.10.10/css/font_awesome/css/v4-shims.min.css', sha256sum='48e30fbbcda9a416802bb17efa3fc5ef4aed8284592bc338628263e2ecc5f80f', filename='font_awesome/css/v4-shims.min.css'),
    Url('https://unpkg.com/onsenui@2.10.10/css/font_awesome/webfonts/fa-brands-400.woff2', sha256sum='dc64d7192f84497cacad5c10aef682562c24aa6124270f85fe247e223607f3ed', filename='font_awesome/webfonts/fa-brands-400.woff2'),
    Url('https://unpkg.com/onsenui@2.10.10/css/font_awesome/webfonts/fa-brands-400.woff', sha256sum='17ce8b9d612897d1fefd5cd2096dbd83b82d05dd5d1f60421aca15c4ce2445ac', filename='font_awesome/webfonts/fa-brands-400.woff'),
    Url('https://unpkg.com/onsenui@2.10.10/css/font_awesome/webfonts/fa-solid-900.woff2', sha256sum='f18c486a80175cf02fee0e05c2b4acd86c04cdbaecec61c1ef91f920509b5efe', filename='font_awesome/webfonts/fa-solid-900.woff2'),
    Url('https://unpkg.com/onsenui@2.10.10/css/font_awesome/webfonts/fa-solid-900.woff', sha256sum='20464aebbff54cc17776497ce4112c3374a54b38f7ba5f58eec12174149d6742', filename='font_awesome/webfonts/fa-solid-900.woff'),
    Url('https://unpkg.com/onsenui@2.10.10/css/font_awesome/webfonts/fa-solid-900.ttf', sha256sum='7a58f741ff539af94798ff561c918e5841d7e6164e90cbe57befdec4a16f6a4e', filename='font_awesome/webfonts/fa-solid-900.ttf'),
    Url('https://cdn.jsdelivr.net/npm/pouchdb@7.1.1/dist/pouchdb.min.js', sha256sum='249bd5d3452a205b51ca5f972b5beeb9c79781efbe9c6260412e2f31c81f718a'),
    Url('https://cdn.jsdelivr.net/npm/pouchdb@7.1.1/dist/pouchdb.find.min.js', sha256sum='50cf2fb626976fa4594670e40e4adc92698158f6c46965a2e8748f38e7e7ad34'),
    FoodsSource(),
])


if __name__ == '__main__':
    app.main()
