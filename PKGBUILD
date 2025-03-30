# Maintainer: Your Name <your.email@example.com>
pkgname=rclonetray-kde
pkgver=1.0.0
pkgrel=1
pkgdesc="Native KDE system tray application for Rclone"
arch=('x86_64')
url="https://github.com/yourusername/rclonetray-kde"
license=('GPL3')
depends=('python' 'python-pyside6' 'rclone' 'fuse3' 'python-dbus')
makedepends=('python-pip' 'python-build' 'python-installer' 'python-wheel')
source=("$pkgname-$pkgver.tar.gz")
sha256sums=('SKIP')

package() {
    cd "$srcdir/$pkgname-$pkgver"
    
    # Install Python package
    python -m installer --destdir="$pkgdir" dist/*.whl

    # Install desktop file
    install -Dm644 "desktop/org.rclonetray.desktop" "$pkgdir/usr/share/applications/org.rclonetray.desktop"
    
    # Install icons
    install -Dm644 "src/ui/icons/icon.png" "$pkgdir/usr/share/icons/hicolor/128x128/apps/rclonetray.png"
    
    # Install systemd user service
    install -Dm644 "systemd/rclonetray.service" "$pkgdir/usr/lib/systemd/user/rclonetray.service"
}
