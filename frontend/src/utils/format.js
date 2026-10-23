// ---------- Status (satu sumber label & warna; dipakai StatusBadge & TrackingTimeline) ----------
export const STATUS = {
  PENDING: { label: 'Menunggu', icon: 'fa-clipboard-check', cls: 'bg-yellow-100 text-yellow-900', dot: 'bg-yellow-500' },
  REJECTED: { label: 'Ditolak', icon: 'fa-ban', cls: 'bg-red-100 text-red-800', dot: 'bg-red-600' },
  ASSIGNED: { label: 'Ditugaskan', icon: 'fa-user-check', cls: 'bg-blue-100 text-blue-800', dot: 'bg-blue-600' },
  PICKED_UP: { label: 'Dijemput', icon: 'fa-hand-holding', cls: 'bg-indigo-100 text-indigo-800', dot: 'bg-indigo-600' },
  IN_TRANSIT: { label: 'Dalam Perjalanan', icon: 'fa-truck-fast', cls: 'bg-purple-100 text-purple-800', dot: 'bg-purple-600' },
  DELIVERED: { label: 'Terkirim', icon: 'fa-box-open', cls: 'bg-green-100 text-green-800', dot: 'bg-green-500' },
  COMPLETED: { label: 'Selesai', icon: 'fa-flag-checkered', cls: 'bg-green-700 text-white', dot: 'bg-green-700' },
}
export const STATUS_LIST = Object.keys(STATUS)
export const statusLabel = (s) => STATUS[s]?.label ?? s

// ---------- Tanggal: "DD MMM YYYY, HH:mm" (waktu server UTC -> waktu lokal saat tampil) ----------
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
const pad = (n) => String(n).padStart(2, '0')

export function formatDate(iso) {
  const d = new Date(iso)
  if (!iso || isNaN(d)) return '-'
  return `${pad(d.getDate())} ${MONTHS[d.getMonth()]} ${d.getFullYear()}`
}

export function formatDateTime(iso) {
  const d = new Date(iso)
  if (!iso || isNaN(d)) return '-'
  return `${formatDate(iso)}, ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

/** "2026-09-25" (tanggal murni dari API) -> "25 Sep". Tidak lewat new Date(string) agar tidak bergeser zona. */
export function formatDayMonth(dateStr) {
  const [, m, d] = dateStr.split('-').map(Number)
  return `${d} ${MONTHS[m - 1]}`
}
export function formatMonthYear(dateStr) {
  const [y, m] = dateStr.split('-').map(Number)
  return `${MONTHS[m - 1]} ${String(y).slice(2)}`
}

export function timeAgo(iso) {
  const min = Math.floor((Date.now() - new Date(iso).getTime()) / 60000)
  if (isNaN(min) || min < 1) return 'Baru saja'
  if (min < 60) return `${min} menit lalu`
  if (min < 1440) return `${Math.floor(min / 60)} jam lalu`
  return `${Math.floor(min / 1440)} hari lalu`
}

// ---------- Lain-lain ----------
export const formatWeight = (n) => `${Number(n).toLocaleString('id-ID', { maximumFractionDigits: 2 })} kg`
export const firstName = (name = '') => name.trim().split(/\s+/)[0] || ''
export const initials = (name = '') =>
  name.trim().split(/\s+/).slice(0, 2).map((w) => w[0]?.toUpperCase()).join('') || '?'

export const ROLE_LABEL = { CUSTOMER: 'Customer', COURIER: 'Kurir', ADMIN: 'Admin' }

/** proof_image_url dari backend berupa path relatif (/static/...). Tambahkan origin API. */
export function assetUrl(path) {
  if (!path) return ''
  if (/^https?:\/\//.test(path)) return path
  try {
    const base = import.meta.env.VITE_API_BASE_URL || '/api/v1'
    return new URL(base, window.location.origin).origin + path
  } catch {
    return path
  }
}
