"use client";

import { useState, type FormEvent } from "react";

type Result = {
  site: string;
  title: string;
  path: string;
  snippet: string;
  verified: boolean;
  score: number;
};

type SearchResponse = {
  query: string;
  results: Result[];
};

export default function Home() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Result[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setSearched(true);

    try {
      const res = await fetch(
        `http://localhost:3001/search?q=${encodeURIComponent(query)}`
      );
      const data: SearchResponse = await res.json();
      setResults(data.results);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="max-w-2xl mx-auto p-6">
      <form onSubmit={handleSubmit} className="mb-8">
        <h1 className="text-3xl font-bold mb-4 text-center">Ichin Search</h1>
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search registered sites and pages..."
            className="flex-1 border border-stone-300 rounded-lg px-4 py-2 text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg text-lg font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "..." : "Search"}
          </button>
        </div>
      </form>

      {loading && <p className="text-stone-500 text-center">Searching...</p>}

      {searched && !loading && results && results.length === 0 && (
        <p className="text-stone-500 text-center">
          No results found for &quot;{query}&quot;.
        </p>
      )}

      {results && results.length > 0 && (
        <div>
          <p className="text-sm text-stone-500 mb-4">
            {results.length} result{results.length !== 1 ? "s" : ""} for
            &quot;{query}&quot;
          </p>
          <ul className="space-y-4">
            {results.map((r, i) => (
              <li key={i} className="bg-white border border-stone-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm text-stone-500">{r.site}</span>
                  {r.verified && (
                    <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">
                      verified
                    </span>
                  )}
                  <span className="text-xs text-stone-400 ml-auto">
                    score: {r.score}
                  </span>
                </div>
                <h2 className="text-lg font-semibold text-blue-700">
                  {r.title}
                </h2>
                <p className="text-sm text-stone-500 mb-1">{r.path}</p>
                <p className="text-stone-700">{r.snippet}</p>
              </p>
            ))}
          </ul>
        </div>
      )}

      {!searched && (
        <div className="text-center text-stone-400 mt-16">
          <p>Search across registered Ichin sites and pages.</p>
          <p className="text-sm mt-2">
            Powered by registry-based indexing and simple keyword ranking.
          </p>
        </div>
      )}
    </main>
  );
}
