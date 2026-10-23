const KEY = 'alur_notif_asked'

/**
 * Minta izin notifikasi SETELAH aksi pertama pengguna (bukan saat app dibuka), hanya sekali.
 * Catatan: pengiriman Web Push butuh endpoint subscribe di backend (belum ada).
 */
export async function askNotificationPermissionOnce() {
  if (!('Notification' in window) || localStorage.getItem(KEY)) return
  localStorage.setItem(KEY, '1')
  if (Notification.permission !== 'default') return
  try {
    await Notification.requestPermission()
  } catch {
    /* diabaikan */
  }
}
