/**
 * Perkecil foto kamera (sisi terpanjang <= 1600px, JPEG) sebelum diunggah.
 * Foto HP sering > 5 MB (batas backend) dan bisa berformat HEIC; hasil di sini selalu JPEG kecil.
 */
export async function compressImage(file, maxSide = 1600, quality = 0.8) {
  let bitmap
  try {
    bitmap = await createImageBitmap(file)
  } catch {
    throw new Error('Foto tidak dapat dibaca. Coba ambil ulang.')
  }
  const scale = Math.min(1, maxSide / Math.max(bitmap.width, bitmap.height))
  const canvas = document.createElement('canvas')
  canvas.width = Math.round(bitmap.width * scale)
  canvas.height = Math.round(bitmap.height * scale)
  canvas.getContext('2d').drawImage(bitmap, 0, 0, canvas.width, canvas.height)
  bitmap.close?.()
  const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', quality))
  if (!blob) throw new Error('Gagal memproses foto. Coba ambil ulang.')
  return new File([blob], 'bukti.jpg', { type: 'image/jpeg' })
}
