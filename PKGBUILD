pkgname=radeon-tray
_up_pkgname=Radeon-tray
pkgver=1.2
pkgrel=0
pkgdesc="A system tray icon for controlling radeon cards' power states"
arch=('any')
url="https://github.com/StuntsPT/Radeon-tray/"
license=('GPL3')
depends=('python' 'python-pyqt4' 'python-pyzmq>=13.0' 'python-setuptools')
source=("git://github.com/coderobe/Radeon-tray.git")
md5sums=('SKIP')

package() {
  cd ${srcdir}/${_up_pkgname}
  yes | python3 setup.py install --root=${pkgdir}
  
  mkdir -p ${pkgdir}/usr/lib/systemd/system
  cp radeontray/systemd/radeonpm.service ${pkgdir}/usr/lib/systemd/system/

  mkdir -p ${pkgdir}/usr/share/applications
  cp radeontray/conf/radeontrayclient.desktop ${pkgdir}/usr/share/applications/

  mkdir -p  ${pkgdir}/usr/share/Radeon-tray-icon
  cp  radeontray/assets/radeon-tray.svg  ${pkgdir}/usr/share/Radeon-tray-icon
}
