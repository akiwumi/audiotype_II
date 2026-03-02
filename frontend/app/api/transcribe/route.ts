import { NextRequest, NextResponse } from 'next/server'

// Proxies file uploads to the FastAPI backend.
// This avoids CORS issues — the browser talks to Next.js,
// and Next.js forwards the request to Railway server-side.
export async function POST(req: NextRequest) {
  const apiBase = process.env.API_BASE ?? 'http://localhost:8000'

  let formData: FormData
  try {
    formData = await req.formData()
  } catch {
    return NextResponse.json({ detail: 'Invalid form data' }, { status: 400 })
  }

  try {
    const upstream = await fetch(`${apiBase}/transcribe`, {
      method: 'POST',
      body: formData,
    })

    const data = await upstream.json()
    return NextResponse.json(data, { status: upstream.status })
  } catch {
    return NextResponse.json(
      { detail: 'Could not reach the transcription server. Is the backend running?' },
      { status: 502 }
    )
  }
}
