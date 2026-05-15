import { useState } from 'react';
import { searchBooks, errorMessage } from '../api.js';

export default function Search() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null); // null = no search yet
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  async function runSearch(e) {
    e.preventDefault();
    const q = query.trim();
    if (!q) {
      setError('Enter a keyword to search');
      return;
    }
    try {
      setLoading(true);
      setError('');
      setResults(await searchBooks(q));
    } catch (err) {
      setError(errorMessage(err));
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  const filtered = (results || []).filter((b) =>
    !categoryFilter || b.category === categoryFilter,
  );
  const categories = Array.from(
    new Set((results || []).map((b) => b.category)),
  ).sort();

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Search</h1>
          <div className="page-subtitle">
            Find books by title, author or category
          </div>
        </div>
      </div>

      <form className="toolbar" onSubmit={runSearch}>
        <input
          className="input"
          placeholder="e.g. clean, kahneman, programming…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? 'Searching…' : 'Search'}
        </button>
        {results && results.length > 0 && (
          <select
            className="input"
            style={{ maxWidth: 220 }}
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
          >
            <option value="">All categories</option>
            {categories.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        )}
      </form>

      {error && <div className="alert">{error}</div>}

      {results === null ? (
        <div className="card empty">
          <div className="empty-title">Start by entering a keyword</div>
          <div>
            Search runs across the book title, author, and category fields.
          </div>
        </div>
      ) : filtered.length === 0 ? (
        <div className="card empty">
          <div className="empty-title">No matching books</div>
          <div>Try a different keyword.</div>
        </div>
      ) : (
        <>
          <div className="search-result-meta">
            {filtered.length} result{filtered.length === 1 ? '' : 's'} for
            “{query}”{categoryFilter && ` in ${categoryFilter}`}
          </div>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Title</th>
                  <th>Author</th>
                  <th>Category</th>
                  <th>ISBN</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((b) => (
                  <tr key={b.book_id}>
                    <td>{b.book_id}</td>
                    <td>{b.title}</td>
                    <td>{b.author}</td>
                    <td>{b.category}</td>
                    <td>{b.isbn}</td>
                    <td>
                      <span
                        className={
                          'pill ' +
                          (b.availability_status === 'Available'
                            ? 'pill-available'
                            : 'pill-borrowed')
                        }
                      >
                        {b.availability_status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </>
  );
}
