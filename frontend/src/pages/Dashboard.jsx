import { useEffect, useState } from 'react';
import { dashboardStats, listTransactions, errorMessage } from '../api.js';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [recent, setRecent] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setLoading(true);
        const [s, t] = await Promise.all([dashboardStats(), listTransactions()]);
        if (cancelled) return;
        setStats(s);
        setRecent(t.slice(0, 5));
      } catch (e) {
        if (!cancelled) setError(errorMessage(e));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Dashboard</h1>
          <div className="page-subtitle">Library at a glance</div>
        </div>
      </div>

      {error && <div className="alert">{error}</div>}
      {loading ? (
        <div className="loading">Loading…</div>
      ) : (
        <>
          <div className="stat-grid">
            <StatCard label="Total Books" value={stats?.total_books ?? 0} accent="blue" />
            <StatCard label="Available" value={stats?.available_books ?? 0} accent="green" />
            <StatCard label="Borrowed" value={stats?.borrowed_books ?? 0} accent="amber" />
            <StatCard label="Borrowers" value={stats?.total_borrowers ?? 0} accent="purple" />
            <StatCard label="Open Loans" value={stats?.active_transactions ?? 0} accent="amber" />
          </div>

          <div className="card">
            <h2>Recent transactions</h2>
            {recent.length === 0 ? (
              <div className="empty">
                <div className="empty-title">No transactions yet</div>
                <div>Use the Transactions tab to record a borrow.</div>
              </div>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Book</th>
                      <th>Borrower</th>
                      <th>Borrowed</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recent.map((t) => (
                      <tr key={t.transaction_id}>
                        <td>{t.transaction_id}</td>
                        <td>{t.book_title}</td>
                        <td>{t.borrower_name}</td>
                        <td>{new Date(t.borrow_date).toLocaleString()}</td>
                        <td>
                          {t.return_date ? (
                            <span className="pill pill-returned">Returned</span>
                          ) : (
                            <span className="pill pill-borrowed">Open</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </>
  );
}

function StatCard({ label, value, accent }) {
  return (
    <div className={`stat-card stat-accent-${accent}`}>
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
    </div>
  );
}
