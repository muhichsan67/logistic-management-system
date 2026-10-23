// Validasi dasar di sisi klien (mengikuti BACKEND_RULES 6). Backend tetap penentu akhir.
const blank = (v) => !String(v ?? '').trim()

export const rule = {
  required: (label) => (v) => (blank(v) ? `${label} wajib diisi` : ''),
  email: (v) => (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(v).trim()) ? '' : 'Format email tidak valid'),
  phone: (v) => (/^(\d{8,20}|\+\d{7,19})$/.test(String(v).trim()) ? '' : 'Telepon harus berupa angka, 8-20 karakter'),
  name: (label) => (v) => {
    const n = String(v).trim().length
    return n < 2 || n > 100 ? `${label} harus 2-100 karakter` : ''
  },
  password: (v) => {
    if (String(v).length < 8) return 'Password minimal 8 karakter'
    if (!/[A-Za-z]/.test(v) || !/\d/.test(v)) return 'Password harus memuat huruf dan angka'
    return ''
  },
  weight: (v) => {
    const n = Number(String(v).replace(',', '.'))
    if (blank(v) || Number.isNaN(n) || n <= 0) return 'Berat harus lebih dari 0'
    if (n > 9999.99) return 'Berat maksimal 9999,99 kg'
    if (!/^\d+([.,]\d{1,2})?$/.test(String(v).trim())) return 'Berat maksimal 2 angka desimal'
    return ''
  },
  positiveInt: (label) => (v) => (/^[1-9]\d{0,5}$/.test(String(v).trim()) ? '' : `${label} harus bilangan bulat positif`),
  same: (other, message) => (v) => (v === other() ? '' : message),
}

/** rules = { field: [fn, fn] } -> { field: 'pesan' } (hanya field yang salah). */
export function runRules(values, rules) {
  const errors = {}
  for (const [field, fns] of Object.entries(rules)) {
    for (const fn of fns) {
      const msg = fn(values[field])
      if (msg) {
        errors[field] = msg
        break
      }
    }
  }
  return errors
}

/** Salin error per-field dari respons 422 backend ke objek errors form. */
export function applyServerErrors(errors, err) {
  for (const e of err?.fieldErrors || []) errors[e.field] = e.message
}
