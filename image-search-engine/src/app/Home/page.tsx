"use client"
import { useState } from 'react'

interface SearchResult {
  title: string;
  description: string;
  image_url: string;
}

export default function Home() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])

  const handleSearch = async () => {
    const res = await fetch(`https://web-production-6cb6.up.railway.app/search?query=${encodeURIComponent(query)}`)
    const data = await res.json()
    console.log(data)  // Log the response to confirm the structure
    setResults(data.results)
  }

  return (
    <div>
      <h1>Frog Image Search</h1>
      <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search frogs..." />
      <button onClick={handleSearch}>Search</button>

      <div>
        {results.map((result, i) => (
          <div key={i}>
            <h3>{result.title}</h3>
            <p>{result.description}</p>
            <img src={result.image_url} alt={result.title} width="300" />
          </div>
        ))}
      </div>
    </div>
  )
}
